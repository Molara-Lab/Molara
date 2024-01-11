"""Camera class for the opengl widget."""

from __future__ import annotations

import numpy as np
import pyrr

__copyright__ = "Copyright 2024, Molara"


class Camera:
    """Creates a Camera object.

    :param width: Width of the opengl widget.
    :param height: Height of the opengl widget.
    """

    def __init__(self, width: float, height: float) -> None:
        """Creates a Camera object."""
        self.fov = 45.0
        self.width = width
        self.height = height
        self.position = pyrr.Vector3([1.0, 0.0, 0.0], dtype=np.float32)
        self.up_vector = pyrr.Vector3([0.0, 1.0, 0.0], dtype=np.float32)
        self.right_vector = pyrr.Vector3([0.0, 0.0, -1.0], dtype=np.float32)
        self.distance_from_target = 5.0
        self.zoom_sensitivity = 0.15
        self.projection_matrix = None
        self.calculate_projection_matrix(self.width, self.height)

        self.rotation = pyrr.Quaternion()
        self.last_rotation = self.rotation
        self.translation = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        self.last_translation = self.translation
        self.position *= self.distance_from_target
        self.target = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        self.initial_target = self.target
        self.initial_position = pyrr.Vector3(
            pyrr.vector3.normalize(self.position),
            dtype=np.float32,
        )
        self.initial_up_vector = self.up_vector
        self.initial_right_vector = self.right_vector
        self.view_matrix = pyrr.matrix44.create_look_at(
            self.position,
            self.target,
            self.up_vector,
            dtype=np.float32,
        )
        self.view_matrix_inv = pyrr.matrix44.inverse(self.view_matrix)
        self.projection_matrix_inv = pyrr.matrix44.inverse(self.projection_matrix)

    def calculate_projection_matrix(self, width: float, height: float) -> None:
        """Calculates the projection matrix to get from world to camera space.

        :param width: Width of the opengl widget.
        :param height: Height of the opengl widget.
        """
        self.projection_matrix = pyrr.matrix44.create_perspective_projection_matrix(
            self.fov,
            width / height,
            0.1,
            100,
            dtype=np.float32,
        )

    def reset(self, width: float, height: float) -> None:
        """Resets the camera."""
        self.width = width
        self.height = height
        self.position = pyrr.Vector3([1.0, 0.0, 0.0], dtype=np.float32)
        self.up_vector = pyrr.Vector3([0.0, 1.0, 0.0], dtype=np.float32)
        self.right_vector = pyrr.Vector3([0.0, 0.0, -1.0], dtype=np.float32)
        self.distance_from_target = 5.0
        self.zoom_sensitivity = 0.15
        self.projection_matrix = None
        self.calculate_projection_matrix(self.width, self.height)

        self.rotation = pyrr.Quaternion()
        self.last_rotation = self.rotation
        self.translation = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        self.last_translation = self.translation
        self.position *= self.distance_from_target
        self.target = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        self.initial_target = self.target
        self.initial_position = pyrr.Vector3(
            pyrr.vector3.normalize(self.position),
            dtype=np.float32,
        )
        self.initial_up_vector = self.up_vector
        self.initial_right_vector = self.right_vector

        self.view_matrix = pyrr.matrix44.create_look_at(
            self.position,
            self.target,
            self.up_vector,
            dtype=np.float32,
        )
        self.view_matrix_inv = pyrr.matrix44.inverse(self.view_matrix)
        self.projection_matrix_inv = pyrr.matrix44.inverse(self.projection_matrix)

    def set_distance_from_target(self, num_steps: int) -> None:
        """Set the distance between the camera and its target.

        :param zoom: Factor that is multiplied with the normalized camera position vector and the current distance
            between the camera and the target.
        """
        zoom_factor = 1.0
        zoom_factor += num_steps * 1  # Empirical value to control zoom sensitivity
        zoom_factor = max(
            0.1,
            zoom_factor,
        )  # Limit zoom factor to avoid zooming too far
        self.distance_from_target += zoom_factor * (np.sign(zoom_factor - 1)) * self.zoom_sensitivity
        self.distance_from_target = max(self.distance_from_target, 1.0)

    def update(self, save: bool = False) -> None:
        """Updates the camera position and orientation."""
        self.up_vector = self.rotation * self.initial_up_vector
        self.right_vector = self.rotation * self.initial_right_vector
        self.position = self.rotation * self.initial_position * self.distance_from_target + self.translation
        self.position = np.array(self.position, dtype=np.float32)
        self.target = self.initial_target + self.translation
        if save:
            self.last_rotation = self.rotation
            self.last_translation = self.translation
        self.view_matrix = pyrr.matrix44.create_look_at(
            self.position,
            self.target,
            self.up_vector,
            dtype=np.float32,
        )
        self.view_matrix_inv = pyrr.matrix44.inverse(self.view_matrix)

    def set_translation_vector(
        self,
        old_mouse_position: np.ndarray,
        mouse_position: np.ndarray,
    ) -> None:
        """Calculates the translation matrix using the normalized mouse positions.

        :param old_mouse_position: Old normalized x and y coordinate of the mouse position on the opengl widget.
        :param mouse_position: New normalized x and y coordinate of the mouse position on the opengl widget.
        """
        x_translation = -(mouse_position[0] - old_mouse_position[0])
        y_translation = -(mouse_position[1] - old_mouse_position[1])
        self.translation = self.right_vector * x_translation + self.up_vector * y_translation + self.last_translation

    def set_rotation_quaternion(
        self,
        old_mouse_position: np.ndarray,
        new_mouse_position: np.ndarray,
    ) -> None:
        """Calculates the rotation quaternion using the normalized mouse positions.

        :param old_mouse_position: Old normalized x and y coordinate of the mouse position on the opengl widget.
        :param new_mouse_position: New normalized x and y coordinate of the mouse position on the opengl widget.
        """

        def calculate_arcball_point(x: float, y: float) -> np.ndarray:
            """Calculates the x, y, and z on the surface of an invisible sphere.

            :param x: Normalized x coordinate.
            :param y: Normalized y coordinate.
            :return: x, y, and z on the surface of an invisible sphere.
            """
            z = x
            squared_sum = z**2 + y**2
            if squared_sum <= 1:
                x = np.sqrt(1 - squared_sum)
            else:
                x = 0.0
                length = np.sqrt(squared_sum)
                z /= length
                y /= length
            return np.array([x, y, -z], dtype=np.float32)

        previous_arcball_point = calculate_arcball_point(
            old_mouse_position[0],
            old_mouse_position[1],
        )
        current_arcball_point = calculate_arcball_point(
            new_mouse_position[0],
            new_mouse_position[1],
        )

        tolerance_parallel = 1e-5
        if np.linalg.norm(previous_arcball_point - current_arcball_point) > tolerance_parallel:
            rotation_axis = np.cross(current_arcball_point, previous_arcball_point)
            rotation_axis = pyrr.vector3.normalize(rotation_axis)
            rotation_angle = np.arccos(
                np.clip(np.dot(previous_arcball_point, current_arcball_point), -1, 1),
            )

            self.rotation = self.last_rotation * pyrr.Quaternion.from_axis_rotation(
                rotation_axis,
                rotation_angle,
            )
        else:
            self.rotation = self.last_rotation
