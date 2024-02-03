"""A Structures Class to be able to work with several structures."""
from __future__ import annotations

from molara.Structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"


class Structures:
    """A class to store and manipulate a list of Structures."""

    def __init__(self) -> None:
        """Initializes the Structures Class."""
        self._structures: list = []
        self._structure_id = 0

    @property
    def _num_structures(self) -> int:
        """Number of structures."""
        return len(self._structures)

    def _get_current_structure(self) -> Structure:
        """Returns the current structure."""
        return self._structures[self._structure_id]

    def _get_structure_by_id(self, structure_id: int) -> Structure:
        """Return a structure of the list of structure by a given index.

        param: index: int.
        """
        self._structure_id = structure_id
        return self._structures[self._structure_id]

    def _set_next_structure(self) -> None:
        """Returns the next structure in the list of structure."""
        self._structure_id += 1
        self._structure_id %= self._num_structures

    def _set_previous_structure(self) -> None:
        """Returns the previous structure of the list of structure."""
        self._structure_id -= 1

        if self._structure_id < 0:
            self._structure_id = self._num_structures - 1

    def _add_structure(self, struct: Structure) -> None:
        """Adds a structure to the list of structures.

        param: struct: Structure.
        """
        if not isinstance(struct, Structure):
            msg = "The given structure is not a Structure object."
            raise TypeError(msg)
        self._structures.append(struct)

    def _remove_structure(self, structure_id: int) -> None:
        """Removes a structure from the list of structures.

        param: id: int.
        """
        self._structures.pop(structure_id)
