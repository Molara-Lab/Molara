from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import numpy as np

from molara.Molecule.atom import Atom, element_symbol_to_atomic_number
from molara.Molecule.drawer import Drawer

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


class Molecule:
    def __init__(
        self,
        atomic_numbers: np.ndarray,
        coordinates: np.ndarray,
        header: str | None = None,
        dummy: bool = False,
    ) -> None:
        if dummy:
            self.dummy = True
        self.atomic_numbers = np.array(atomic_numbers)
        self.atoms = []
        self.vdw_rads: list[np.float32] = []
        self.subdivisions = 20
        self.unique_atomic_numbers: list[int] = []
        for i, atomic_number in enumerate(atomic_numbers):
            atom = Atom(atomic_number, coordinates[i])
            self.atoms.append(atom)
            if atomic_number not in self.unique_atomic_numbers:
                self.unique_atomic_numbers.append(atomic_number)

        self.bonded_pairs = self.calculate_bonds()
        self.drawer = Drawer(self.atoms, self.bonded_pairs)

        self.gen_energy_information(header)

    def calculate_bonds(self) -> np.ndarray:
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

    def add_atom(self, atomic_number: int, coordinate: ArrayLike) -> None:
        atom = Atom(atomic_number, coordinate)
        self.atoms.append(atom)
        self.bonded_pairs = self.calculate_bonds()

    def remove_atom(self, index: int) -> None:
        self.atoms.pop(index)
        self.bonded_pairs = self.calculate_bonds()

    def center_coordinates(self) -> None:
        coordinates = np.array([atom.position for atom in self.atoms])
        center = np.average(
            coordinates,
            weights=[atom.atomic_mass for atom in self.atoms],
            axis=0,
        )
        for _i, atom in enumerate(self.atoms):
            atom.position -= center
        self.drawer.set_atoms(self.atoms)
        self.drawer.set_sphere_model_matrices()
        self.drawer.set_cylinder_model_matrices()

    def gen_energy_information(self, string: str | None) -> None:
        """
        Reads the energy from the second line
        """
        if isinstance(string, str):
            self.energy = float(string.split()[1])
        else:
            self.energy = 0.0
