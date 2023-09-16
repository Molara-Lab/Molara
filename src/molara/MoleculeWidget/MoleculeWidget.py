# This Python file uses the following encoding: utf-8
import numpy as np
from OpenGL.GL import GL_DEPTH_TEST, GL_MULTISAMPLE, glClearColor, glEnable, glViewport
from PySide6.QtCore import Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from molara.Rendering.Buffers import Vao
from molara.Rendering.Camera import Camera
from molara.Rendering.Rendering import draw_scene
from molara.Rendering.Shaders import compile_shaders


class MoleculeWidget(QOpenGLWidget):
    def __init__(self, parent):
        self.shader = None
        self.parent = parent
        QOpenGLWidget.__init__(self, parent)

        self.molecule = None
        self.vertex_attribute_objects = None
        self.axes = False
        self.rotate_sphere = False
        self.click_position = None
        self.rotation_angle_x = 0.0
        self.rotation_angle_y = 0.0
        self.position = np.zeros(2)
        self.zoom_factor = 1.0
        self.contour = False
        self.bonds = True
        self.camera = Camera(self.width(), self.height())
        self.cursor_in_widget = False

    def reset_view(self):
        self.camera.reset(self.width(), self.height())
        self.update()

    def set_molecule(self, molecule):
        self.molecule = molecule
        if self.molecule.bonded_pairs[0, 0] == -1:
            self.bonds = False
        else:
            self.bonds = True
        self.center_molecule()

    def center_molecule(self):
        if self.molecule is not None:
            self.molecule.center_coordinates()
            self.set_vertex_attribute_objects()
        self.update()
    
    def toggle_axes(self):
        if self.axes:
            self.axes = False
        else:
            self.axes = True
        self.update()

    def initializeGL(self):
        glClearColor(1, 1, 1, 1.0)
        glEnable(GL_DEPTH_TEST, GL_MULTISAMPLE)
        self.shader = compile_shaders()

    def resizeGL(self, width, height):
        glViewport(0, 0, self.width(), self.height())
        self.camera.calculate_projection_matrix(self.width(), self.height())
        self.update()

    def paintGL(self):
        draw_scene(self.shader, self.camera, self.vertex_attribute_objects, self.molecule)
        return

    def set_vertex_attribute_objects(self):
        self.vertex_attribute_objects = []
        for atomic_number in self.molecule.unique_atomic_numbers:
            vao = Vao(
                self,
                self.molecule.drawer.unique_spheres[atomic_number].vertices,
                self.molecule.drawer.unique_spheres[atomic_number].indices,
                self.molecule.drawer.unique_spheres[atomic_number].model_matrices,
            )
            self.vertex_attribute_objects.append(vao.vao)
        for atomic_number in self.molecule.unique_atomic_numbers:
            vao = Vao(
                self,
                self.molecule.drawer.unique_cylinders[atomic_number].vertices,
                self.molecule.drawer.unique_cylinders[atomic_number].indices,
                self.molecule.drawer.unique_cylinders[atomic_number].model_matrices,
            )
            self.vertex_attribute_objects.append(vao.vao)

    def draw_axes(self):
        return

    def wheelEvent(self, event):
        self.zoom_factor = 1
        num_degrees = event.angleDelta().y() / 8
        num_steps = num_degrees / 100  # Empirical value to control zoom speed
        self.zoom_factor += num_steps * 0.1  # Empirical value to control zoom sensitivity
        self.zoom_factor = max(0.1, self.zoom_factor)  # Limit zoom factor to avoid zooming too far
        self.camera.set_distance_from_target(self.zoom_factor)
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and event.x() in range(self.width()) and event.y() in range(self.height()):
            self.rotate_sphere = True
            self.set_normalized_position(event)
            self.click_position = np.copy(self.position)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.rotate_sphere and self.click_position is not None:
            self.set_normalized_position(event)
            self.camera.calculate_camera_position(self.click_position, self.position)
            self.update()

    def set_normalized_position(self, event):
        if self.width() >= self.height():
            self.position[0] = (event.x() * 2 - self.width()) / self.width()
            self.position[1] = -(event.y() * 2 - self.height()) / self.width()
        else:
            self.position[0] = (event.x() * 2 - self.width()) / self.height()
            self.position[1] = -(event.y() * 2 - self.height()) / self.height()
        self.position = np.array(self.position, dtype=np.float32)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.rotate_sphere:
            self.rotate_sphere = False
            self.set_normalized_position(event)
            self.camera.calculate_camera_position(self.click_position, self.position, save=True)
            self.click_position = None
            # self.update()
