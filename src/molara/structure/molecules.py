"""A Molecules Class to be able to work with several molecules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from molara.structure.structures import Structures

if TYPE_CHECKING:
    from molara.structure.molecule import Molecule

__copyright__ = "Copyright 2024, Molara"


class Molecules(Structures):
    """A class to store and manipulate a list of Molecules."""

    def __init__(self) -> None:
        """Initialize the Molecules Class."""
        super().__init__()
        self.energies: list = []

        # aliases for attributes and properties from Structure
        self.mols: list[Molecule] = self._structures

        # aliases for routines from Structure
        self.get_current_mol = self._get_current_structure
        self.get_mol_by_id = self._get_structure_by_id
        self.set_next_mol = self._set_next_structure
        self.set_previous_mol = self._set_previous_structure
        self.set_mol_by_id = self._set_structure_by_id

    @property
    def num_mols(self) -> int:
        """Number of molecules."""
        return self._num_structures

    @property
    def all_molecules(self) -> list[Molecule]:
        """Return all molecules."""
        return self.mols

    @property
    def mol_index(self) -> int:
        """Index of currently displayed molecule."""
        return self._structure_id

    def add_molecule(self, mol: Molecule) -> None:
        """Add a new molecules to list of molecules.

        :param mol: Molecule object to be added
        """
        self._add_structure(mol)
        self.energies.append(mol.energy)

    def remove_molecule(self, mol_id: int) -> None:
        """Remove a molecule from list of molecules.

        :param mol_id: Index of the molecule
        """
        self._remove_structure(mol_id)
        self.energies.pop(mol_id)
