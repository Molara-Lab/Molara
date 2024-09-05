"""Contains the Drawer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.rendering.cylinder import Cylinder, calculate_cylinder_model_matrix
from molara.rendering.matrices import (
    calculate_model_matrices,
    calculate_rotation_matrices,
    calculate_scale_matrices,
    calculate_translation_matrices,
)
from molara.rendering.sphere import (
    Sphere,
)
from molara.tools.mathtools import norm

if TYPE_CHECKING:
    from molara.structure.atom import Atom

__copyright__ = "Copyright 2024, Molara"


NO_BONDS = np.array([[-1, -1]], dtype=np.int_)


class Drawer:
    """Creates a Drawer object."""

    def __init__(self, atoms: list[Atom], bonds: np.ndarray, draw_bonds: bool) -> None:
        """Create a Drawer object.

        :param atoms: list of atoms to be drawn
        :param bonds: list ids of bonded atoms
        :param draw_bonds: bool that specifies whether bonds shall be drawn (as cylinders)
        """
        self.subdivisions_sphere = 20
        self.subdivisions_cylinder = 20
        self.stick_mode = False
        self.color_scheme = "Jmol"

        self.sphere_scale = 1.0
        self.sphere_default_radius = 1.0 / 6
        self.cylinder_scale = 1.0
        self.cylinder_radius = 0.075

        self.sphere = Sphere(self.subdivisions_sphere)
        self.cylinder = Cylinder(self.subdivisions_cylinder)
        self.sphere_model_matrices = np.array([], dtype=np.float32)
        self.sphere_translation_matrices: list | np.ndarray = []
        self.sphere_scale_matrices: list | np.ndarray = []

        self.atom_positions: list | np.ndarray = []
        self.atom_colors: np.ndarray = np.array([], dtype=np.float32)
        self.atom_scales: list | np.ndarray = []
        self.update_atoms(atoms)

        self.cylinder_scale_matrices: list | np.ndarray = []
        self.cylinder_rotation_matrices: list | np.ndarray = []
        self.cylinder_translation_matrices: list | np.ndarray = []
        self.cylinder_model_matrices = np.array([], dtype=np.float32)
        self.cylinder_colors: list | np.ndarray = np.array([], dtype=np.float32)
        self.cylinder_positions: list | np.ndarray = []
        self.cylinder_directions: list | np.ndarray = []
        self.cylinder_dimensions: list | np.ndarray = []

        self.bonds = NO_BONDS
        self.update_bonds(bonds, draw_bonds)

    @property
    def has_bonds(self) -> bool:
        """Specifies whether drawer has been passed any bonds to draw."""
        return self.bonds[0][0] != -1

    def update_atoms(self, atoms: list[Atom] | None = None) -> None:
        """Update the bonds and/or bond matrices of the drawer."""
        if atoms is not None:
            self.atoms = atoms
            self.set_atom_colors()
            self.set_atom_positions()
            self.set_atom_scales()
            self.set_atom_scale_matrices()
        self.set_atom_translation_matrices()
        self.set_atom_model_matrices()

    def update_bonds(self, bonds: np.ndarray | None = None, draw_bonds: bool = True) -> None:
        """Update the bonds and/or bond matrices of the drawer."""
        self.draw_bonds = draw_bonds

        if bonds is not None:
            self.bonds = bonds

        if not self.draw_bonds:
            return

        if self.has_bonds:
            self.set_cylinder_props()
            if bonds is not None:
                self.set_cylinder_scale_matrices()
                self.set_cylinder_rotation_matrices()
            self.set_cylinder_translation_matrices()
            self.set_cylinder_model_matrices()

    def set_atoms(self, atoms: list[Atom]) -> None:
        """Set the atoms to be displayed.

        :param atoms: List of atoms to be displayed.
        """
        self.atoms = atoms
        self.set_atom_colors()
        self.set_atom_positions()

    def set_atom_colors(self) -> None:
        """Set the colors of the atoms."""
        self.atom_colors = np.array([atom.color[self.color_scheme] for atom in self.atoms], dtype=np.float32)

    def set_cylinder_dimensions(self) -> None:
        """Set the dimensions of the cylinders.

        It is important to note, that the radius ([:,1]) of the cylinders need not be changed!
        """
        self.cylinder_dimensions = np.array(self.cylinder_dimensions, dtype=np.float32)
        self.cylinder_dimensions[:, 0] = self.cylinder_radius * self.cylinder_scale
        self.cylinder_dimensions[:, 2] = self.cylinder_radius * self.cylinder_scale

    def set_cylinder_props(self) -> None:
        """Set the colors of the bonds (cylinders)."""
        self.cylinder_colors = []
        self.cylinder_positions = []
        self.cylinder_directions = []
        self.cylinder_dimensions = []
        radius = self.cylinder_radius * self.cylinder_scale

        for bond in self.bonds:
            if bond[0] == -1:
                continue

            atom1, atom2 = self.atoms[bond[0]], self.atoms[bond[1]]
            pos1, pos2 = atom1.position, atom2.position
            difference = pos1 - pos2
            # Calculate the length of the cylinder.
            length = float(norm(difference)) / 2
            mid_point = (pos1 + pos2) / 2
            # calculate the point 1 quarter between the 2 atoms
            pos_quarter1 = mid_point + difference / 4
            # calculate the point 3 quarter between the 2 atoms
            pos_quarter2 = mid_point - difference / 4
            self.cylinder_positions.append(pos_quarter1)
            self.cylinder_positions.append(pos_quarter2)
            self.cylinder_directions.append(difference)
            self.cylinder_dimensions.append([radius, length, radius])
            self.cylinder_colors += [
                np.array([atom1.color[self.color_scheme]], dtype=np.float32),
                np.array([atom2.color[self.color_scheme]], dtype=np.float32),
            ]

        self.cylinder_colors = np.array(self.cylinder_colors, dtype=np.float32)
        self.cylinder_positions = np.array(self.cylinder_positions, dtype=np.float32)
        self.cylinder_directions = np.array(self.cylinder_directions, dtype=np.float64)
        self.cylinder_dimensions = np.array(self.cylinder_dimensions, dtype=np.float32)

    def set_cylinder_colors(self) -> None:
        """Set the colors of the bonds (cylinders)."""
        self.cylinder_colors = []
        for bond in self.bonds:
            if bond[0] == -1:
                continue
            atom1, atom2 = self.atoms[bond[0]], self.atoms[bond[1]]
            self.cylinder_colors += [
                np.array([atom1.color[self.color_scheme]], dtype=np.float32),
                np.array([atom2.color[self.color_scheme]], dtype=np.float32),
            ]
        self.cylinder_colors = np.array(self.cylinder_colors, dtype=np.float32)

    def set_atom_positions(self) -> None:
        """Set the positions of the atoms."""
        self.atom_positions = np.array(
            [np.array(atom.position, dtype=np.float32) for atom in self.atoms],
            dtype=np.float32,
        )

    def set_atom_scales(self) -> None:
        """Set the scales of the atoms."""
        self.atom_scales = []
        scaling_factor = self.sphere_default_radius * self.sphere_scale
        if not self.stick_mode:
            self.atom_scales = np.array(
                [3 * [scaling_factor * atom.vdw_radius] for atom in self.atoms],
                dtype=np.float32,
            )
        else:
            self.atom_scales = np.array([3 * [scaling_factor] for _ in self.atoms], dtype=np.float32)

    def reset_atom_model_matrices(self) -> None:
        """Reset the model matrices for the spheres."""
        self.sphere_model_matrices = np.array([], dtype=np.float32)

    def reset_cylinders_model_matrices(self) -> None:
        """Reset the model matrices for the cylinders."""
        self.cylinder_model_matrices = np.array([], dtype=np.float32)

    def reset_atom_colors(self) -> None:
        """Reset the colors for the spheres."""
        self.atom_colors = np.array([], dtype=np.float32)

    def set_cylinder_model_matrices(self) -> None:
        """Set the model matrices for the cylinders."""
        self.reset_cylinders_model_matrices()
        self.cylinder_model_matrices = calculate_model_matrices(
            self.cylinder_translation_matrices,
            self.cylinder_scale_matrices,
            self.cylinder_rotation_matrices,
            cylinder=True,
        )

    def set_cylinder_translation_matrices(self) -> None:
        """Set the translation matrices for the spheres."""
        self.cylinder_translation_matrices = calculate_translation_matrices(
            np.array(self.cylinder_positions),
        )

    def set_cylinder_scale_matrices(self) -> None:
        """Set the translation matrices for the cylinders."""
        self.cylinder_scale_matrices = calculate_scale_matrices(
            np.array(self.cylinder_dimensions),
        )

    def set_cylinder_rotation_matrices(self) -> None:
        """Set the rotation matrices for the cylinders."""
        self.cylinder_rotation_matrices = calculate_rotation_matrices(
            np.array(self.cylinder_directions),
        )

    def set_atom_translation_matrices(self) -> None:
        """Set the translation matrices for the spheres."""
        self.sphere_translation_matrices = calculate_translation_matrices(
            np.array(self.atom_positions),
        )

    def set_atom_scale_matrices(self) -> None:
        """Set the scale matrices for the spheres."""
        self.sphere_scale_matrices = calculate_scale_matrices(
            np.array(self.atom_scales),
        )

    def set_atom_model_matrices(self) -> None:
        """Set the model matrices for the spheres."""
        self.reset_atom_model_matrices()
        self.sphere_model_matrices = calculate_model_matrices(
            np.array(self.sphere_translation_matrices),
            np.array(self.sphere_scale_matrices),
        )


def calculate_bond_cylinders_model_matrix(atom1: Atom, atom2: Atom) -> np.ndarray:
    """Calculate the model matrix for a cylinder between two atoms.

    :param atom1: first Atom
    :param atom2: second Atom
    :return: Model matrix for the cylinder between atom1 and atom2.
    """
    radius = 0.075
    difference = atom1.position - atom2.position
    # Calculate the length of the cylinder.
    length = float(norm(difference)) / 2
    mid_point = (atom1.position + atom2.position) / 2
    # calculate the point 1 quarter between the 2 atoms
    pos_quarter1 = mid_point - difference / 4
    # calculate the point 3 quarter between the 2 atoms
    pos_quarter2 = mid_point + difference / 4

    mat1 = calculate_cylinder_model_matrix(pos_quarter1, radius, length, difference)
    mat2 = calculate_cylinder_model_matrix(pos_quarter2, radius, length, difference)
    return np.array(
        [
            mat2,
            mat1,
        ],
        dtype=np.float32,
    )
