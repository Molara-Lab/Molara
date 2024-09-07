"""Contains the Molecule class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.structure.mos import Mos
from molara.structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"
if TYPE_CHECKING:
    from molara.structure.atom import Atom


class Molecule(Structure):
    """Creates a new Molecule object."""

    def __init__(
        self,
        atomic_numbers: np.ndarray,
        coordinates: np.ndarray,
        header: str | None = None,
        dummy: bool = False,
        draw_bonds: bool = True,
    ) -> None:
        """Create a new Molecule object.

        :param atomic_numbers:np.ndarray: atomic numbers of a atoms
        :param coordinates:np.ndarray: coordinates of the molecule
        :param header:str: header from the imported file
        :param dummy: bool: a dummy object.
        :param draw_bonds: bool: draw bonds between atoms (Default is True)
        """
        if dummy:
            self.dummy = True

        self.atomic_numbers = np.array(atomic_numbers)
        self.atoms: list[Atom] = []
        self.mos = Mos()
        self.vdw_rads: list[np.float32] = []
        self.subdivisions = 20
        self.gen_energy_information(header)
        self.aos: list = []
        super().__init__(atomic_numbers, coordinates, draw_bonds)

    def center_coordinates(self: Molecule) -> None:
        """Centers the structure around the center of mass."""
        self.center_of_mass = self.calculate_center_of_mass()
        for _i, atom in enumerate(self.atoms):
            position = atom.position - self.center_of_mass
            atom.set_position(position)
        for i in range(len(self.aos)):
            atom_idx = self.aos[i].atom_idx
            self.aos[i].position = self.atoms[atom_idx].position

        self.drawer.update_atoms(self.atoms)
        if self.draw_bonds:
            self.drawer.update_bonds()

        self.center_of_mass = self.calculate_center_of_mass()

    def gen_energy_information(self, string: str | None) -> None:
        """Read the energy from the second line.

        :param string: file header from which energy info is extracted
        """
        self.energy = 0.0

        if isinstance(string, str):
            split_string = string.split()

            if "energy:" in split_string:
                index_e = split_string.index("energy:")

                if index_e + 1 < len(split_string):
                    self.energy = float(
                        string.split()[split_string.index("energy:") + 1],
                    )
