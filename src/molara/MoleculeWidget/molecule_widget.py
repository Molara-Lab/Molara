from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from OpenGL.GL import GL_DEPTH_TEST, GL_MULTISAMPLE, glClearColor, glEnable, glViewport
from PySide6.QtCore import QEvent, Qt
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from molara.Rendering.buffers import Vao
from molara.Rendering.camera import Camera
from molara.Rendering.rendering import draw_scene
from molara.Rendering.shaders import compile_shaders

if TYPE_CHECKING:
    from PySide6.QtGui import QMouseEvent

    from molara.Molecule.molecule import Molecule


class MoleculeWidget(QOpenGLWidget):
    def __init__(self, parent: QOpenGLWidget) -> None:
        self.shader = None
        self.parent = parent
        QOpenGLWidget.__init__(self, parent)

        self.molecule = None
        self.vertex_attribute_objects = None
        self.axes = False
        self.rotate = False
        self.translate = False
        self.click_position = None
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
        self.camera.reset(self.width(), self.height())
        self.update()

    def set_molecule(self, molecule: Molecule) -> None:
        self.molecule = molecule
        if self.molecule.bonded_pairs[0, 0] == -1:
            self.bonds = False
        else:
            self.bonds = True
        self.center_molecule()

    def center_molecule(self) -> None:
        if self.molecule is not None:
            self.molecule.center_coordinates()
            self.set_vertex_attribute_objects()
        self.update()

    def toggle_axes(self) -> None:
        if self.axes:
            self.axes = False
        else:
            self.axes = True
        self.update()

    def initializeGL(self) -> None:  # noqa: N802
        glClearColor(1, 1, 1, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        self.shader = compile_shaders()

    def resizeGL(self, width: int, height: int) -> None:  # noqa: N802
        glViewport(0, 0, self.width(), self.height())
        self.camera.calculate_projection_matrix(self.width(), self.height())
        self.update()

    def paintGL(self) -> None:  # noqa: N802
        draw_scene(self.shader, self.camera, self.vertex_attribute_objects, self.molecule)
        return

    def set_vertex_attribute_objects(self) -> None:
        self.vertex_attribute_objects = []
        for atomic_number in self.molecule.unique_atomic_numbers:
            idx = self.molecule.drawer.unique_spheres_mapping[atomic_number]
            vao = Vao(
                self,
                self.molecule.drawer.unique_spheres[idx].vertices,
                self.molecule.drawer.unique_spheres[idx].indices,
                self.molecule.drawer.unique_spheres[idx].model_matrices,
            )
            self.vertex_attribute_objects.append(vao.vao)
        for atomic_number in self.molecule.unique_atomic_numbers:
            idx = self.molecule.drawer.unique_cylinders_mapping[atomic_number]
            vao = Vao(
                self,
                self.molecule.drawer.unique_cylinders[idx].vertices,
                self.molecule.drawer.unique_cylinders[idx].indices,
                self.molecule.drawer.unique_cylinders[idx].model_matrices,
            )
            self.vertex_attribute_objects.append(vao.vao)

    def draw_axes(self) -> None:
        return

    def wheelEvent(self, event: QEvent) -> None:  # noqa: N802
        self.zoom_factor = 1
        num_degrees = event.angleDelta().y() / 8
        num_steps = num_degrees / 100  # Empirical value to control zoom speed
        self.zoom_factor += num_steps * 0.1  # Empirical value to control zoom sensitivity
        self.zoom_factor = max(0.1, self.zoom_factor)  # Limit zoom factor to avoid zooming too far
        self.camera.set_distance_from_target(self.zoom_factor)
        self.camera.update()
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
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
        if self.width() >= self.height():
            self.position[0] = (event.x() * 2 - self.width()) / self.width()
            self.position[1] = -(event.y() * 2 - self.height()) / self.width()
        else:
            self.position[0] = (event.x() * 2 - self.width()) / self.height()
            self.position[1] = -(event.y() * 2 - self.height()) / self.height()
        self.position = np.array(self.position, dtype=np.float32)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
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
