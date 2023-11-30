"""This module contains the MoleculeWidget class, which is a subclass of QOpenGLWidget."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import numpy as np
from OpenGL.GL import GL_DEPTH_TEST, GL_MULTISAMPLE, glClearColor, glEnable, glViewport
from PySide6.QtCore import QEvent, Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from molara.Rendering.camera import Camera
from molara.Rendering.rendering import Renderer
from molara.Rendering.shaders import compile_shaders

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent

    from molara.Molecule.molecule import Molecule


class MoleculeWidget(QOpenGLWidget):
    """Creates a MoleculeWidget object, which is a subclass of QOpenGLWidget."""

    def __init__(self, parent: QOpenGLWidget) -> None:
        """Creates a MoleculeWidget object, which is a subclass of QOpenGLWidget."""
        self.parent = parent  # type: ignore[method-assign, assignment]
        QOpenGLWidget.__init__(self, parent)

        self.renderer = Renderer()
        self.molecule_is_set = False
        self.vertex_attribute_objects = [-1]
        self.axes = [-1, -1]  # -1 means no axes are drawn, any other integer means axes are drawn
        self.rotate = False
        self.translate = False
        self.click_position: np.ndarray | None = None
        self.rotation_angle_x = 0.0
        self.rotation_angle_y = 0.0
        self.position = np.zeros(2)
        self.old_position = np.zeros(2)
        self.zoom_factor = 1.0
        self.contour = False
        self.bonds = True
        self.camera = Camera(self.width(), self.height())
        self.cursor_in_widget = False

    def reset_view(self) -> None:
        """Resets the view of the molecule to the initial view."""
        self.camera.reset(self.width(), self.height())
        self.update()

    def delete_molecule(self) -> None:
        """Delete molecule and reset vertex attributes."""
        self.vertex_attribute_objects = []
        self.update()

    def set_molecule(self, molecule: Molecule) -> None:
        """Sets the molecule to be drawn."""
        self.molecule = molecule
        if self.molecule.bonded_pairs[0, 0] == -1:
            self.bonds = False
        else:
            self.bonds = True
        self.molecule_is_set = True
        self.center_molecule()

    def center_molecule(self) -> None:
        """Centers the molecule in the widget."""
        if self.molecule_is_set:
            self.molecule.center_coordinates()
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
        if self.molecule_is_set:
            self.renderer.draw_scene(
                self.camera,
            )
        else:
            self.renderer.draw_scene(self.camera)

    def set_vertex_attribute_objects(self) -> None:
        """Sets the vertex attribute objects of the molecule."""
        self.makeCurrent()
        self.renderer.update_atoms_vao(
            self.molecule.drawer.sphere.vertices,
            self.molecule.drawer.sphere.indices,
            self.molecule.drawer.sphere_model_matrices,
            self.molecule.drawer.sphere_colors,
        )
        self.renderer.update_bonds_vao(
            self.molecule.drawer.cylinder.vertices,
            self.molecule.drawer.cylinder.indices,
            self.molecule.drawer.cylinder_model_matrices,
            self.molecule.drawer.cylinder_colors,
        )

    def wheelEvent(self, event: QEvent) -> None:  # noqa: N802
        """Zooms in and out of the molecule."""
        self.zoom_factor = 1
        num_degrees = event.angleDelta().y() / 8  # type: ignore[attr-defined]
        num_steps = num_degrees / 100  # Empirical value to control zoom speed
        self.zoom_factor += num_steps * 0.1  # Empirical value to control zoom sensitivity
        self.zoom_factor = max(
            0.1,
            self.zoom_factor,
        )  # Limit zoom factor to avoid zooming too far
        self.camera.set_distance_from_target(self.zoom_factor)
        self.camera.update()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        """Starts the rotation or translation of the molecule."""
        if (
            event.button() == Qt.MouseButton.LeftButton
            and event.x() in range(self.width())
            and event.y() in range(self.height())
        ):
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
            positions = np.array([[length / 2, 0, 0], [0, length / 2, 0], [0, 0, length / 2]], dtype=np.float32)
            directions = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
            colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=np.float32)
            radii = np.array([radius] * 3, dtype=np.float32)
            lengths = np.array([length] * 3, dtype=np.float32)
            self.axes[0] = self.renderer.draw_cylinders(positions, directions, radii, lengths, colors, 25)
            positions = np.array([[length, 0, 0], [0, length, 0], [0, 0, length], [0, 0, 0]], dtype=np.float32)
            colors = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=np.float32)
            radii = np.array([radius] * 4, dtype=np.float32)
            self.axes[1] = self.renderer.draw_spheres(positions, radii, colors, 25)
        self.update()
