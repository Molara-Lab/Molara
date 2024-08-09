"""A Crystals Class to be able to work with several crystals."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from molara.structure.crystal import Crystal

from molara.structure.structures import Structures


class Crystals(Structures):
    """A class to store and manipulate a list of Crystals."""

    def __init__(self) -> None:
        """Initialize the Crystals Class."""
        super().__init__()
        self.energies: list = []

        # aliases for attributes and properties from Structure
        self.mols = self._structures

        # aliases for routines from Structure
        self.get_current_mol = self._get_current_structure
        self.get_mol_by_id = self._get_structure_by_id
        self.set_next_mol = self._set_next_structure
        self.set_previous_mol = self._set_previous_structure
        self.remove_crystal = self._remove_structure

    def _get_current_structure(self) -> Crystal:
        """Return the current structure."""
        return self._structures[self._structure_id]

    @property
    def num_mols(self) -> int:
        """Number of crystals."""
        return self._num_structures

    @property
    def mol_index(self) -> int:
        """Index of currently displayed molecule."""
        return self._structure_id

    def add_crystal(self, crystal: Crystal) -> None:
        """Add a new crystals to list of crystals.

        :param crystal: Crystal object to be added to Crystals object
        """
        self._add_structure(crystal)
        self.energies.append(crystal.energy)
