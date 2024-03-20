"""Contains the Molecule class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.Structure.mos import Mos
from molara.Structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"
if TYPE_CHECKING:
    from molara.Structure.atom import Atom


class Molecule(Structure):
    """Creates a new Molecule object."""

    def __init__(  # noqa: PLR0913
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
