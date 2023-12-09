"""Contains the Drawer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.Rendering.cylinder import Cylinder, calculate_cylinder_model_matrix
from molara.Rendering.matrices import (
    calculate_model_matrices,
    calculate_scale_matrices,
    calculate_translation_matrices,
)
from molara.Rendering.sphere import (
    Sphere,
    calculate_sphere_model_matrix,
)
from molara.Tools.mathtools import norm

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
        self.sphere_translation_matrices: list = []
        self.sphere_scale_matrices: list = []
        self.cylinder_model_matrices = np.array([], dtype=np.float32)
        self.cylinder_colors = np.array([], dtype=np.float32)
        self.atoms = atoms
        self.bonds = bonds
        self.atom_positions: list = []
        self.atom_colors: list = []
        self.atom_scale: list = []
        self.set_atom_colors()
        self.set_atom_positions()
        self.set_atom_scales()
        self.set_cylinder_model_matrices()
        self.set_atom_scale_matrices()
        self.set_atom_translation_matrices()
        self.set_atom_model_matrices()

    def set_atoms(self, atoms: list[Atom]) -> None:
        """Sets the atoms to be displayed.

        :param atoms: List of atoms to be displayed.
        :return:
        """
        self.atoms = atoms
        self.set_atom_colors()
        self.set_atom_positions()

    def set_atom_colors(self) -> None:
        """Sets the colors of the atoms.

        :return:
        """
        self.atom_colors = []
        for atom in self.atoms:
            self.atom_colors.append(np.array([atom.cpk_color], dtype=np.float32))
        self.atom_colors = np.array(self.atom_colors, dtype=np.float32)

    def set_atom_positions(self) -> None:
        """Sets the positions of the atoms.

        :return:
        """
        self.atom_positions = []
        for atom in self.atoms:
            self.atom_positions.append(np.array(atom.position, dtype=np.float32))
        self.atom_positions = np.array(self.atom_positions, dtype=np.float32)

    def set_atom_scales(self) -> None:
        """Sets the positions of the atoms.

        :return:
        """
        self.atom_scales = []
        for atom in self.atoms:
            r = float(atom.vdw_radius / 6)
            self.atom_scales.append([r, r, r])
        self.atom_scales = np.array(self.atom_scales, dtype=np.float32)

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

    def reset_atom_colors(self) -> None:
        """Resets the colors for the spheres.

        :return:
        """
        self.atom_colors = []

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

    def set_atom_translation_matrices(self) -> None:
        """Sets the translation matrices for the spheres.

        :return:
        """
        self.sphere_translation_matrices = calculate_translation_matrices(
            np.array(self.atom_positions),
        )

    def set_atom_scale_matrices(self) -> None:
        """Sets the scale matrices for the spheres.

        :return:
        """
        self.sphere_scale_matrices = calculate_scale_matrices(
            np.array(self.atom_scales),
        )

    def set_atom_model_matrices(self) -> None:
        """Sets the model matrices for the spheres.

        :return:
        """
        self.reset_atom_model_matrices()
        self.sphere_model_matrices = calculate_model_matrices(
            np.array(self.sphere_translation_matrices),
            np.array(self.sphere_scale_matrices),
        )


def calculate_bond_cylinders_model_matrix(atom1: Atom, atom2: Atom) -> np.ndarray:
    """Calculates the model matrix for a cylinder between two atoms.

    :param atom1: Atom1
    :param atom2: Atom2
    :return: Model matrix for the cylinder between atom1 and atom2.
    """
    radius = 0.075
    difference = atom1.position - atom2.position
    # Calculate the length of the cylinder.
    length = float(norm(difference)) / 2
    mid_point = (atom1.position + atom2.position) / 2
    # calculate the point 1 quarter between the 2 atoms
    position_1 = mid_point - difference / 4
    # calculate the point 3 quarter between the 2 atoms
    position_2 = mid_point + difference / 4

    mat1 = calculate_cylinder_model_matrix(position_1, radius, length, difference)
    mat2 = calculate_cylinder_model_matrix(position_2, radius, length, difference)
    return np.array(
        [
            mat2,
            mat1,
        ],
        dtype=np.float32,
    )
