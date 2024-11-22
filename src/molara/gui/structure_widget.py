"""Contains the StructureWidget class, which is a subclass of QOpenGLWidget."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np
from OpenGL.GL import GL_DEPTH_TEST, GL_MULTISAMPLE, glClearColor, glEnable, glViewport
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from molara.rendering.atom_labels import calculate_atom_number_arrays
from molara.rendering.camera import Camera
from molara.rendering.rendering import Renderer
from molara.rendering.shaders import compile_shaders
from molara.structure.crystal import Crystal
from molara.tools.raycasting import select_sphere

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QWidget

    from molara.structure.molecule import Molecule
    from molara.structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"

MEASUREMENT, BUILDER = 0, 1


class StructureWidget(QOpenGLWidget):
    """Creates a StructureWidget object, which is a subclass of QOpenGLWidget."""

    def __init__(self, parent: QWidget) -> None:
        """Create a StructureWidget object, which is a subclass of QOpenGLWidget.

        :param parent: parent widget (main window's central widget)
        """
        self.central_widget = parent
        self.main_window = self.central_widget.parent()  # type: ignore[method-assign, assignment]
        QOpenGLWidget.__init__(self, parent)

        self.renderer = Renderer()
        self.structures: list[Structure | Molecule | Crystal] = []
        self.vertex_attribute_objects = [-1]
        self.axes = [
            -1,
            -1,
        ]  # -1 means no axes are drawn, any other integer means axes are drawn
        self.box = [
            -1,
            -1,
        ]
        self.rotate = False
        self.translate = False
        self.click_position: np.ndarray | None = None
        self.rotation_angle_x = 0.0
        self.rotation_angle_y = 0.0
        self.position = np.zeros(2)
        self.old_position = np.zeros(2)
        self.contour = False
        self.camera = Camera(self.width(), self.height())
        self.cursor_in_widget = False
        self.measurement_selected_spheres: list = [-1] * 4
        self.builder_selected_spheres: list = [-1] * 3

        self.old_sphere_colors: list = [np.ndarray] * 4
        self.new_sphere_colors: list = [
            np.array([1, 0, 0], dtype=np.float32),
            np.array([0, 1, 0], dtype=np.float32),
            np.array([0, 0, 1], dtype=np.float32),
            np.array([1, 1, 0], dtype=np.float32),
        ]
        self.show_atom_indices = False
        self.atom_indices_arrays: tuple[np.ndarray, np.ndarray] = (np.zeros(1), np.zeros(1))
        self.number_scale = 1.0

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
    def draw_axes(self) -> bool:
        """Specifies whether the axes should be drawn."""
        return self.axes[0] != -1

    @property
    def draw_unit_cell_boundaries(self) -> bool:
        """Specifies whether the unit cell boundaries should be drawn."""
        return self.box[0] != -1

    @property
    def orthographic_projection(self) -> bool:
        """Specifies whether the projection is orthographic or not."""
        return self.camera.orthographic_projection

    def update_atom_number_labels(self) -> None:
        """Update the positions of the labels."""
        assert self.structures

        calculate_atom_number_arrays(
            self.atom_indices_arrays[0],
            self.atom_indices_arrays[1],
            self.structures[0],
            self.camera,
        )
        self.renderer.draw_numbers(
            self.atom_indices_arrays[0],
            self.atom_indices_arrays[1],
        )

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
            self.set_vertex_attribute_objects()
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
        self.set_vertex_attribute_objects()
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
        self.camera.import_settings(filename)
        self.update()

    def initializeGL(self) -> None:  # noqa: N802
        """Initialize the widget."""
        glClearColor(1, 1, 1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        self.renderer.set_shaders(compile_shaders())
        self.renderer.aspect_ratio = self.width() / self.height()

    def resizeGL(self, width: int, height: int) -> None:  # noqa: N802
        """Resizes the widget.

        :param width: widget width (in pixels)
        :param height: widget height (in pixels)
        """
        glViewport(0, 0, width, height)  # one can also use self.width() and self.height()
        self.camera.width, self.camera.height = width, height
        self.camera.calculate_projection_matrix()
        self.renderer.aspect_ratio = self.width() / self.height()
        self.update()

    def paintGL(self) -> None:  # noqa: N802
        """Draws the scene."""
        self.makeCurrent()
        self.renderer.draw_scene(self.camera, self.bonds)
        if self.show_atom_indices:
            self.update_atom_number_labels()
            self.renderer.display_numbers(self.camera, self.number_scale)

    def set_vertex_attribute_objects(self, update_bonds: bool = True) -> None:
        """Set the vertex attribute objects of the structure."""
        assert isinstance(self.structures[0].drawer.cylinder_colors, np.ndarray)
        sphere_vertices = self.structures[0].drawer.sphere.vertices
        sphere_indices = self.structures[0].drawer.sphere.indices
        cylinder_vertices = self.structures[0].drawer.cylinder.vertices
        cylinder_indices = self.structures[0].drawer.cylinder.indices
        sphere_model_matrices = self.structures[0].drawer.sphere_model_matrices
        atom_colors = self.structures[0].drawer.atom_colors
        cylinder_model_matrices = self.structures[0].drawer.cylinder_model_matrices
        cylinder_colors = self.structures[0].drawer.cylinder_colors
        for i in range(1, len(self.structures)):
            sphere_model_matrices = np.concatenate(
                (sphere_model_matrices, self.structures[i].drawer.sphere_model_matrices),
                axis=0,
            )
            atom_colors = np.concatenate(
                (atom_colors, self.structures[i].drawer.atom_colors),
                axis=0,
            )
            cylinder_model_matrices = np.concatenate(
                (cylinder_model_matrices, self.structures[i].drawer.cylinder_model_matrices),
                axis=0,
            )
            cylinder_colors = np.concatenate(
                (cylinder_colors, self.structures[i].drawer.cylinder_colors),
                axis=0,
            )
        self.makeCurrent()
        self.renderer.update_atoms_vao(
            sphere_vertices,
            sphere_indices,
            sphere_model_matrices,
            atom_colors,
        )
        self.renderer.update_bonds_vao(
            cylinder_vertices,
            cylinder_indices,
            cylinder_model_matrices,
            cylinder_colors,
        ) if update_bonds else None

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

        if event.button() == Qt.MouseButton.LeftButton:
            # first test if Shift key is pressed (for selecting atoms)
            if bool(QGuiApplication.keyboardModifiers() & Qt.ShiftModifier):  # type: ignore[attr-defined]
                if self.main_window.measurement_dialog.isVisible():
                    self.update_selected_atoms(MEASUREMENT, event)
                if self.main_window.builder_dialog.isVisible():
                    self.update_selected_atoms(BUILDER, event)
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
        if self.draw_axes:
            self.renderer.remove_cylinder(self.axes[0])
            self.renderer.remove_sphere(self.axes[1])
            self.axes = [-1, -1]
            self.update()
            self.main_window.update_action_texts()
            return

        positions = np.array(
            [[length / 2, 0, 0], [0, length / 2, 0], [0, 0, length / 2]],
            dtype=np.float32,
        )
        directions = np.eye(3, dtype=np.float32)
        colors = np.eye(3, dtype=np.float32)
        radii = np.array([radius] * 3, dtype=np.float32)
        lengths = np.array([length] * 3, dtype=np.float32)
        self.axes[0] = self.renderer.draw_cylinders(
            positions,
            directions,
            radii,
            lengths,
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
        self.axes[1] = self.renderer.draw_spheres(positions, radii, colors, 25)
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

        box_was_drawn = self.box[0] != -1

        if not box_was_drawn and update_box:
            # if no box is drawn and unit cell boundary shall not be toggled but just updated, nothing needs to be done!
            return

        if box_was_drawn:
            self.renderer.remove_cylinder(self.box[0])
            # if a box was drawn and the unit cell boundary shall not be simply updated,
            # the box should be removed.
            if not update_box:
                self.box = [-1, -1]
                self.update()
                self.main_window.update_action_texts()
                return
            if not isinstance(self.structures[0], Crystal):
                self.box = [-1, -1]
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
        self.box[0] = self.renderer.draw_cylinders_from_to(
            positions,
            radii,
            colors,
            25,
        )
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
            self.structures[0].drawer.atom_positions,
            self.structures[0].drawer.atom_scales[:, 0],  # type: ignore[call-overload]
        )

    def exec_select_sphere(self, sphere_id: int, selected_spheres_list: list) -> None:
        """Select a sphere, change its color, update the selected spheres list.

        :param sphere_id: id of the sphere that shall be selected
        :param selected_spheres_list: list of selected spheres
        """
        id_in_selection = selected_spheres_list.index(-1)
        selected_spheres_list[id_in_selection] = sphere_id
        self.old_sphere_colors[id_in_selection] = self.structures[0].drawer.atom_colors[sphere_id].copy()
        self.structures[0].drawer.atom_colors[sphere_id] = self.new_sphere_colors[id_in_selection].copy()

    def exec_unselect_sphere(self, sphere_id: int, selected_spheres_list: list) -> None:
        """Unselect a sphere, change its color, update the selected spheres list.

        :param sphere_id: id of the sphere that shall be unselected
        :param selected_spheres_list: list of selected spheres
        """
        if sphere_id == -1:
            return

        id_in_selection = selected_spheres_list.index(sphere_id)
        self.structures[0].drawer.atom_colors[sphere_id] = self.old_sphere_colors[id_in_selection].copy()
        self.measurement_selected_spheres[id_in_selection] = -1

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

        selected_spheres_list = (
            self.measurement_selected_spheres if purpose == MEASUREMENT else self.builder_selected_spheres
        )

        if selected_sphere_id != -1:
            if -1 in selected_spheres_list:
                if selected_sphere_id in selected_spheres_list:
                    self.exec_unselect_sphere(selected_sphere_id, selected_spheres_list)
                else:
                    self.exec_select_sphere(selected_sphere_id, selected_spheres_list)
            elif selected_sphere_id in self.measurement_selected_spheres:
                self.exec_unselect_sphere(selected_sphere_id, selected_spheres_list)
        elif bool(QGuiApplication.keyboardModifiers() & Qt.ControlModifier):  # type: ignore[attr-defined]
            for selected_sphere_i in self.measurement_selected_spheres:
                self.exec_unselect_sphere(selected_sphere_i, selected_spheres_list)

        self.renderer.update_atoms_vao(
            self.structures[0].drawer.sphere.vertices,
            self.structures[0].drawer.sphere.indices,
            self.structures[0].drawer.sphere_model_matrices,
            self.structures[0].drawer.atom_colors,
        )
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
        for selected_sphere_i in self.measurement_selected_spheres:
            if selected_sphere_i == -1:
                continue
            color = self.old_sphere_colors[self.measurement_selected_spheres.index(selected_sphere_i)].copy()
            self.structures[0].drawer.atom_colors[selected_sphere_i] = color
        for i in range(4):
            self.measurement_selected_spheres[i] = -1
        self.set_vertex_attribute_objects(update_bonds=False)
        self.update()

    def clear_builder_selected_atoms(self) -> None:
        """Reset the selected spheres builder spheres."""
        self.builder_selected_spheres = [-1] * 3
