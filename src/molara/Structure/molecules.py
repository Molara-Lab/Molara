"""A Molecules Class to be able to work with several molecules."""
from __future__ import annotations

from typing import TYPE_CHECKING

from molara.Structure.structures import Structures

if TYPE_CHECKING:
    from molara.Structure.molecule import Molecule

__copyright__ = "Copyright 2024, Molara"


class Molecules(Structures):
    """A class to store and manipulate a list of Molecules."""

    def __init__(self) -> None:
        """Initializes the Molecules Class."""
        super().__init__()
        self.energies: list = []

        # aliases for attributes and properties from Structure
        self.mols = self._structures

        # aliases for routines from Structure
        self.get_current_mol = self._get_current_structure
        self.get_index_mol = self._get_structure_by_id
        self.set_next_mol = self._set_next_structure
        self.set_previous_mol = self._set_previous_structure
        self.remove_molecule = self._remove_structure

    @property
    def num_mols(self) -> int:
        """Number of molecules."""
        return self._num_structures

    @property
    def mol_index(self) -> int:
        """Index of currently displayed molecule."""
        return self._structure_id

    def add_molecule(self, mol: Molecule) -> None:
        """Add a new molecules to list of molecules."""
        self._add_structure(mol)
        self.energies.append(mol.energy)