"""A Structures Class to be able to work with several structures."""

from __future__ import annotations

from molara.structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"


class Structures:
    """A class to store and manipulate a list of Structures."""

    def __init__(self) -> None:
        """Initialize the Structures Class."""
        self._structures: list = []
        self._structure_id = 0

    @property
    def _num_structures(self) -> int:
        """Number of structures."""
        return len(self._structures)

    def _get_current_structure(self) -> Structure:
        """Return the current structure."""
        return self._structures[self._structure_id]

    def _get_structure_by_id(self, structure_id: int) -> Structure:
        """Return a structure of the list of structure by a given index.

        :param structure_id: list index of the structure that shall be returned
        """
        self._structure_id = structure_id
        return self._structures[self._structure_id]

    def _set_next_structure(self) -> None:
        """Return the next structure in the list of structure."""
        self._structure_id += 1
        self._structure_id %= self._num_structures

    def _set_previous_structure(self) -> None:
        """Return the previous structure of the list of structure."""
        self._structure_id -= 1
        self._structure_id %= self._num_structures

    def _set_structure_by_id(self, structure_id: int) -> None:
        """Set the structure by a given index.

        :param structure_id: list index of the structure that shall be set as current
        """
        self._structure_id = structure_id
        self._structure_id %= self._num_structures

    def _add_structure(self, struct: Structure) -> None:
        """Add a structure to the list of structures.

        :param struct: Structure object to be added to the list
        """
        if not isinstance(struct, Structure):
            msg = "The given structure is not a Structure object."
            raise TypeError(msg)
        self._structures.append(struct)

    def _remove_structure(self, structure_id: int) -> None:
        """Remove a structure from the list of structures.

        :param structure_id: list index of the structure that shall be removed
        """
        self._structures.pop(structure_id)
