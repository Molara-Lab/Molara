"""A module for the Structure class."""

from __future__ import annotations

from typing import TYPE_CHECKING

# if TYPE_CHECKING:
import numpy as np

from molara.Structure.atom import Atom
from molara.Structure.drawer import Drawer

__copyright__ = "Copyright 2024, Molara"

if TYPE_CHECKING:
    from molara.Structure.crystal import Crystal
    from molara.Structure.molecule import Molecule


class Structure:
    """Base class for a structure with a set of atoms. Molecule and Crystal inherit from this."""

    def __init__(
        self: Structure | Crystal | Molecule,
        atomic_numbers: np.ndarray,
        coordinates: np.ndarray,
        draw_bonds: bool = True,
    ) -> None:
        """Creates a new Structure object.

        :param atomic_numbers: np.ndarray: atomic numbers of a atoms
        :param coordinates: np.ndarray: coordinates of the atoms
        :param header:str: header from the imported file
        """
        self.atomic_numbers = np.array(atomic_numbers)
        self.atoms = []
        self.vdw_rads: list[np.float32] = []
        self.unique_atomic_numbers: list[int] = []

        for i, atomic_number in enumerate(atomic_numbers):
            atom = Atom(atomic_number, coordinates[i])
            self.atoms.append(atom)
            if atomic_number not in self.unique_atomic_numbers:
                self.unique_atomic_numbers.append(atomic_number)

        self.molar_mass: float = np.sum([atom.atomic_mass for atom in self.atoms])
        self.bonded_pairs = self.calculate_bonds()
        self.draw_bonds = draw_bonds and (self.bonded_pairs[0, 0] != -1)
        self.drawer = Drawer(self.atoms, self.bonded_pairs, self.draw_bonds)
        self.n_at = len(self.atoms)

    def copy(self: Structure | Crystal | Molecule) -> Structure:
        """Creates a copy of the structure."""
        return type(self)(
            self.atomic_numbers,
            np.array([atom.position for atom in self.atoms]),
            self.draw_bonds,
        )

    def compute_collision(self: Structure | Crystal | Molecule, coordinate: np.ndarray) -> int | None:
        """Computes if the given coordinate is equal to the coordinate of an existing atom.

        Return None if no atom collides.

        :param coordinate: Coordinate to check whether they are equal to position of an atom
        """
        dist_threshold = 1e-10
        for i, atom in enumerate(self.atoms):
            dist = np.linalg.norm(atom.position - coordinate)
            if dist < dist_threshold:
                return i
        return None

    def center_coordinates(self: Structure | Crystal | Molecule) -> None:
        """Centers the structure around the center of mass."""
        coordinates = np.array([atom.position for atom in self.atoms])
        self.center = np.average(
            coordinates,
            weights=[atom.atomic_mass for atom in self.atoms],
            axis=0,
        )
        for _i, atom in enumerate(self.atoms):
            position = atom.position - self.center
            atom.set_position(position)
        self.drawer.set_atoms(self.atoms)
        self.drawer.set_atom_translation_matrices()
        if self.draw_bonds:
            self.drawer.set_cylinder_props()
            self.drawer.set_cylinder_translation_matrices()
            self.drawer.set_cylinder_model_matrices()
        self.drawer.set_atom_model_matrices()

    def calculate_bonds(self: Structure | Crystal | Molecule) -> np.ndarray:
        """Calculates the bonded pairs of atoms."""
        bonded_pairs = []

        vdw_radii = np.array([atom.vdw_radius for atom in self.atoms])
        coordinates = np.array([atom.position for atom in self.atoms])

        for i in range(len(self.atoms)):
            atom1_coord = coordinates[i]
            atom1_radius = vdw_radii[i]

            distances = np.linalg.norm(coordinates - atom1_coord, axis=1)
            mean_radii = (vdw_radii + atom1_radius) / 1.75

            bonded_indices = np.where(distances <= mean_radii)[0]
            bonded_pairs.extend([(i, j) for j in bonded_indices if j > i])

        if bonded_pairs:
            return np.array(bonded_pairs)

        return np.array([[-1, -1]], dtype=np.int_)

    def toggle_bonds(self: Structure | Crystal | Molecule) -> None:
        """Toggles the bonds on and off."""
        self.draw_bonds = not self.draw_bonds

    def add_atom(
        self: Structure | Crystal | Molecule,
        atomic_number: int,
        coordinate: np.ndarray,
    ) -> None:
        """Adds an atom to the structure.

        :param atomic_number: atomic number (nuclear charge number) of the atom
        :param coordinate: cartesian coordinates of atom location
        """
        atom = Atom(atomic_number, coordinate)
        self.atoms.append(atom)
        self.bonded_pairs = self.calculate_bonds()
        self.drawer = Drawer(self.atoms, self.bonded_pairs, draw_bonds=self.draw_bonds)
        self.atomic_numbers = np.append(self.atomic_numbers, atomic_number)
        self.n_at += 1
        self.molar_mass += atom.atomic_mass

    def remove_atom(self: Structure | Crystal | Molecule, index: int) -> None:
        """Removes an atom from the structure.

        :param index: list index of the atom that shall be removed
        """
        self.n_at -= 1
        self.molar_mass -= self.atoms[index].atomic_mass
        self.atoms.pop(index)

        if self.n_at != 0:
            self.bonded_pairs = self.calculate_bonds()
            self.drawer = Drawer(self.atoms, self.bonded_pairs, draw_bonds=self.draw_bonds)

        self.atomic_numbers = np.delete(self.atomic_numbers, index)
