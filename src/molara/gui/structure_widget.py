"""Contains the StructureWidget class, which is a subclass of QOpenGLWidget."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Literal

import numpy as np
from OpenGL.GL import GL_DEPTH_TEST, GL_MULTISAMPLE, glClearColor, glEnable
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from molara.rendering.camera import Camera
from molara.rendering.rendering import Renderer
from molara.structure.crystal import Crystal
from molara.tools.raycasting import select_sphere

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QWidget

    from molara.structure.molecule import Molecule
    from molara.structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"

MEASUREMENT, BUILDER, ORBITALS = 0, 1, 2


class StructureWidget(QOpenGLWidget):
    """Creates a StructureWidget object, which is a subclass of QOpenGLWidget."""

    def __init__(self, parent: QWidget) -> None:
        """Create a StructureWidget object, which is a subclass of QOpenGLWidget.

        :param parent: parent widget (main window's central widget)
        """
        self.central_widget = parent
        self.main_window = self.central_widget.parent()  # type: ignore[method-assign, assignment]
        QOpenGLWidget.__init__(self, parent)

        self.structures: list[Structure | Molecule | Crystal] = []
        self.vertex_attribute_objects = [-1]
        self.draw_axes = False
        self.box = False
        self.rotate = False
        self.translate = False
        self.click_position: np.ndarray | None = None
        self.rotation_angle_x = 0.0
        self.rotation_angle_y = 0.0
        self.position = np.zeros(2)
        self.old_position = np.zeros(2)
        self.contour = False
        self.camera = Camera(self.width(), self.height())
        self.renderer = Renderer(self)
        self.cursor_in_widget = False
        self.measurement_selected_spheres: list = [-1] * 4
        self.measurement_drawn_spheres: list = [-1] * 4
        self.builder_selected_spheres: list = [-1] * 3
        self.builder_drawn_spheres: list = [-1] * 3

        self.old_sphere_colors: list = [np.ndarray] * 4
        self.highlighted_atoms_colors: list = [
            np.array([1, 0, 0], dtype=np.float32),
            np.array([0, 1, 0], dtype=np.float32),
            np.array([0, 0, 1], dtype=np.float32),
            np.array([1, 1, 0], dtype=np.float32),
        ]
        self.show_atom_indices = False
        self.atom_indices_arrays: tuple[np.ndarray, np.ndarray] = (np.zeros(1), np.zeros(1))
        self.number_scale = 1.0
        self.highlighted_atoms: list = []

    @property
    def bonds(self) -> bool:
        """Specifies whether bonds should be drawn (returns False if no bonds present whatsoever)."""
        if self.structures:
            result = self.structures[0].draw_bonds and self.structures[0].has_bonds
            self.main_window.structure_customizer_dialog.bonds = result
            return result
        return False

    @property
    def draw_bonds(self) -> bool:
        """Specifies whether bonds should be drawn."""
        if len(self.structures) != 1:
            return False
        return self.structures[0].draw_bonds

    @property
    def orthographic_projection(self) -> bool:
        """Specifies whether the projection is orthographic or not."""
        return self.camera.orthographic_projection

    def reset_view(self) -> None:
        """Reset the view of the structure to the initial view."""
        self.center_structure()
        dy, dz = None, None
        if not len(self.structures) or not self.structures[0]:
            return
        if not self.structures[0].atoms:
            return
        if len(self.structures[0].atoms) > 1:
            x, y, z = np.array([atom.position for atom in self.structures[0].atoms]).T
            dy = y.max() - y.min()
            dz = z.max() - z.min()
        self.camera.reset(self.width(), self.height(), dy, dz)
        self.update()

    def set_view_to_axis(self, axis: Literal["x", "y", "z"]) -> None:
        """Set view angle parallel to a specified axis.

        :param axis: axis to which the view shall be set
        """
        self.camera.center_coordinates()
        self.camera.set_rotation(axis)
        self.update()

    def delete_structure(self) -> None:
        """Delete structures and reset vertex attributes."""
        self.vertex_attribute_objects = [-1]
        self.update()

    def set_structure(self, structs: list[Structure | Crystal | Molecule], reset_view: bool = True) -> None:
        """Set the structures to be drawn.

        :param structs: list of Structure object that shall be drawn
        :param reset_view: Specifies whether the view shall be reset to the initial view
        """
        self.structures = structs
        if reset_view:
            self.reset_view()
        else:
            self.update_molecule_spheres_cylinders()
            self.update()

        self.main_window.structure_customizer_dialog.set_bonds(self.bonds)
        self.main_window.structure_customizer_dialog.apply_changes()
        self.toggle_unit_cell_boundaries(update_box=True)

        self.reset_measurement()

    def center_structure(self) -> None:
        """Centers the structure in the widget."""
        if not self.structures:
            return
        self.structures[0].center_coordinates()
        self.camera.center_coordinates()
        self.update_molecule_spheres_cylinders()
        self.update()

    def export_camera_settings(self, filename: str) -> None:
        """Export camera settings to .npz file.

        :param filename: name of the file to which the camera settings shall be saved
        """
        self.camera.export_settings(filename)

    def import_camera_settings(self, filename: str) -> None:
        """Import camera settings from .npz file.

        :param filename: name of the file from which the camera settings shall be loaded
        """
        if not filename.endswith(".json"):
            return
        with Path(filename).open() as file:
            data = json.load(file)
        self.camera.import_settings(filename)
        self.resize(data["width"], data["height"])
        self.resizeGL(data["width"], data["height"])
        self.main_window.resize(data["width"], data["height"])
        self.update()

    def initializeGL(self) -> None:  # noqa: N802
        """Initialize the widget."""
        glClearColor(1, 1, 1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        self.renderer.set_shaders()
        self.renderer.device_pixel_ratio = self.devicePixelRatio()
        self.renderer.create_framebuffers(self.width(), self.height())
        self.renderer.create_screen_vao()

    def resizeGL(self, width: int, height: int) -> None:  # noqa: N802
        """Resizes the widget.

        :param width: widget width (in pixels)
        :param height: widget height (in pixels)
        """
        self.renderer.create_framebuffers(width, height)
        self.camera.width, self.camera.height = width, height
        self.camera.calculate_projection_matrix()
        self.update()

    def paintGL(self) -> None:  # noqa: N802
        """Draws the scene."""
        if not self.isValid():
            return
        self.renderer.default_framebuffer = self.defaultFramebufferObject()
        self.makeCurrent()
        self.renderer.draw_scene()

    def update_molecule_spheres_cylinders(self) -> None:
        """Update the spheres and cylinders (atoms and bonds of a molecule)."""
        self.makeCurrent()
        for name in ["Atoms", "Bonds"]:
            if name in self.renderer.objects3d:
                self.renderer.remove_object(name)
        if self.structures[0].drawer.spheres is not None:
            self.renderer.objects3d["Atoms"] = self.structures[0].drawer.spheres
            self.renderer.objects3d["Atoms"].generate_buffers()
        if self.structures[0].drawer.cylinders is not None and self.structures[0].draw_bonds:
            self.renderer.objects3d["Bonds"] = self.structures[0].drawer.cylinders
            self.renderer.objects3d["Bonds"].generate_buffers()

    def wheelEvent(self, event: QEvent) -> None:  # noqa: N802
        """Zooms in and out of the structure."""
        num_degrees = event.angleDelta().y() / 8  # type: ignore[attr-defined]
        num_steps = num_degrees / 100  # Empirical value to control zoom speed
        self.camera.set_distance_from_target(num_steps)
        self.camera.update()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Start the rotation or translation of the structure.

        :param event: mouse event (such as left click, right click...)
        """
        if not 0 < event.position().x() < self.width() or not 0 < event.position().y() < self.height():
            return

        iso_lines_tab = 1

        if event.button() == Qt.MouseButton.LeftButton:
            # first test if Shift key is pressed (for selecting atoms)
            if bool(QGuiApplication.keyboardModifiers() & Qt.ShiftModifier):  # type: ignore[attr-defined]
                if self.main_window.measurement_dialog.isVisible():
                    self.update_selected_atoms(MEASUREMENT, event)
                if self.main_window.builder_dialog.isVisible():
                    self.update_selected_atoms(BUILDER, event)
                if (
                    self.main_window.mo_dialog.isVisible()
                    and self.main_window.mo_dialog.ui.isoTab.currentIndex() == iso_lines_tab
                ):
                    self.update_selected_atoms(ORBITALS, event)
                return

            self.rotate = True
            if self.translate is True:
                self.stop_translate(event)
            self.set_normalized_position(event)
            self.click_position = np.copy(self.position)

        if event.button() == Qt.MouseButton.RightButton:
            self.translate = True
            if self.rotate is True:
                self.stop_rotation(event)
            self.set_normalized_position(event)
            self.click_position = np.copy(self.position)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Rotates or translates the structure.

        :param event: mouse event (such as left click, right click...)
        """
        if self.rotate and self.click_position is not None:
            self.set_normalized_position(event)
            self.camera.set_rotation_quaternion(self.click_position, self.position)
        if self.translate and self.click_position is not None:
            self.set_normalized_position(event)
            self.camera.set_translation_vector(self.click_position, self.position)
        self.camera.update()
        self.update()

    def set_normalized_position(self, event: QMouseEvent) -> None:
        """Set the normalized position of the mouse cursor.

        :param event: mouse event (such as left click, right click...)
        """
        if self.width() >= self.height():
            self.position[0] = (event.position().x() * 2 - self.width()) / self.width()
            self.position[1] = -(event.position().y() * 2 - self.height()) / self.width()
        else:
            self.position[0] = (event.position().x() * 2 - self.width()) / self.height()
            self.position[1] = -(event.position().y() * 2 - self.height()) / self.height()
        self.position = np.array(self.position, dtype=np.float32)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Stop the rotation or translation of the structure.

        :param event: mouse event (such as left click, right click...)
        """
        if event.button() == Qt.MouseButton.LeftButton and self.rotate:
            self.stop_rotation(event)
        if event.button() == Qt.MouseButton.RightButton and self.translate:
            self.stop_translate(event)

    def stop_translate(self, event: QMouseEvent) -> None:
        """Stop the translation of the structure.

        :param event: mouse event (such as left click, right click...)
        :return:
        """
        self.translate = False
        self.set_normalized_position(event)
        self.camera.update(save=True)
        self.click_position = None

    def stop_rotation(self, event: QMouseEvent) -> None:
        """Stop the rotation of the structure.

        :param event: mouse event (such as left click, right click...)
        :return:
        """
        self.rotate = False
        self.set_normalized_position(event)
        self.camera.update(save=True)
        self.click_position = None

    def toggle_axes(self) -> None:
        """Draws the cartesian axes."""
        length = 2.0
        radius = 0.02
        self.makeCurrent()
        self.draw_axes = not self.draw_axes
        if not self.draw_axes:
            self.renderer.remove_object("Axes_cylinders")
            self.renderer.remove_object("Axes_spheres")
            self.update()
            self.main_window.update_action_texts()
            return

        positions = np.array(
            [[length / 2, 0, 0], [0, length / 2, 0], [0, 0, length / 2]],
            dtype=np.float32,
        )
        directions = np.eye(3, dtype=np.float32)
        colors = np.eye(3, dtype=np.float32)
        dimensions = np.array([[radius, length, radius]] * 3, dtype=np.float32)

        self.renderer.draw_cylinders(
            "Axes_cylinders",
            positions,
            directions,
            dimensions,
            colors,
            25,
        )
        positions = np.array(
            [[length, 0, 0], [0, length, 0], [0, 0, length], [0, 0, 0]],
            dtype=np.float32,
        )
        colors = np.array(
            [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]],
            dtype=np.float32,
        )
        radii = np.array([radius] * 4, dtype=np.float32)
        self.renderer.draw_spheres("Axes_spheres", positions, radii, colors, 25)
        self.update()

        self.main_window.update_action_texts()

    def toggle_projection(self) -> None:
        """Toggles between orthographic and perspective projection."""
        self.camera.toggle_projection()
        self.update()
        self.main_window.update_action_texts()

    def toggle_unit_cell_boundaries(self, update_box: bool = False) -> None:
        """Draws the unit cell boundaries.

        :param update_box: specifies whether box shall be updated. If False, a drawn box will be hidden.
        """
        if len(self.structures) != 1:
            return

        self.makeCurrent()

        box_was_drawn = self.box

        if not box_was_drawn and update_box:
            # if no box is drawn and unit cell boundary shall not be toggled but just updated, nothing needs to be done!
            return

        if box_was_drawn:
            self.renderer.remove_object("Box_cylinder")
            # if a box was drawn and the unit cell boundary shall not be simply updated,
            # the box should be removed.
            if not update_box:
                self.box = False
                self.update()
                self.main_window.update_action_texts()
                return
            if not isinstance(self.structures[0], Crystal):
                self.box = False
                self.update()
                self.main_window.update_action_texts()
                return

        # the unit cell boundaries shall be drawn anew if:
        # 1.) a box was not drawn before and function is called as a "toggle", not an update
        # 2.) a box was drawn before, but shall be updated (crystal structure changed)
        assert isinstance(self.structures[0], Crystal)

        positions = self.structures[0].unitcell_boundaries_positions

        diagonal_length = np.linalg.norm(self.structures[0].basis_vectors)
        lowerlim_radius = 0.005
        radius = max(lowerlim_radius, diagonal_length / 350)  # just some arbitrary scaling that looks nice
        colors = np.array([0, 0, 0] * positions.shape[0], dtype=np.float32)
        radii = np.array([radius] * positions.shape[0], dtype=np.float32)
        self.renderer.draw_cylinders_from_to(
            "Box_cylinder",
            positions,
            radii,
            colors,
            25,
        )
        self.box = True
        self.update()

        self.main_window.update_action_texts()

    def identify_selected_sphere(self, xpos: int, ypos: int) -> int:
        """Return index of sphere that has been selected by clicking.

        :param xpos: x position of the mouse-click event
        :param ypos: y position of the mouse-click event
        """
        if len(self.structures) != 1:
            return -1

        click_position = np.array(
            [
                (xpos * 2 - self.width()) / self.width(),
                (ypos * 2 - self.height()) / self.height(),
            ],
            dtype=np.float32,
        )
        return select_sphere(
            click_position,
            self.camera.position,
            self.camera.view_matrix_inv,
            self.camera.projection_matrix_inv,
            self.camera.fov,
            self.height() / self.width(),
            self.structures[0].drawer.sphere_positions,
            self.structures[0].drawer.sphere_radii[:],  # type: ignore[call-overload]
        )

    def exec_select_sphere(self, sphere_id: int, selected_spheres_list: list, drawn_spheres_list: list) -> None:
        """Select a sphere, change its color, update the selected spheres list.

        :param sphere_id: id of the sphere that shall be selected
        :param selected_spheres_list: list of selected spheres
        :param drawn_spheres_list: list of the indices of the already drawn spheres
        """
        id_in_selection = selected_spheres_list.index(-1)
        selected_spheres_list[id_in_selection] = sphere_id
        drawn_spheres_list[id_in_selection] = self.draw_selected_atom(sphere_id, id_in_selection)

    def draw_selected_atom(self, atom_id: int, selected_id: int, subdivisions: int = 20) -> int:
        """Draw a mesh grid sphere at the location of the selected atom.

        :param atom_id: index of the atom that is selected
        :param selected_id: index of the selected atom in the list of selected atoms
        :param subdivisions: number of subdivisions of the sphere (i.e. the 3d resolution of the sphere mesh grid)
        """
        sphere_position = np.array([self.structures[0].atoms[atom_id].position], dtype=np.float32)
        sphere_color = np.array(self.highlighted_atoms_colors[selected_id], dtype=np.float32)
        radius = self.structures[0].drawer.sphere_radii[atom_id] + 0.05
        self.renderer.draw_spheres(
            f"Atom_{atom_id}",
            sphere_position,
            np.array([radius], dtype=np.float32),
            sphere_color,
            subdivisions,
            wire_frame=True,
        )
        return 0

    def exec_unselect_sphere(self, sphere_id: int, selected_spheres_list: list, drawn_spheres_list: list) -> None:
        """Unselect a sphere, change its color, update the selected spheres list.

        :param sphere_id: id of the sphere that shall be unselected
        :param selected_spheres_list: list of selected spheres
        :param drawn_spheres_list: list of the indices of the already drawn spheres
        """
        if sphere_id == -1:
            return

        id_in_selection = selected_spheres_list.index(sphere_id)
        selected_spheres_list[id_in_selection] = -1
        self.renderer.remove_object(f"Atom_{sphere_id}")
        drawn_spheres_list[id_in_selection] = -1

    def update_selected_atoms(self, purpose: int, event: QMouseEvent) -> None:
        """Update the selected atoms in the measurement or builder dialog.

        :param purpose: purpose of the selection (MEASUREMENT=0, BUILDER=1)
        :param event: mouse event (such as left click, right click...)
        :return:
        """
        if len(self.structures) != 1:
            return
        self.makeCurrent()
        selected_sphere_id = self.identify_selected_sphere(event.position().x(), event.position().y())

        if purpose == ORBITALS:
            selected_spheres_list = self.main_window.mo_dialog.isoline_selected_atoms
            drawn_spheres_list = self.main_window.mo_dialog.isoline_drawn_spheres
        else:
            selected_spheres_list = (
                self.measurement_selected_spheres if purpose == MEASUREMENT else self.builder_selected_spheres
            )
            drawn_spheres_list = (
                self.measurement_drawn_spheres if purpose == MEASUREMENT else self.builder_drawn_spheres
            )

        if selected_sphere_id != -1:
            if -1 in selected_spheres_list:
                if selected_sphere_id in selected_spheres_list:
                    self.exec_unselect_sphere(selected_sphere_id, selected_spheres_list, drawn_spheres_list)
                else:
                    self.exec_select_sphere(selected_sphere_id, selected_spheres_list, drawn_spheres_list)
            elif selected_sphere_id in selected_spheres_list:
                self.exec_unselect_sphere(selected_sphere_id, selected_spheres_list, drawn_spheres_list)
        elif bool(QGuiApplication.keyboardModifiers() & Qt.ControlModifier):  # type: ignore[attr-defined]
            for selected_sphere_i in selected_spheres_list:
                self.exec_unselect_sphere(selected_sphere_i, selected_spheres_list, drawn_spheres_list)

        self.update()

        self.main_window.measurement_dialog.display_metrics(
            self.structures[0],
            self.measurement_selected_spheres,
        ) if purpose == MEASUREMENT else None

    def reset_measurement(self) -> None:
        """Reset measurement arrays and measurement dialog."""
        if len(self.structures) != 1:
            return
        self.measurement_selected_spheres = [-1] * 4
        self.main_window.measurement_dialog.display_metrics(
            self.structures[0],
            self.measurement_selected_spheres,
        )

    def unselect_all_atoms(self) -> None:
        """Unselect all selected atoms."""
        if len(self.structures) != 1:
            return
        for i in self.measurement_selected_spheres:
            if i != -1:
                self.exec_unselect_sphere(i, self.measurement_selected_spheres, self.measurement_drawn_spheres)
        for i in range(4):
            self.measurement_selected_spheres[i] = -1
        self.update()

    def clear_builder_selected_atoms(self) -> None:
        """Reset the selected spheres builder spheres."""
        self.builder_selected_spheres = [-1] * 3
