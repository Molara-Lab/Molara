from __future__ import annotations

from typing import Optional

import numpy as np
import pyrr


class Camera:
    """Creates a Camera object.

    :param width: Width of the opengl widget.
    :param height: Height of the opengl widget.
    """

    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        self.reference_position = pyrr.Vector3([1.0, 0.0, 0.0], dtype=np.float32)
        self.position = pyrr.Vector3([1.0, 0.0, 0.0], dtype=np.float32)
        self.target = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        self.up_vector = pyrr.Vector3([0.0, 1.0, 0.0], dtype=np.float32)
        self.distance_from_target = 5.0
        self.zoom_factor = 0.05

        self.projection_matrix = None
        self.calculate_projection_matrix(self.width, self.height)

        self.current_rotation = pyrr.Quaternion()
        self.last_rotation = pyrr.Quaternion()
        self.position *= self.distance_from_target

    def calculate_projection_matrix(self, width: float, height: float) -> None:
        """Calculates the projection matrix to get from world to camera space.

        :param width: Width of the opengl widget.
        :param height: Height of the opengl widget.
        """
        self.projection_matrix = pyrr.matrix44.create_perspective_projection_matrix(45, width / height, 0.1, 100)

    def reset(self, width: float, height: float) -> None:
        """Resets the camera."""
        self.__init__(width, height)

    def calc_distance_from_target(self, zoom: float) -> None:
        """Set the distance between the camera and its target.

        :param zoom: Factor that is multiplied with the normalized camera position vector and the current distance
            between the camera and the target.
        """
        self.distance_from_target += self.zoom_factor * zoom * (np.sign(zoom-1))
        if self.distance_from_target < 1.0:
            self.distance_from_target = 1.0
        self.set_distance_from_target()
    def set_distance_from_target(self) -> None:
        """Set the distance between the camera and its target.

        :param distance: Distance between the camera and its target.
        """
        self.position = pyrr.vector3.normalize(self.position) * self.distance_from_target

    def calculate_camera_translation(self, old_mouse_position: float, mouse_position: float, save: bool = False) -> None:
        """
        Calculates the camera position according to arcball movement using the normalized mouse positions.
        :param old_mouse_position: Old normalized x and y coordinate of the mous position on the opengl widget.
        :param new_mouse_position: New normalized x and y coordinate of the mous position on the opengl widget.
        :param save: If given the current rotation quaternion is saved.
        """
    def calculate_camera_orientation(
        self, old_mouse_position: float, new_mouse_position: float, save: Optional[bool] = False
    ) -> None:
        """Calculates the camera position according to arcball movement using the normalized mouse positions.

        :param old_mouse_position: Old normalized x and y coordinate of the mous position on the opengl widget.
        :param new_mouse_position: New normalized x and y coordinate of the mous position on the opengl widget.
        :param save: If given the current rotation quaternion is saved.
        """

        def calculate_arcball_point(x: float, y: float) -> np.ndarray:
            """Calculates the x, y, and z on the surface of an invisible sphere using only the x and y coordinates and
            using the positive z solution.

            :param x: Normalized x coordinate.
            :param y: Normalized y coordinate.
            :return: x, y, and z on the surface of an invisible sphere.
            """
            z = x
            squared_sum = z**2 + y**2
            if squared_sum <= 1.0:
                x = np.sqrt(1.0 - squared_sum)
            else:
                x = 0.0
                length = np.sqrt(squared_sum)
                z /= length
                y /= length
            return np.array([x, y, -z], dtype=np.float32)

        self.position = pyrr.vector3.normalize(self.position)

        previous_arcball_point = calculate_arcball_point(old_mouse_position[0], old_mouse_position[1])
        current_arcball_point = calculate_arcball_point(new_mouse_position[0], new_mouse_position[1])

        if np.linalg.norm(previous_arcball_point - current_arcball_point) < 1e-3:
            rotation_axis = np.array([1, 0, 0], dtype=np.float32)
            rotation_angle = 0.0
        else:
            rotation_axis = np.cross(current_arcball_point, previous_arcball_point)
            rotation_angle = np.arccos(np.clip(np.dot(previous_arcball_point, current_arcball_point), -1, 1))

        self.current_rotation = pyrr.Quaternion.from_axis_rotation(rotation_axis, rotation_angle)
        rotation = self.last_rotation * self.current_rotation

        self.up_vector = rotation * pyrr.Vector3([0.0, 1.0, 0.0], dtype=np.float32)
        self.position = (
            pyrr.vector3.normalize(rotation * (self.reference_position - self.target) + self.target)
        )

        self.set_distance_from_target()

        if save:
            self.last_rotation = rotation
