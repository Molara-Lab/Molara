"""This module contains the Molecule class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import numpy as np

from molara.Molecule.atom import Atom
from molara.Molecule.basisset import Basisset
from molara.Molecule.drawer import Drawer
from molara.Molecule.mos import Mos
from molara.Molecule.geometry import Geometry

if TYPE_CHECKING:
    from numpy.typing import ArrayLike


class Molecule(Geometry):
    """Creates a new Molecule object."""

    def __init__(  # noqa: PLR0913
        self,
        atomic_numbers: np.ndarray,
        coordinates: np.ndarray,
        header: str | None = None,
        dummy: bool = False,
        draw_bonds: bool = True,
    ) -> None:
        """Creates a new Molecule object.

        params:
        atomic_numbers:np.ndarray: atomic numbers of a atoms
        coordinates:np.ndarray: coordinates of the molecule
        header:str: header from the imported file
        dummy: bool: a dummy object.
        """
        if dummy:
            self.dummy = True
        self.atomic_numbers = np.array(atomic_numbers)
        self.atoms = []
        self.basisset = Basisset()
        self.mos = Mos()
        self.vdw_rads: list[np.float32] = []
        self.subdivisions = 20
        self.gen_energy_information(header)

    def gen_energy_information(self, string: str | None) -> None:
        """Reads the energy from the second line."""
        self.energy = 0.0

        if isinstance(string, str):
            split_string = string.split()

            if "energy:" in split_string:
                index_e = split_string.index("energy:")

                if index_e + 1 < len(split_string):
                    self.energy = float(
                        string.split()[split_string.index("energy:") + 1],
                    )
