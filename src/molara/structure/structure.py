"""A module for the Structure class."""

from __future__ import annotations

import numpy as np
from scipy import spatial

from molara.structure.atom import Atom
from molara.structure.drawer import Drawer

__copyright__ = "Copyright 2024, Molara"

NO_BONDS = np.array([[-1, -1]], dtype=np.int_)


class Structure:
    """Base class for a structure with a set of atoms. Molecule and Crystal inherit from this."""

    def __init__(
        self: Structure,
        atomic_numbers: np.ndarray,
        coordinates: np.ndarray,
        draw_bonds: bool = True,
    ) -> None:
        """Create a new Structure object.

        :param atomic_numbers: np.ndarray: atomic numbers of a atoms
        :param coordinates: np.ndarray: coordinates of the atoms
        :param header:str: header from the imported file
        """
        self.atomic_numbers = np.array(atomic_numbers)
        self.coords = coordinates
        self.atoms = []
        self.vdw_rads: list[np.float32] = []
        self.unique_atomic_numbers: list[int] = []

        for i, atomic_number in enumerate(atomic_numbers):
            atom = Atom(atomic_number, coordinates[i])
            self.atoms.append(atom)
            if atomic_number not in self.unique_atomic_numbers:
                self.unique_atomic_numbers.append(atomic_number)

        self.molar_mass: float = np.sum([atom.atomic_mass for atom in self.atoms])

        self.bond_distance_factor = 1.0 / 1.75  # (sum of vdw radii) / 1.75 is the maximum distance for a bond
        self.draw_bonds = draw_bonds
        self.bonded_pairs = NO_BONDS
        self.bonds_calculated = False
        if self.draw_bonds:
            self.bonded_pairs = self.calculate_bonds()
            self.bonds_calculated = True

        self.drawer = Drawer(self.atoms, self.bonded_pairs, self.draw_bonds)
        self.n_at = len(self.atoms)
        self.center_of_mass = self.calculate_center_of_mass()
        self.coordinate_shift = np.zeros(3)  # keeps track of coord. shifts (e.g., by recentering)
        self.geometric_center = np.mean(self.coords, axis=0)

    def __copy__(self: Structure) -> Structure:
        """Create a copy of the structure."""
        return type(self)(
            self.atomic_numbers,
            np.array([atom.position for atom in self.atoms]),
            draw_bonds=self.draw_bonds,
        )

    def compute_collision(self: Structure, coordinate: np.ndarray) -> int | None:
        """Compute if the given coordinate is equal to the coordinate of an existing atom.

        Return None if no atom collides.

        :param coordinate: Coordinate to check whether they are equal to position of an atom
        """
        dist_threshold = 1e-10
        for i, atom in enumerate(self.atoms):
            dist = np.linalg.norm(atom.position - coordinate)
            if dist < dist_threshold:
                return i
        return None

    def calculate_center_of_mass(self: Structure) -> np.ndarray:
        """Return the center of mass of the structure."""
        return np.average(
            [atom.position for atom in self.atoms],
            weights=[atom.atomic_mass for atom in self.atoms],
            axis=0,
        )

    def center_coordinates(self: Structure) -> None:
        """Centers the structure around the center of mass."""
        self.center_of_mass = self.calculate_center_of_mass()
        self.coordinate_shift += self.center_of_mass  # change to geometric center if needed
        self.geometric_center = np.mean(self.coords, axis=0)
        for _i, atom in enumerate(self.atoms):
            position = atom.position - self.center_of_mass
            atom.set_position(position)

        self.drawer.update_atoms(self.atoms)
        if self.draw_bonds:
            self.drawer.update_bonds()

        self.center_of_mass = self.calculate_center_of_mass()
        self.geometric_center = np.mean(self.coords, axis=0)

    def calculate_bonds(self: Structure) -> np.ndarray:
        """Calculate the bonded pairs of atoms."""
        same_position_threshold = 1e-3
        bonded_pairs = []

        vdw_radii = np.array([atom.vdw_radius for atom in self.atoms])
        coordinates = np.array([atom.position for atom in self.atoms])

        max_distance = 2.0 * vdw_radii.max() * self.bond_distance_factor
        tree = spatial.cKDTree(coordinates)

        for i, j in tree.query_pairs(max_distance):
            atom1_radius, atom2_radius = vdw_radii[i], vdw_radii[j]
            distance = np.linalg.norm(coordinates[j] - coordinates[i])

            mean_radii = (atom1_radius + atom2_radius) * self.bond_distance_factor
            if distance <= mean_radii and distance > same_position_threshold:
                bonded_pairs.append((i, j))

        if bonded_pairs:
            return np.array(bonded_pairs)

        return NO_BONDS

    @property
    def has_bonds(self) -> bool:
        """Specifies whether structure contains any bonds that could be displayed."""
        return self.bonded_pairs[0][0] != -1

    def toggle_bonds(self: Structure) -> None:
        """Toggles the bonds on and off."""
        self.draw_bonds = not self.draw_bonds
        if not self.draw_bonds:
            return
        if not self.bonds_calculated:
            self.bonded_pairs = self.calculate_bonds()
            self.bonds_calculated = True
            self.drawer.update_bonds(self.bonded_pairs, self.draw_bonds)
            return
        self.drawer.update_bonds()

    def add_atom(
        self: Structure,
        atomic_number: int,
        coordinate: np.ndarray,
    ) -> None:
        """Add an atom to the structure.

        :param atomic_number: atomic number (nuclear charge number) of the atom
        :param coordinate: cartesian coordinates of atom location
        """
        atom = Atom(atomic_number, coordinate)
        self.atoms.append(atom)
        self.bonded_pairs = self.calculate_bonds()
        self.drawer = Drawer(self.atoms, self.bonded_pairs, draw_bonds=self.draw_bonds)
        self.atomic_numbers = np.append(self.atomic_numbers, atomic_number)
        self.coords = np.append(self.coords, coordinate)
        self.n_at += 1
        self.molar_mass += atom.atomic_mass

    def remove_atom(self: Structure, index: int) -> None:
        """Remove an atom from the structure.

        :param index: list index of the atom that shall be removed
        """
        self.n_at -= 1
        self.molar_mass -= self.atoms[index].atomic_mass
        self.atoms.pop(index)

        if self.n_at != 0:
            self.bonded_pairs = self.calculate_bonds()
            self.drawer = Drawer(self.atoms, self.bonded_pairs, draw_bonds=self.draw_bonds)

        self.atomic_numbers = np.delete(self.atomic_numbers, index)
        self.coords = np.delete(self.coords, index)
