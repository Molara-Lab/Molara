"""Contains the Drawer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.Rendering.cylinder import Cylinder, calculate_cylinder_model_matrix
from molara.Rendering.matrices import (
    calculate_model_matrices,
    calculate_rotation_matrices,
    calculate_scale_matrices,
    calculate_translation_matrices,
)
from molara.Rendering.sphere import (
    Sphere,
)
from molara.Tools.mathtools import norm

if TYPE_CHECKING:
    from molara.Molecule.atom import Atom

__copyright__ = "Copyright 2024, Molara"


class Drawer:
    """Creates a Drawer object."""

    def __init__(self, atoms: list[Atom], bonds: np.ndarray, draw_bonds: bool) -> None:
        """Creates a Drawer object."""
        self.subdivisions_sphere = 15
        self.subdivisions_cylinder = 20
        self.sphere = Sphere(self.subdivisions_sphere)
        self.cylinder = Cylinder(self.subdivisions_cylinder)
        self.sphere_model_matrices = np.array([], dtype=np.float32)
        self.sphere_translation_matrices: list | np.ndarray = []
        self.sphere_scale_matrices: list | np.ndarray = []
        self.cylinder_scale_matrices: list | np.ndarray = []
        self.cylinder_rotation_matrices: list | np.ndarray = []
        self.cylinder_translation_matrices: list | np.ndarray = []
        self.cylinder_model_matrices = np.array([], dtype=np.float32)
        self.cylinder_colors: np.ndarray = np.array([], dtype=np.float32)
        self.atoms = atoms
        self.bonds = bonds
        self.atom_positions: list | np.ndarray = []
        self.atom_colors: np.ndarray = np.array([], dtype=np.float32)
        self.atom_scales: list | np.ndarray = []
        self.cylinder_positions: list | np.ndarray = []
        self.cylinder_directions: list | np.ndarray = []
        self.cylinder_dimensions: list | np.ndarray = []
        self.set_atom_colors()
        self.set_atom_positions()
        self.set_atom_scales()
        self.set_atom_scale_matrices()
        self.set_atom_translation_matrices()
        self.set_atom_model_matrices()

        if self.bonds[0, 0] != -1 and draw_bonds:
            self.set_cylinder_props()
            self.set_cylinder_scale_matrices()
            self.set_cylinder_rotation_matrices()
            self.set_cylinder_translation_matrices()
            self.set_cylinder_model_matrices()

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
        for i, atom in enumerate(self.atoms):
            if i != 0:
                self.atom_colors = np.concatenate(
                    (self.atom_colors, np.array([atom.cpk_color], dtype=np.float32)),
                )
            else:
                self.atom_colors = np.array([self.atoms[0].cpk_color], dtype=np.float32)
        self.atom_colors = np.array(self.atom_colors, dtype=np.float32)

    def set_cylinder_props(self) -> None:
        """Sets the colors of the bonds (cylinders).

        :return:
        """
        self.cylinder_colors = np.array([], dtype=np.float32)
        self.cylinder_positions = []
        self.cylinder_directions = []
        self.cylinder_dimensions = []
        i = 0
        for bond in self.bonds:
            if bond[0] != -1:
                radius = 0.075
                difference = self.atoms[bond[0]].position - self.atoms[bond[1]].position
                # Calculate the length of the cylinder.
                length = float(norm(difference)) / 2
                mid_point = (self.atoms[bond[0]].position + self.atoms[bond[1]].position) / 2
                # calculate the point 1 quarter between the 2 atoms
                position_1 = mid_point + difference / 4
                # calculate the point 3 quarter between the 2 atoms
                position_2 = mid_point - difference / 4
                self.cylinder_positions.append(position_1)
                self.cylinder_positions.append(position_2)
                self.cylinder_directions.append(difference)
                self.cylinder_dimensions.append([radius, length, radius])
                if i != 0:
                    self.cylinder_colors = np.concatenate(
                        (
                            self.cylinder_colors,
                            np.array([self.atoms[bond[0]].cpk_color], dtype=np.float32),
                            np.array([self.atoms[bond[1]].cpk_color], dtype=np.float32),
                        ),
                    )
                else:
                    self.cylinder_colors = np.array(
                        [
                            self.atoms[bond[0]].cpk_color,
                            self.atoms[bond[1]].cpk_color,
                        ],
                        dtype=np.float32,
                    )
                i += 1

        self.cylinder_colors = np.array(self.cylinder_colors, dtype=np.float32)
        self.cylinder_positions = np.array(self.cylinder_positions, dtype=np.float32)
        self.cylinder_directions = np.array(self.cylinder_directions, dtype=np.float64)
        self.cylinder_dimensions = np.array(self.cylinder_dimensions, dtype=np.float32)

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
        self.atom_colors = np.array([], dtype=np.float32)

    def set_cylinder_model_matrices(self) -> None:
        """Sets the model matrices for the cylinders.

        :return:
        """
        self.reset_cylinders_model_matrices()
        self.cylinder_model_matrices = calculate_model_matrices(
            self.cylinder_translation_matrices,
            self.cylinder_scale_matrices,
            self.cylinder_rotation_matrices,
            cylinder=True,
        )

    def set_cylinder_translation_matrices(self) -> None:
        """Sets the translation matrices for the spheres.

        :return:
        """
        self.cylinder_translation_matrices = calculate_translation_matrices(
            np.array(self.cylinder_positions),
        )

    def set_cylinder_scale_matrices(self) -> None:
        """Sets the translation matrices for the cylinders.

        :return:
        """
        self.cylinder_scale_matrices = calculate_scale_matrices(
            np.array(self.cylinder_dimensions),
        )

    def set_cylinder_rotation_matrices(self) -> None:
        """Sets the rotation matrices for the cylinders.

        :return:
        """
        self.cylinder_rotation_matrices = calculate_rotation_matrices(
            np.array(self.cylinder_directions),
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
