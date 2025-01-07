"""Contains the Drawer class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.rendering.cylinders import Cylinders
from molara.rendering.spheres import (
    Spheres,
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
        self.atoms: None | list = atoms

        self.subdivisions_sphere = 20
        self.electron_scale = 0.03
        self.subdivisions_cylinder = 20
        self.stick_mode = False
        self.color_scheme = "Jmol"

        self.sphere_scale = 1.0
        self.sphere_default_radius = 1.0 / 6
        self.cylinder_scale = 1.0
        self.cylinder_default_radius = 0.075

        self.spheres: Spheres | None = None
        self.cylinders: Cylinders | None = None

        self.sphere_positions: list | np.ndarray = []
        self.sphere_colors: list | np.ndarray = []
        self.sphere_radii: list | np.ndarray = []
        self.set_spheres()

        self.cylinder_colors: list | np.ndarray = []
        self.cylinder_positions: list | np.ndarray = []
        self.cylinder_directions: list | np.ndarray = []
        self.cylinder_dimensions: list | np.ndarray = []

        self.bonds = NO_BONDS
        self.draw_bonds = draw_bonds
        self.update_bonds(bonds)

    @property
    def has_bonds(self) -> bool:
        """Specifies whether drawer has been passed any bonds to draw."""
        return self.bonds[0][0] != -1

    def set_spheres(self, atoms: None | list = None) -> None:
        """Update the bonds and/or bond matrices of the drawer."""
        if atoms is not None:
            self.atoms = atoms

        self.sphere_positions = []
        self.sphere_colors = []
        self.sphere_radii = []
        scaling_factor = self.sphere_default_radius * self.sphere_scale
        assert self.atoms is not None
        if not self.stick_mode:
            for atom in self.atoms:
                self.sphere_positions.append(atom.position)
                self.sphere_colors.append(atom.color[self.color_scheme])
                if atom.vdw_radius > 0:
                    self.sphere_radii.append(scaling_factor * atom.vdw_radius)
                else:
                    self.sphere_radii.append(self.electron_scale)
        else:
            scaling_factor = self.cylinder_default_radius * self.sphere_scale
            scaling_factor *= 0.99
            for atom in self.atoms:
                self.sphere_positions.append(atom.position)
                self.sphere_colors.append(atom.color[self.color_scheme])
                self.sphere_radii.append(scaling_factor)

        self.sphere_positions = np.array(self.sphere_positions, dtype=np.float32)
        self.sphere_colors = np.array(self.sphere_colors, dtype=np.float32)
        self.sphere_radii = np.array(self.sphere_radii, dtype=np.float32)

        self.spheres = Spheres(
            self.subdivisions_sphere,
            self.sphere_positions,
            self.sphere_radii,
            self.sphere_colors,
            wire_frame=False,
        )

    def update_bonds(self, bonds: np.ndarray | None = None, draw_bonds: bool = True) -> None:
        """Update the bonds and/or bond matrices of the drawer."""
        self.draw_bonds = draw_bonds

        if bonds is not None:
            self.bonds = bonds

        if not self.draw_bonds:
            return

        if self.has_bonds:
            self.set_cylinders()

    def set_atom_colors(self) -> None:
        """Set the colors of the atoms."""
        assert self.atoms is not None
        assert self.spheres is not None
        self.sphere_colors = np.array([atom.color[self.color_scheme] for atom in self.atoms], dtype=np.float32)
        self.spheres.colors = self.sphere_colors

    def set_atom_positions(self) -> None:
        """Set the positions of the atoms."""
        assert self.atoms is not None
        self.sphere_positions = np.array(
            [np.array(atom.position, dtype=np.float32) for atom in self.atoms],
            dtype=np.float32,
        )

    def set_sphere_radii(self) -> None:
        """Set the scales of the atoms."""
        self.sphere_radii = []
        scaling_factor = self.sphere_default_radius * self.sphere_scale
        assert self.atoms is not None
        if not self.stick_mode:
            self.sphere_radii = np.array(
                [
                    scaling_factor * atom.vdw_radius if atom.vdw_radius > 0 else self.electron_scale
                    for atom in self.atoms
                ],
                dtype=np.float32,
            )
        else:
            scaling_factor = self.cylinder_default_radius * self.sphere_scale
            scaling_factor *= 0.99
            self.sphere_radii = np.array(
                [scaling_factor if atom.vdw_radius > 0 else self.electron_scale for atom in self.atoms],
                dtype=np.float32,
            )

    def set_cylinders(self) -> None:
        """Set the colors of the bonds (cylinders)."""
        self.cylinder_colors = []
        self.cylinder_positions = []
        self.cylinder_directions = []
        self.cylinder_dimensions = []
        radius = self.cylinder_default_radius * self.cylinder_scale

        assert self.bonds is not None
        assert self.atoms is not None
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
            self.cylinder_directions.append(difference)
            self.cylinder_dimensions.append([radius, length, radius])
            self.cylinder_dimensions.append([radius, length, radius])
            self.cylinder_colors.append(atom1.color[self.color_scheme])
            self.cylinder_colors.append(atom2.color[self.color_scheme])

        self.cylinder_colors = np.array(self.cylinder_colors, dtype=np.float32)
        self.cylinder_positions = np.array(self.cylinder_positions, dtype=np.float32)
        self.cylinder_directions = np.array(self.cylinder_directions, dtype=np.float32)
        self.cylinder_dimensions = np.array(self.cylinder_dimensions, dtype=np.float32)

        self.cylinders = Cylinders(
            self.subdivisions_cylinder,
            self.cylinder_positions,
            self.cylinder_directions,
            self.cylinder_dimensions,
            self.cylinder_colors,
            wire_frame=False,
        )

    def set_cylinder_radii(self) -> None:
        """Set the dimensions of the cylinders.

        It is important to note, that the radius ([:,1]) of the cylinders need not be changed!
        """
        assert isinstance(self.cylinder_dimensions, np.ndarray)
        self.cylinder_dimensions[:, 0] = self.cylinder_default_radius * self.cylinder_scale
        self.cylinder_dimensions[:, 2] = self.cylinder_default_radius * self.cylinder_scale

    def set_cylinder_colors(self) -> None:
        """Set the colors of the bonds (cylinders)."""
        self.cylinder_colors = []
        assert self.bonds is not None
        assert self.atoms is not None
        if self.cylinders is None:
            return
        for bond in self.bonds:
            if bond[0] == -1:
                continue
            atom1, atom2 = self.atoms[bond[0]], self.atoms[bond[1]]
            self.cylinder_colors.append(atom1.color[self.color_scheme])
            self.cylinder_colors.append(atom2.color[self.color_scheme])
        self.cylinder_colors = np.array(self.cylinder_colors, dtype=np.float32)
        self.cylinders.colors = self.cylinder_colors

    def set_cylinder_model_matrices(self) -> None:
        """Set the model matrices for the cylinders."""
        assert self.cylinders is not None
        self.cylinders.calculate_model_matrices()

    def set_cylinder_translation_matrices(self) -> None:
        """Set the translation matrices for the spheres."""
        assert self.cylinders is not None

        self.cylinders.calculate_translation_matrices(self.cylinder_positions)

    def set_cylinder_scale_matrices(self) -> None:
        """Set the translation matrices for the cylinders."""
        assert self.cylinders is not None

        self.cylinders.calculate_scaling_matrices(self.cylinder_dimensions)

    def set_cylinder_rotation_matrices(self) -> None:
        """Set the rotation matrices for the cylinders."""
        assert self.cylinders is not None

        self.cylinders.calculate_rotation_matrices(self.cylinder_directions)

    def set_atom_translation_matrices(self) -> None:
        """Set the translation matrices for the spheres."""
        assert self.spheres is not None

        self.spheres.calculate_translation_matrices(self.sphere_positions)

    def set_atom_scale_matrices(self) -> None:
        """Set the scale matrices for the spheres."""
        assert self.spheres is not None

        self.spheres.calculate_scaling_matrices(self.sphere_radii)

    def set_atom_model_matrices(self) -> None:
        """Set the model matrices for the spheres."""
        assert self.spheres is not None

        self.spheres.calculate_model_matrices()
