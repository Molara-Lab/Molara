"""A module for the Geometry class."""
from __future__ import annotations

from typing import TYPE_CHECKING

# if TYPE_CHECKING:
import numpy as np

from .atom import Atom
from .drawer import Drawer

class Geometry:
    """A class to represent a molecule's geometry."""

    def __init__(  # noqa: PLR0913
        self,
        atomic_numbers: np.ndarray,
        coordinates: np.ndarray,
        draw_bonds: bool = True,
    ) -> None:
        """Creates a new Geometry object.

        params:
        atomic_numbers:np.ndarray: atomic numbers of a atoms
        coordinates:np.ndarray: coordinates of the molecule
        header:str: header from the imported file
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

        self.bonded_pairs = self.calculate_bonds()
        self.drawer = Drawer(self.atoms, self.bonded_pairs)
        self.draw_bonds = (self.bonded_pairs[0, 0] != -1) and draw_bonds

    def center_coordinates(self) -> None:
        """Centers the molecule around the center of mass."""
        coordinates = np.array([atom.position for atom in self.atoms])
        center = np.average(
            coordinates,
            weights=[atom.atomic_mass for atom in self.atoms],
            axis=0,
        )
        for _i, atom in enumerate(self.atoms):
            atom.position -= center
        self.drawer.set_atoms(self.atoms)
        self.drawer.set_atom_translation_matrices()
        if self.draw_bonds:
            self.drawer.set_cylinder_props()
            self.drawer.set_cylinder_translation_matrices()
            self.drawer.set_cylinder_model_matrices()
        self.drawer.set_atom_model_matrices()

    def calculate_bonds(self) -> np.ndarray:
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

    def toggle_bonds(self) -> None:
        """Toggles the bonds on and off."""
        self.draw_bonds = not self.draw_bonds

    def add_atom(self, atomic_number: int, coordinate: np.ndarray) -> None:
        """Adds an atom to the molecule."""
        atom = Atom(atomic_number, coordinate)
        self.atoms.append(atom)
        self.bonded_pairs = self.calculate_bonds()

    def remove_atom(self, index: int) -> None:
        """Removes an atom from the molecule."""
        self.atoms.pop(index)
        self.bonded_pairs = self.calculate_bonds()
