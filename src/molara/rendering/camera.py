"""Camera class for the opengl widget."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

import numpy as np
import numpy.typing as npt
import pyrr

__copyright__ = "Copyright 2024, Molara"


class Camera:
    """Creates a Camera object."""

    def __init__(self, width: float, height: float) -> None:
        """Create a Camera object.

        :param width: Width of the opengl widget.
        :param height: Height of the opengl widget.
        """
        self.fov = 45.0
        self.width = width
        self.height = height
        self.near = 0.1
        self.far = 720.0
        self.position = pyrr.Vector3([1.0, 0.0, 0.0], dtype=np.float32)
        self.up_vector = pyrr.Vector3([0.0, 1.0, 0.0], dtype=np.float32)
        self.right_vector = pyrr.Vector3([0.0, 0.0, -1.0], dtype=np.float32)
        self.distance_from_target = 5.0
        self.zoom_sensitivity = 0.15
        self.projection_matrix: npt.ArrayLike | None = None
        self.orthographic_projection = False  # specify whether orthographic projection shall be used
        self.calculate_projection_matrix()

        self.rotation = pyrr.Quaternion()
        self.translation = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        self.position *= self.distance_from_target
        self.target = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)

        self.last_rotation = self.rotation
        self.last_translation = self.translation
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

    def calculate_projection_matrix(self) -> None:
        """Calculate the projection matrix to get from world to camera space."""
        width, height = self.width, self.height  # Width and height of the opengl widget
        if self.orthographic_projection:
            # calculate width and height of the clipping plane
            # such that it matches the field of view in the perspective projection
            h = self.distance_from_target * np.tan(np.radians(self.fov / 2))
            w = h * width / height
            self.projection_matrix = pyrr.matrix44.create_orthogonal_projection_matrix(
                -w,
                w,
                -h,
                h,
                self.near,
                self.far,
                dtype=np.float32,
            )
            return
        self.projection_matrix = pyrr.matrix44.create_perspective_projection_matrix(
            self.fov,
            width / height,
            self.near,
            self.far,
            dtype=np.float32,
        )
        self.projection_matrix_inv = pyrr.matrix44.inverse(self.projection_matrix)

    def reset(
        self,
        width: float,
        height: float,
        dy_struct: float | None = None,
        dz_struct: float | None = None,
    ) -> None:
        """Reset the camera.

        :param width: Width of the opengl widget.
        :param height: Height of the opengl widget.
        :param dy_struct: extent of the structure in y-direction
        :param dz_struct: extent of the structure in z-direction
        """
        self.width = width
        self.height = height

        # set distance from target such that the structure fits into the view
        # equation to be solved:
        # tan(fov [°] / 2)) * distance_from_target = dy / 2
        # if vertical (y) length is limiting, dy = dy_struct. Otherwise, dy = height/width*dz_struct
        # z-axis is horizontal by default.
        distance_from_target = None
        if dy_struct and dz_struct:
            extra_space_factor = 1.5
            dy = dy_struct if dy_struct * self.width > dz_struct * self.height else dz_struct * self.height / self.width
            distance_from_target = extra_space_factor * dy / (2 * np.tan(np.radians(self.fov / 2)))

        self.set_position(
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, -1.0],
            distance_from_target,
        )

    def set_position(
        self,
        position: list[float],
        up_vector: list[float],
        right_vector: list[float],
        distance_from_target: float | None = None,
    ) -> None:
        """Set camera position and orientation.

        :param position: coordinates of camera position
        :param up_vector: vector indicating which direction is upward for the camera
        :param right_vector: vector indicating which direction is right for the camera
        :param distance_from_target: distance between the camera and its target
        """
        self.position = pyrr.Vector3(position, dtype=np.float32)
        self.up_vector = pyrr.Vector3(up_vector, dtype=np.float32)
        self.right_vector = pyrr.Vector3(right_vector, dtype=np.float32)
        self.distance_from_target = distance_from_target if distance_from_target else self.distance_from_target
        self.projection_matrix = None
        self.calculate_projection_matrix()

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

    def set_rotation(self, axis: Literal["x", "y", "z"]) -> None:
        """Align the camera rotation with one of the major axes ("x", "y", "z").

        :param axis: specifies along which axis camera view shall be aligned.
        """
        self.initial_position = pyrr.Vector3([1.0, 0.0, 0.0], dtype=np.float32)
        self.initial_up_vector = pyrr.Vector3([0.0, 1.0, 0.0], dtype=np.float32)
        self.initial_right_vector = pyrr.Vector3([0.0, 0.0, -1.0], dtype=np.float32)
        if axis == "x":
            rotation_axis = pyrr.Vector3([0, 1, 0], dtype=np.float32)
            rotation_angle = 0.0
        elif axis == "y":
            rotation_axis = pyrr.Vector3([0, 0, 1], dtype=np.float32)
            rotation_angle = np.pi / 2.0
        elif axis == "z":
            rotation_axis = pyrr.Vector3([0, 1, 0], dtype=np.float32)
            rotation_angle = np.pi / 2.0
        self.rotation = pyrr.Quaternion() * pyrr.Quaternion.from_axis_rotation(
            rotation_axis,
            rotation_angle,
        )
        self.last_rotation = self.rotation
        self.update()

    def center_coordinates(self) -> None:
        """Reset camera translation such that center of structure is in center of view."""
        self.translation = pyrr.Vector3([0.0, 0.0, 0.0], dtype=np.float32)
        self.last_translation = self.translation
        self.update()

    def set_distance_from_target(self, num_steps: int) -> None:
        """Set the distance between the camera and its target.

        :param num_steps: Number of zoom steps. From this, factor is calculated that is multiplied
            with the normalized camera position vector and the current distance
            between the camera and the target.
        """
        zoom_factor = 1.0
        zoom_factor += num_steps * 1  # Empirical value to control zoom sensitivity
        zoom_factor = max(
            0.1,
            zoom_factor,
        )  # Limit zoom factor to avoid zooming too far
        self.distance_from_target += np.log10(zoom_factor * self.zoom_sensitivity) * np.sign(zoom_factor - 1)
        self.distance_from_target = max(self.distance_from_target, 1.0)

    def toggle_projection(self) -> None:
        """Toggle between perspective and orthographic projection."""
        self.orthographic_projection = not self.orthographic_projection
        self.calculate_projection_matrix()

    def update(self, save: bool = False) -> None:
        """Update the camera position and orientation.

        :param save: specifies whether updated camera orientation shall be saved as new reference
        """
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
        if self.orthographic_projection:
            self.calculate_projection_matrix()

    def set_translation_vector(
        self,
        old_mouse_position: np.ndarray,
        mouse_position: np.ndarray,
    ) -> None:
        """Calculate the translation matrix using the normalized mouse positions.

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
        """Calculate the rotation quaternion using the normalized mouse positions.

        :param old_mouse_position: Old normalized x and y coordinate of the mouse position on the opengl widget.
        :param new_mouse_position: New normalized x and y coordinate of the mouse position on the opengl widget.
        """

        def calculate_arcball_point(x: float, y: float) -> np.ndarray:
            """Calculate the x, y, and z on the surface of an invisible sphere.

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

    def export_settings(self, file_name: str) -> None:
        """Export camera settings to .npz file.

        :param file_name: Name of the file to which camera settings are saved.
        """
        settings = {
            "orthographic_projection": self.orthographic_projection,
            "fov": self.fov,
            "width": self.width,
            "height": self.height,
            "zoom_sensitivity": self.zoom_sensitivity,
            "distance_from_target": self.distance_from_target,
            "position": self.position.tolist(),
            "up_vector": self.up_vector.tolist(),
            "right_vector": self.right_vector.tolist(),
            "target": self.target.tolist(),
            "translation": self.translation.tolist(),
            "initial_position": self.initial_position.tolist(),
            "initial_up_vector": self.initial_up_vector.tolist(),
            "initial_right_vector": self.initial_right_vector.tolist(),
            "initial_target": self.initial_target.tolist(),
            "last_translation": self.last_translation.tolist(),
            "rotation": self.rotation.tolist(),
            "last_rotation": self.last_rotation.tolist(),
        }
        if not file_name.endswith(".json"):
            file_name += ".json"
        with Path(file_name).open("w") as file:
            json.dump(settings, file, indent=4)

    def import_settings(self, file_name: str) -> None:
        """Import camera settings from .npz file.

        :param file_name: Name of the file from which camera settings are loaded.
        """
        if not file_name.endswith(".json"):
            # Show warning
            return
        with Path(file_name).open() as file:
            data = json.load(file)
        self.orthographic_projection = data["orthographic_projection"]
        self.fov = data["fov"]
        self.width = data["width"]
        self.height = data["height"]
        self.zoom_sensitivity = data["zoom_sensitivity"]
        self.set_position(
            data["position"],
            data["up_vector"],
            data["right_vector"],
            data["distance_from_target"],
        )
        self.initial_position = pyrr.Vector3(data["initial_position"], dtype=np.float32)
        self.initial_up_vector = pyrr.Vector3(data["initial_up_vector"], dtype=np.float32)
        self.initial_right_vector = pyrr.Vector3(data["initial_right_vector"], dtype=np.float32)
        self.target = pyrr.Vector3(data["target"], dtype=np.float32)
        self.initial_target = pyrr.Vector3(data["initial_target"], dtype=np.float32)
        self.translation = pyrr.Vector3(data["translation"], dtype=np.float32)
        self.last_translation = pyrr.Vector3(data["last_translation"], dtype=np.float32)
        self.rotation = pyrr.Quaternion(data["rotation"])
        self.last_rotation = pyrr.Quaternion(data["last_rotation"])
        self.calculate_projection_matrix()
        self.update()
