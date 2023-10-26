from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pyrr

from molara.Rendering.cylinder import Cylinders
from molara.Rendering.sphere import Spheres

if TYPE_CHECKING:
    from molara.Molecule.atom import Atom


class Drawer:
    def __init__(self, atoms: list[Atom], bonds: np.ndarray) -> None:
        self.subdivisions_sphere = 15
        self.subdivisions_cylinder = 20
        self.unique_spheres: list[Spheres] = []
        self.unique_spheres_mapping: list[int] = [-1 for _ in range(119)]
        self.unique_cylinders: list[Cylinders] = []
        self.unique_cylinders_mapping: list[int] = [-1 for _ in range(119)]
        self.atoms = atoms
        self.bonds = bonds
        self.set_sphere_model_matrices()
        self.set_cylinder_model_matrices()

    def set_atoms(self, atoms: list[Atom]) -> None:
        """Sets the atoms to be displayed.
        :param atoms: List of atoms to be displayed.
        :return:
        """
        self.atoms = atoms

    def reset_spheres_model_matrices(self) -> None:
        """Resets the model matrices for the spheres.
        :return:
        """
        self.unique_spheres = []
        self.unique_spheres_mapping = [-1 for _ in range(119)]

    def reset_cylinders_model_matrices(self) -> None:
        """Resets the model matrices for the cylinders.
        :return:
        """
        self.unique_cylinders = []
        self.unique_cylinders_mapping = [-1 for _ in range(119)]

    def set_cylinder_model_matrices(self) -> None:
        """Sets the model matrices for the cylinders.
        :return:
        """
        self.reset_cylinders_model_matrices()
        for atom in self.atoms:
            idx = self.unique_cylinders_mapping[atom.atomic_number]
            if idx == -1:
                self.unique_cylinders.append(Cylinders(atom.cpk_color, self.subdivisions_cylinder))
                self.unique_cylinders_mapping[atom.atomic_number] = len(self.unique_cylinders) - 1
        for bond in self.bonds:
            idx1 = self.unique_cylinders_mapping[self.atoms[bond[0]].atomic_number]
            idx2 = self.unique_cylinders_mapping[self.atoms[bond[1]].atomic_number]
            if bond[0] != -1:
                model_matrices = calculate_bond_cylinders_model_matrix(self.atoms[bond[0]], self.atoms[bond[1]])
                if self.unique_cylinders[idx1].model_matrices.shape[0] == 0:
                    self.unique_cylinders[idx1].model_matrices = model_matrices[0]
                else:
                    self.unique_cylinders[idx1].model_matrices = np.concatenate(
                        (self.unique_cylinders[idx1].model_matrices, model_matrices[0]),
                    )
                if self.unique_cylinders[idx2].model_matrices.shape[0] == 0:
                    self.unique_cylinders[idx2].model_matrices = model_matrices[1]
                else:
                    self.unique_cylinders[idx2].model_matrices = np.concatenate(
                        (self.unique_cylinders[idx2].model_matrices, model_matrices[1]),
                    )

    def set_sphere_model_matrices(self) -> None:
        """Sets the model matrices for the spheres.
        :return:
        """
        self.reset_spheres_model_matrices()
        for atom in self.atoms:
            idx = self.unique_spheres_mapping[atom.atomic_number]
            if idx == -1:
                self.unique_spheres.append(Spheres(atom.cpk_color, self.subdivisions_sphere))
                self.unique_spheres[-1].model_matrices = calculate_sphere_model_matrix(atom)
                self.unique_spheres_mapping[atom.atomic_number] = len(self.unique_spheres) - 1
            else:
                self.unique_spheres[idx].model_matrices = np.concatenate(
                    (self.unique_spheres[idx].model_matrices, calculate_sphere_model_matrix(atom)),
                )


def calculate_sphere_model_matrix(atom: Atom) -> np.ndarray:
    """Calculates the model matrix for an atom displayed as a sphere.
    :param atom: Atom
    :return: Model matrix for the sphere.
    """
    # Calculate the translation matrix to translate the sphere to the correct position.
    translation_matrix = pyrr.matrix44.create_from_translation(pyrr.Vector3(atom.position))
    # Calculate the scale matrix to scale the sphere to the correct size.
    scale_matrix = pyrr.matrix44.create_from_scale(pyrr.Vector3([atom.vdw_radius / 6] * 3))
    # Return the model matrix for the sphere.
    return np.array([np.array(scale_matrix @ translation_matrix, dtype=np.float32)], dtype=np.float32)


def calculate_bond_cylinders_model_matrix(atom1: Atom, atom2: Atom) -> np.ndarray:
    """Calculates the model matrix for a cylinder between two atoms.
    :param atom1: Atom1
    :param atom2: Atom2
    :return: Model matrix for the cylinder between atom1 and atom2.
    """
    difference = atom1.position - atom2.position
    # Calculate the length of the cylinder.
    length = np.linalg.norm(difference)
    mid_point = (atom1.position + atom2.position) / 2
    # calculate the point 1 quarter between the 2 atoms
    position_1 = mid_point - difference / 4
    # calculate the point 3 quarter between the 2 atoms
    position_2 = mid_point + difference / 4
    # Calculate the rotation axis to rotate the cylinder to the correct orientation.
    y_axis = np.array([0, 1, 0], dtype=np.float32)
    difference = difference / np.linalg.norm(difference)
    if abs(y_axis @ difference) != 1:
        rotation_axis = np.cross(y_axis, difference)
        # Calculate the angle to rotate the cylinder to the correct orientation.
        rotation_angle = np.arccos(
            np.clip(
                np.dot(difference, y_axis) / (np.linalg.norm(difference)),
                -1,
                1,
            ),
        )
    else:
        rotation_axis = np.array([0, 0, 1], dtype=np.float32)
        rotation_angle = 0
    translation_matrix_1 = pyrr.matrix44.create_from_translation(pyrr.Vector3(position_1))
    translation_matrix_2 = pyrr.matrix44.create_from_translation(pyrr.Vector3(position_2))
    # Calculate the rotation matrix to rotate the cylinder to the correct orientation.
    rotation_matrix = pyrr.matrix44.create_from_axis_rotation(rotation_axis, rotation_angle)
    # Calculate the scale matrix to scale the cylinder to the correct length.
    scale = pyrr.Vector3([0.15] * 3)
    scale[1] = length / 2
    scale_matrix = pyrr.matrix44.create_from_scale(pyrr.Vector3(scale))
    # Return the model matrix for the cylinder.
    rotation_scale_matrix = scale_matrix @ rotation_matrix
    return np.array(
        [
            np.array([rotation_scale_matrix @ translation_matrix_2], dtype=np.float32),
            np.array([rotation_scale_matrix @ translation_matrix_1], dtype=np.float32),
        ],
        dtype=np.float32,
    )
