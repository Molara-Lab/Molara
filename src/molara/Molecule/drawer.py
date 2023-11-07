"""Contains the Drawer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pyrr

from molara.Rendering.cylinder import Cylinder, calculate_cylinder_model_matrix
from molara.Rendering.sphere import Sphere

if TYPE_CHECKING:
    from molara.Molecule.atom import Atom


class Drawer:
    """Creates a Drawer object."""

    def __init__(self, atoms: list[Atom], bonds: np.ndarray) -> None:
        """Creates a Drawer object."""
        self.subdivisions_sphere = 15
        self.subdivisions_cylinder = 20
        self.sphere = Sphere(self.subdivisions_sphere)
        self.cylinder = Cylinder(self.subdivisions_cylinder)
        self.sphere_model_matrices = np.array([], dtype=np.float32)
        self.sphere_colors = np.array([], dtype=np.float32)
        self.cylinder_model_matrices = np.array([], dtype=np.float32)
        self.cylinder_colors = np.array([], dtype=np.float32)
        self.atoms = atoms
        self.bonds = bonds
        self.set_atom_model_matrices()
        self.set_cylinder_model_matrices()

    def set_atoms(self, atoms: list[Atom]) -> None:
        """Sets the atoms to be displayed.

        :param atoms: List of atoms to be displayed.
        :return:
        """
        self.atoms = atoms

    def reset_atom_model_matrices(self) -> None:
        """Resets the model matrices for the spheres.

        :return:
        """
        self.sphere_model_matrices = np.array([], dtype=np.float32)

    def reset_cylinders_model_matrices(self) -> None:
        """Resets the model matrices for the cylinders.

        :return:
        """
        self.cylinder_model_matrices = np.array([], dtype=np.float32)

    def set_cylinder_model_matrices(self) -> None:
        """Sets the model matrices for the cylinders.

        :return:
        """
        self.reset_cylinders_model_matrices()
        for bond in self.bonds:
            if bond[0] != -1:
                model_matrix = calculate_bond_cylinders_model_matrix(
                    self.atoms[bond[0]],
                    self.atoms[bond[1]],
                )
                # print(model_matrix)
                colors_1 = np.array(self.atoms[bond[0]].cpk_color)
                colors_2 = np.array(self.atoms[bond[1]].cpk_color)
                if self.cylinder_model_matrices.shape[0] == 0:
                    self.cylinder_model_matrices = model_matrix
                    self.cylinder_colors = np.array([colors_1], dtype=np.float32)
                    self.cylinder_colors = np.concatenate(
                        (self.cylinder_colors, np.array([colors_2], dtype=np.float32)),
                    )
                else:
                    self.cylinder_model_matrices = np.concatenate(
                        (self.cylinder_model_matrices, model_matrix),
                    )
                    self.cylinder_colors = np.concatenate(
                        (self.cylinder_colors, np.array([colors_1], dtype=np.float32)),
                    )
                    self.cylinder_colors = np.concatenate(
                        (self.cylinder_colors, np.array([colors_2], dtype=np.float32)),
                    )

    def set_atom_model_matrices(self) -> None:
        """Sets the model matrices for the spheres.

        :return:
        """
        self.reset_atom_model_matrices()
        for atom in self.atoms:
            if self.sphere_model_matrices.shape[0] == 0:
                self.sphere_model_matrices = calculate_atom_model_matrix(atom)
                self.sphere_colors = np.array([atom.cpk_color], dtype=np.float32)
            else:
                self.sphere_model_matrices = np.concatenate(
                    (
                        self.sphere_model_matrices,
                        calculate_atom_model_matrix(atom),
                    ),
                )
                self.sphere_colors = np.concatenate(
                    (self.sphere_colors, np.array([atom.cpk_color], dtype=np.float32)),
                )


def calculate_atom_model_matrix(atom: Atom) -> np.ndarray:
    """Calculates the model matrix for an atom displayed as a sphere.

    :param atom: Atom
    :return: Model matrix for the sphere.
    """
    # Calculate the translation matrix to translate the sphere to the correct position.
    translation_matrix = pyrr.matrix44.create_from_translation(
        pyrr.Vector3(atom.position),
    )
    # Calculate the scale matrix to scale the sphere to the correct size.
    scale_matrix = pyrr.matrix44.create_from_scale(
        pyrr.Vector3([atom.vdw_radius / 6] * 3),
    )
    # Return the model matrix for the sphere.
    return np.array(
        [np.array(scale_matrix @ translation_matrix, dtype=np.float32)],
        dtype=np.float32,
    )


def calculate_bond_cylinders_model_matrix(atom1: Atom, atom2: Atom) -> np.ndarray:
    """Calculates the model matrix for a cylinder between two atoms.

    :param atom1: Atom1
    :param atom2: Atom2
    :return: Model matrix for the cylinder between atom1 and atom2.
    """
    difference = atom1.position - atom2.position
    # Calculate the length of the cylinder.
    length = float(np.linalg.norm(difference))
    mid_point = (atom1.position + atom2.position) / 2
    # calculate the point 1 quarter between the 2 atoms
    position_1 = mid_point - difference / 4
    # calculate the point 3 quarter between the 2 atoms
    position_2 = mid_point + difference / 4

    mat1 = calculate_cylinder_model_matrix(position_1, 0.15, length, difference)
    mat2 = calculate_cylinder_model_matrix(position_2, 0.15, length, difference)
    return np.array(
        [
            mat2,
            mat1,
        ],
        dtype=np.float32,
    )
