from __future__ import annotations

import numpy as np

from molara.Molecule.molecule import Molecule


class Molecules:
    """
    A class to store and manipulate a list of Molecules
    """

    def __init__(self) -> None:
        self.mols: list = []
        self.num_mols = 0
        self.mol_index = 0
        self.energies: list = []

    def get_current_mol(self) -> Molecule:
        return self.mols[self.mol_index]

    def set_next_mol(self) -> None:
        """
        Returns the next molecule in the list of molecules
        """

        self.mol_index += 1

        self.mol_index %= self.num_mols

    def get_index_mol(self, index: int) -> Molecule:
        """
        Return a molecule of the list of molecules by a given index
        param: index: int
        """
        self.mol_index = index
        return self.mols[self.mol_index]

    def set_previous_mol(self) -> None:
        """
        Returns the previous molecule of the list of molecules
        """
        self.mol_index -= 1

        if self.mol_index < 0:
            self.mol_index = self.num_mols - 1

    def add_molecule(self, mol: Molecule) -> None:
        """
        Adds a molecule to the list of molecules
        param: mol: Molecule
        """

        if type(mol) == Molecule:
            self.mols.append(mol)

            self.num_mols += 1

            self.energies.append(mol.energy)

    def remove_molecule(self, index: int) -> None:
        """
        Removes a molecule from the list of molecules
        param: index: int
        """

        self.mols.pop(index)
        self.num_mols -= 1
