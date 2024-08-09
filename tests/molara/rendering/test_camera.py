"""Test the Camera class."""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest import TestCase

import numpy as np
import pyrr
from molara.rendering.camera import Camera
from molara.util.testing import assert_vectors_equal

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

    def test_adopt_config(self) -> None:
        """Test Camera configuration adoption."""
        other_camera = Camera(1000, 800)

        other_camera.fov = 60.0
        other_camera.distance_from_target = 10.0
        other_camera.zoom_sensitivity = 0.2
        other_camera.initial_position = pyrr.Vector3([10.0, 20.0, 30.0], dtype=np.float32)
        other_camera.initial_up_vector = pyrr.Vector3([1.0, 2.0, 3.0], dtype=np.float32)
        other_camera.initial_right_vector = pyrr.Vector3([3.0, 2.0, 1.0], dtype=np.float32)
        other_camera.initial_target = pyrr.Vector3([-1.0, -2.0, -3.0], dtype=np.float32)
        other_camera.translation = pyrr.Vector3([7.0, 8.0, 9.0], dtype=np.float32)
        other_camera.rotation = pyrr.Quaternion([6.0, 2.0, 4.0, 1.0], dtype=np.float32)

        other_camera.calculate_projection_matrix()
        other_camera.update()

        camera = self.camera
        assert not camera.orthographic_projection
        assert not other_camera.orthographic_projection
        assert camera.fov != other_camera.fov
        assert camera.width != other_camera.width
        assert camera.height != other_camera.height
        assert camera.distance_from_target != other_camera.distance_from_target
        assert camera.zoom_sensitivity != other_camera.zoom_sensitivity

        camera.adopt_config(other_camera)
        assert camera.fov == other_camera.fov
        assert camera.width == other_camera.width
        assert camera.height == other_camera.height
        assert camera.distance_from_target == other_camera.distance_from_target
        assert camera.zoom_sensitivity == other_camera.zoom_sensitivity
        assert_vectors_equal(camera.position, other_camera.position)
        assert_vectors_equal(camera.up_vector, other_camera.up_vector)
        assert_vectors_equal(camera.right_vector, other_camera.right_vector)
        assert_vectors_equal(camera.translation, other_camera.translation)
        assert_vectors_equal(camera.target, other_camera.target)
        assert_vectors_equal(camera.initial_position, other_camera.initial_position)
        assert_vectors_equal(camera.initial_up_vector, other_camera.initial_up_vector)
        assert_vectors_equal(camera.initial_right_vector, other_camera.initial_right_vector)
        assert_vectors_equal(camera.last_translation, other_camera.last_translation)
        assert_vectors_equal(camera.initial_target, other_camera.initial_target)

        assert_vectors_equal(camera.rotation, other_camera.rotation)
        assert_vectors_equal(camera.last_rotation, other_camera.last_rotation)
        assert_vectors_equal(camera.view_matrix, other_camera.view_matrix)
        assert_vectors_equal(camera.view_matrix_inv, other_camera.view_matrix_inv)
        assert_vectors_equal(camera.projection_matrix, other_camera.projection_matrix)
        assert_vectors_equal(camera.projection_matrix_inv, other_camera.projection_matrix_inv)

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
        assert_vectors_equal(camera.projection_matrix, projection_matrix_perspective)

        camera.toggle_projection()
        assert camera.orthographic_projection
        camera.calculate_projection_matrix()
        assert_vectors_equal(camera.projection_matrix, projection_matrix_orthographic)

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
        assert_vectors_equal(camera.projection_matrix, projection_matrix_orthographic)

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

    def test_export_and_import_settings(self) -> None:
        """Test exporting camera settings."""
        camera = self.camera
        # set some random values
        camera.orthographic_projection = True
        camera.fov = 46.3
        camera.width, camera.height = 468, 325
        camera.distance_from_target = 3.4
        camera.zoom_sensitivity = 0.23
        camera.initial_position = pyrr.Vector3([10.764, -2.543, 1.543], dtype=np.float32)
        camera.initial_up_vector = pyrr.Vector3([0.1, 0.2, 0.7], dtype=np.float32)
        camera.initial_right_vector = pyrr.Vector3([0.9, 0.2, 0.11], dtype=np.float32)
        camera.last_translation = pyrr.Vector3([0.1, 0.2, 0.3], dtype=np.float32)
        camera.initial_target = pyrr.Vector3([0.41, 0.52, 0.63], dtype=np.float32)
        camera.last_rotation = pyrr.Quaternion([0.01, 0.22, 0.13, 0.41], dtype=np.float32)

        with NamedTemporaryFile(suffix=".json") as file:
            filename = file.name
        assert not Path(filename).exists()
        camera.export_settings(filename)

        assert Path(filename).exists()
        with open(filename) as file:
            data = json.load(file)

        # check if settings are correct
        self.assert_camera_settings_equal_data(data)
        # check if position, up_vector, right_vector, translation, target, and rotation are correct
        # (they are not checked in assert_camera_settings_equal_data)
        assert_vectors_equal(data["position"], camera.position.tolist())
        assert_vectors_equal(data["up_vector"], camera.up_vector.tolist())
        assert_vectors_equal(data["right_vector"], camera.right_vector.tolist())
        assert_vectors_equal(data["translation"], camera.translation.tolist())
        assert_vectors_equal(data["target"], camera.target.tolist())
        assert_vectors_equal(data["rotation"], camera.rotation.tolist())

        # reset camera settings
        self.set_camera_settings_to_zeros()

        # import settings again, then delete json file to clean up
        camera.import_settings(filename)
        # Path(filename).unlink()

        # check if settings are correct
        self.assert_camera_settings_equal_data(data)

    def assert_camera_settings_equal_data(self, data: dict) -> None:
        """Assert that the camera settings are equal to the data in the json file."""
        camera = self.camera
        assert camera.orthographic_projection == data["orthographic_projection"]
        assert camera.fov == data["fov"]
        assert camera.width == data["width"]
        assert camera.height == data["height"]
        assert camera.distance_from_target == data["distance_from_target"]
        assert camera.zoom_sensitivity == data["zoom_sensitivity"]
        # position, up_vector, right_vector, and target are not checked,
        # because they are re-calculated in Camera.update(),
        # so they may differ from the values in the json file.
        assert_vectors_equal(camera.translation, data["translation"])
        assert_vectors_equal(camera.rotation, data["rotation"])
        assert_vectors_equal(camera.initial_position, data["initial_position"])
        assert_vectors_equal(camera.initial_up_vector, data["initial_up_vector"])
        assert_vectors_equal(camera.initial_right_vector, data["initial_right_vector"])
        assert_vectors_equal(camera.last_translation, data["last_translation"])
        assert_vectors_equal(camera.initial_target, data["initial_target"])
        assert_vectors_equal(camera.last_rotation, data["last_rotation"])

    def set_camera_settings_to_zeros(self) -> None:
        """Set all camera settings to zero."""
        camera = self.camera
        camera.orthographic_projection = False
        camera.fov = 0.0
        camera.width = 0
        camera.height = 0
        camera.distance_from_target = 0.0
        camera.zoom_sensitivity = 0.0
        camera.position = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        camera.initial_position = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        camera.up_vector = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        camera.right_vector = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        camera.translation = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        camera.target = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        camera.rotation = pyrr.Quaternion([0.0, 0.0, 0.0, 0.0], dtype=np.float32)

    def test_set_rotation(self) -> None:
        """Test setting the rotation of the camera."""
        quaternion_x = [0.0, 0.0, 0.0, 1.0]
        quaternion_y = [0.0, 0.0, np.sqrt(2) / 2, np.sqrt(2) / 2]
        quaternion_z = [0.0, np.sqrt(2) / 2, 0.0, np.sqrt(2) / 2]
        # quaternion_y = [0.0, 0.0, 0.7071067690849304, 0.7071067690849304]
        # quaternion_z = [0.0, 0.7071067690849304, 0.0, 0.7071067690849304]

        self.camera.set_rotation("x")
        assert_vectors_equal(self.camera.rotation.tolist(), quaternion_x)
        self.camera.set_rotation("y")
        assert_vectors_equal(self.camera.rotation.tolist(), quaternion_y)
        self.camera.set_rotation("z")
        assert_vectors_equal(self.camera.rotation.tolist(), quaternion_z)

    def test_set_translation_vector(self) -> None:
        """Test setting the translation of the camera."""
        old_mouse_position = np.array([0.476, 0.325])
        mouse_position = np.array([0.239, 0.591])
        x_translation = -(mouse_position[0] - old_mouse_position[0])
        y_translation = -(mouse_position[1] - old_mouse_position[1])
        last_translation = self.camera.last_translation
        right_vector = self.camera.right_vector
        up_vector = self.camera.up_vector

        self.camera.set_translation_vector(old_mouse_position, mouse_position)
        new_translation = right_vector * x_translation + up_vector * y_translation + last_translation
        assert_vectors_equal(self.camera.translation.tolist(), new_translation.tolist())
