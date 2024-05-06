"""Test the Camera class."""

from __future__ import annotations

from unittest import TestCase

import numpy as np
import pyrr
from molara.Rendering.camera import Camera
from numpy.testing import assert_array_equal

__copyright__ = "Copyright 2024, Molara"


class TestCamera(TestCase):
    """Test the Camera class."""

    def setUp(self) -> None:
        """Set up a Camera object."""
        self.width, self.height = 400, 300
        self.camera = Camera(self.width, self.height)

    def test_setup(self) -> None:
        """Test Camera setup."""
        camera = self.camera
        fov, distance_from_target, zoom_sensitivity = 45.0, 5.0, 0.15
        assert not camera.orthographic_projection
        assert camera.fov == fov
        assert camera.width == self.width
        assert camera.height == self.height
        assert camera.distance_from_target == distance_from_target
        assert camera.zoom_sensitivity == zoom_sensitivity
        assert isinstance(camera.position, pyrr.Vector3)
        assert isinstance(camera.initial_position, pyrr.Vector3)
        assert isinstance(camera.up_vector, pyrr.Vector3)
        assert isinstance(camera.right_vector, pyrr.Vector3)
        assert isinstance(camera.translation, pyrr.Vector3)
        assert isinstance(camera.target, pyrr.Vector3)
        assert isinstance(camera.rotation, pyrr.Quaternion)
        assert isinstance(camera.view_matrix, np.ndarray)
        assert camera.view_matrix.shape == (4, 4)
        assert isinstance(camera.view_matrix_inv, np.ndarray)
        assert camera.view_matrix_inv.shape == (4, 4)
        assert isinstance(camera.projection_matrix, np.ndarray)
        assert camera.projection_matrix.shape == (4, 4)
        assert isinstance(camera.projection_matrix_inv, np.ndarray)
        assert camera.projection_matrix_inv.shape == (4, 4)

    def test_reset(self) -> None:
        """Test Camera reset."""
        self.width, self.height = 444, 333
        self.camera.reset(self.width, self.height)
        assert self.camera.width == self.width
        assert self.camera.height == self.height

    def test_calculate_projection_matrix(self) -> None:
        """Test projection matrix calculation."""
        camera = self.camera
        width, height = camera.width, camera.height
        fov = camera.fov
        distance_from_target = camera.distance_from_target

        projection_matrix_perspective = pyrr.matrix44.create_perspective_projection_matrix(
            fov,
            width / height,
            0.1,
            100,
            dtype=np.float32,
        )

        # calculate width and height of the clipping plane
        # such that it matches the field of view in the perspective projection
        h = distance_from_target * np.tan(np.radians(fov / 2))
        w = h * width / height
        projection_matrix_orthographic = pyrr.matrix44.create_orthogonal_projection_matrix(
            -w,
            w,
            -h,
            h,
            0.1,
            100,
            dtype=np.float32,
        )

        assert not camera.orthographic_projection
        camera.calculate_projection_matrix()
        assert isinstance(camera.projection_matrix, np.ndarray)
        assert_array_equal(camera.projection_matrix, projection_matrix_perspective)

        camera.toggle_projection()
        assert camera.orthographic_projection
        camera.calculate_projection_matrix()
        assert_array_equal(camera.projection_matrix, projection_matrix_orthographic)

        camera.set_distance_from_target(40)
        old_distance_from_target = distance_from_target
        distance_from_target = camera.distance_from_target
        assert distance_from_target > old_distance_from_target
        h = distance_from_target * np.tan(np.radians(fov / 2))
        w = h * width / height
        projection_matrix_orthographic = pyrr.matrix44.create_orthogonal_projection_matrix(
            -w,
            w,
            -h,
            h,
            0.1,
            100,
            dtype=np.float32,
        )
        # in orthographic projection, the projection matrix must be updated when camera.update() is called.
        # here, we test if this is actually the case.
        camera.update()
        assert_array_equal(camera.projection_matrix, projection_matrix_orthographic)

    def test_center_coordinates(self) -> None:
        """Test coordinate recentering."""
        translation = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        self.camera.center_coordinates()
        assert self.camera.translation == translation
        assert self.camera.last_translation == self.camera.translation

    def test_set_distance_from_target(self) -> None:
        """Test setting the distance of the camera to the target point."""
        former_distance = self.camera.distance_from_target
        zoom_sensitivity = self.camera.zoom_sensitivity
        num_steps = 2902
        zoom_factor = max(0.1, 1.0 + num_steps * 1.0)
        self.camera.set_distance_from_target(num_steps)
        new_distance = max(
            1.0,
            former_distance + np.log10(zoom_factor * zoom_sensitivity) * (np.sign(zoom_factor - 1)),
        )
        assert self.camera.distance_from_target == new_distance

    def set_translation_vector(self) -> None:
        """Test setting the translation of the camera."""
        old_mouse_position = np.array([0.476, 0.325])
        mouse_position = np.array([0.239, 0.591])
        x_translation = -(mouse_position[0] - old_mouse_position[0])
        y_translation = -(mouse_position[0] - old_mouse_position[0])
        last_translation = self.camera.last_translation
        right_vector = self.camera.right_vector
        up_vector = self.camera.up_vector

        self.camera.set_translation_vector(old_mouse_position, mouse_position)
        new_translation = right_vector * x_translation + up_vector * y_translation + last_translation
        assert self.camera.translation == new_translation
