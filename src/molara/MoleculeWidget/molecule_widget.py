"""This module contains the MoleculeWidget class, which is a subclass of QOpenGLWidget."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from OpenGL.GL import GL_DEPTH_TEST, GL_MULTISAMPLE, glClearColor, glEnable, glViewport
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from molara.Gui.measuring_tool_dialog import MeasurementDialog
from molara.Gui.mos_dialog import MOsDialog
from molara.Rendering.camera import Camera
from molara.Rendering.rendering import Renderer
from molara.Rendering.shaders import compile_shaders
from molara.Tools.raycasting import select_sphere

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QMainWindow

    from molara.Molecule.structure import Structure

__copyright__ = "Copyright 2024, Molara"


class MoleculeWidget(QOpenGLWidget):
    """Creates a MoleculeWidget object, which is a subclass of QOpenGLWidget."""

    def __init__(self, parent: QMainWindow) -> None:
        """Creates a MoleculeWidget object, which is a subclass of QOpenGLWidget."""
        self.parent = parent  # type: ignore[method-assign, assignment]
        QOpenGLWidget.__init__(self, parent)

        self.measurement_dialog = MeasurementDialog(parent)
        self.display_mos_dialog = MOsDialog(parent)
        self.renderer = Renderer()
        self.molecule_is_set = False
        self.vertex_attribute_objects = [-1]
        self.axes = [
            -1,
            -1,
        ]  # -1 means no axes are drawn, any other integer means axes are drawn
        self.rotate = False
        self.translate = False
        self.click_position: np.ndarray | None = None
        self.rotation_angle_x = 0.0
        self.rotation_angle_y = 0.0
        self.position = np.zeros(2)
        self.old_position = np.zeros(2)
        self.contour = False
        self.bonds = True
        self.camera = Camera(self.width(), self.height())
        self.cursor_in_widget = False
        self.selected_spheres: list = [-1] * 4
        self.old_sphere_colors: list = [np.ndarray] * 4
        self.new_sphere_colors: list = [
            np.array([1, 0, 0], dtype=np.float32),
            np.array([0, 1, 0], dtype=np.float32),
            np.array([0, 0, 1], dtype=np.float32),
            np.array([1, 1, 0], dtype=np.float32),
        ]

    def reset_view(self) -> None:
        """Resets the view of the molecule to the initial view."""
        self.camera.reset(self.width(), self.height())
        self.update()

    def delete_molecule(self) -> None:
        """Delete molecule and reset vertex attributes."""
        self.vertex_attribute_objects = []
        self.update()

    def set_structure(self, struct: Structure) -> None:
        """Sets the molecule to be drawn."""
        self.structure = struct
        if self.structure.bonded_pairs[0, 0] == -1:
            self.bonds = False
        else:
            self.bonds = True
        self.molecule_is_set = True
        self.center_molecule()

    def center_molecule(self) -> None:
        """Centers the molecule in the widget."""
        if self.molecule_is_set:
            #self.structure.center_coordinates()
            self.set_vertex_attribute_objects()
        self.update()

    def initializeGL(self) -> None:  # noqa: N802
        """Initializes the widget."""
        glClearColor(1, 1, 1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        self.renderer.set_shader(compile_shaders())

    def resizeGL(self, width: int, height: int) -> None:  # noqa: ARG002, N802
        """Resizes the widget."""
        glViewport(0, 0, self.width(), self.height())
        self.camera.calculate_projection_matrix(self.width(), self.height())
        self.update()

    def paintGL(self) -> None:  # noqa: N802
        """Draws the scene."""
        self.renderer.draw_scene(self.camera, self.bonds)

    def set_vertex_attribute_objects(self) -> None:
        """Sets the vertex attribute objects of the molecule."""
        self.makeCurrent()
        self.renderer.update_atoms_vao(
            self.structure.drawer.sphere.vertices,
            self.structure.drawer.sphere.indices,
            self.structure.drawer.sphere_model_matrices,
            self.structure.drawer.atom_colors,
        )
        self.renderer.update_bonds_vao(
            self.structure.drawer.cylinder.vertices,
            self.structure.drawer.cylinder.indices,
            self.structure.drawer.cylinder_model_matrices,
            self.structure.drawer.cylinder_colors,
        )

    def wheelEvent(self, event: QEvent) -> None:  # noqa: N802
        """Zooms in and out of the molecule."""
        num_degrees = event.angleDelta().y() / 8  # type: ignore[attr-defined]
        num_steps = num_degrees / 100  # Empirical value to control zoom speed
        self.camera.set_distance_from_target(num_steps)
        self.camera.update()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Starts the rotation or translation of the molecule."""
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.x() in range(self.width())
            and event.y() in range(self.height())
        ):
            if bool(QGuiApplication.keyboardModifiers() & Qt.ShiftModifier):  # type: ignore[attr-defined]
                if self.measurement_dialog.isVisible():
                    self.update_selected_atoms(event)
            else:
                self.rotate = True
                if self.translate is True:
                    self.stop_translate(event)
                self.set_normalized_position(event)
                self.click_position = np.copy(self.position)
        if (
            event.button() == Qt.MouseButton.RightButton
            and event.x() in range(self.width())
            and event.y() in range(self.height())
        ):
            self.translate = True
            if self.rotate is True:
                self.stop_rotation(event)
            self.set_normalized_position(event)
            self.click_position = np.copy(self.position)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Rotates or translates the molecule."""
        if self.rotate and self.click_position is not None:
            self.set_normalized_position(event)
            self.camera.set_rotation_quaternion(self.click_position, self.position)
            self.camera.update()
            self.update()
        if self.translate and self.click_position is not None:
            self.set_normalized_position(event)
            self.camera.set_translation_vector(self.click_position, self.position)
            self.camera.update()
            self.update()

    def set_normalized_position(self, event: QMouseEvent) -> None:
        """Sets the normalized position of the mouse cursor."""
        if self.width() >= self.height():
            self.position[0] = (event.x() * 2 - self.width()) / self.width()
            self.position[1] = -(event.y() * 2 - self.height()) / self.width()
        else:
            self.position[0] = (event.x() * 2 - self.width()) / self.height()
            self.position[1] = -(event.y() * 2 - self.height()) / self.height()
        self.position = np.array(self.position, dtype=np.float32)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Stops the rotation or translation of the molecule."""
        if event.button() == Qt.MouseButton.LeftButton and self.rotate:
            self.stop_rotation(event)
        if event.button() == Qt.MouseButton.RightButton and self.translate:
            self.stop_translate(event)

    def stop_translate(self, event: QMouseEvent) -> None:
        """Stops the translation of the molecule.

        :return:
        """
        self.translate = False
        self.set_normalized_position(event)
        self.camera.update(save=True)
        self.click_position = None

    def stop_rotation(self, event: QMouseEvent) -> None:
        """Stops the rotation of the molecule.

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
        if self.axes[0] != -1:
            self.renderer.remove_cylinder(self.axes[0])
            self.renderer.remove_sphere(self.axes[1])
            self.axes = [-1, -1]
        else:
            positions = np.array(
                [[length / 2, 0, 0], [0, length / 2, 0], [0, 0, length / 2]],
                dtype=np.float32,
            )
            directions = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
            colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
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

    def show_measurement_dialog(self) -> None:
        """Show the measurement dialog."""
        if self.molecule_is_set:
            self.measurement_dialog.ini_labels()
            self.measurement_dialog.show()

    def show_mos_dialog(self) -> None:
        """Show the measurement dialog."""
        if self.molecule_is_set:
            if self.display_mos_dialog.check_if_mos():
                self.display_mos_dialog.show()
            else:
                print("No MOs available.")

    def update_selected_atoms(self, event: QMouseEvent) -> None:
        """Updates the selected atoms in the measurement dialog.

        :param event: The mouse event.
        :return:
        """
        self.makeCurrent()
        click_position = np.array(
            [
                (event.x() * 2 - self.width()) / self.width(),
                (event.y() * 2 - self.height()) / self.height(),
            ],
            dtype=np.float32,
        )
        selected_sphere = select_sphere(
            click_position,
            self.camera.position,
            self.camera.view_matrix_inv,
            self.camera.projection_matrix_inv,
            self.camera.fov,
            self.height() / self.width(),
            self.structure.drawer.atom_positions,
            self.structure.drawer.atom_scales[:, 0],  # type: ignore[call-overload]
        )
        if selected_sphere != -1:
            if -1 in self.selected_spheres:
                if selected_sphere in self.selected_spheres:
                    self.structure.drawer.atom_colors[selected_sphere] = self.old_sphere_colors[
                        self.selected_spheres.index(selected_sphere)
                    ].copy()
                    self.selected_spheres[self.selected_spheres.index(selected_sphere)] = -1
                else:
                    self.selected_spheres[self.selected_spheres.index(-1)] = selected_sphere
                    self.old_sphere_colors[
                        self.selected_spheres.index(selected_sphere)
                    ] = self.structure.drawer.atom_colors[selected_sphere].copy()
                    self.structure.drawer.atom_colors[selected_sphere] = self.new_sphere_colors[
                        self.selected_spheres.index(selected_sphere)
                    ].copy()
            elif selected_sphere in self.selected_spheres:
                self.structure.drawer.atom_colors[selected_sphere] = self.old_sphere_colors[
                    self.selected_spheres.index(selected_sphere)
                ].copy()
                self.selected_spheres[self.selected_spheres.index(selected_sphere)] = -1

        self.renderer.update_atoms_vao(
            self.structure.drawer.sphere.vertices,
            self.structure.drawer.sphere.indices,
            self.structure.drawer.sphere_model_matrices,
            self.structure.drawer.atom_colors,
        )
        self.update()
        self.measurement_dialog.display_metrics(
            self.structure,
            self.selected_spheres,
        )
