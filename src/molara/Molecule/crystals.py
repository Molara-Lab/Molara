"""A Crystals Class to be able to work with several crystals."""
from __future__ import annotations

import numpy as np

from molara.Molecule.crystal import Crystal
from molara.Molecule.structures import Structures


class Crystals(Structures):
    """A class to store and manipulate a list of Crystals."""

    def __init__(self) -> None:
        """Initializes the Crystals Class."""
        self.mols: list = []
        self.mol_index = 0
        self.energies: list = []

    @property
    def num_mols(self) -> int:
        """Number of crystals."""
        return len(self.mols)

    def get_current_mol(self) -> Crystal:
        """Returns a."""
        return self.mols[self.mol_index]

    def set_next_mol(self) -> None:
        """Returns the next crystal in the list of crystals."""
        self.mol_index += 1

        self.mol_index %= self.num_mols

    def get_index_mol(self, index: int) -> Crystal:
        """Return a crystal of the list of crystals by a given index.

        param: index: int.
        """
        self.mol_index = index
        return self.mols[self.mol_index]

    def set_previous_mol(self) -> None:
        """Returns the previous crystal of the list of crystals."""
        self.mol_index -= 1

        if self.mol_index < 0:
            self.mol_index = self.num_mols - 1

    def add_crystal(self, mol: Crystal) -> None:
        """Adds a crystal to the list of crystals.

        param: mol: Crystal.
        """
        if type(mol) == Crystal:
            self.mols.append(mol)

            #self.energies.append(mol.energy)

    def remove_crystal(self, index: int) -> None:
        """Removes a crystal from the list of crystals.

        param: index: int.
        """
        self.mols.pop(index)
