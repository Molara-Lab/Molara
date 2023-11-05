"""A module for the Geometry class."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


class Geometry:
    """A class to represent a molecule's geometry."""

    def __init__(self) -> None:
        """Initializes the Geometry Class."""
        self.atomic_numbers: list[int] = []
        self.coords: list[np.ndarray] = []

    def add_atom(self, atomic_number: int, coords: np.ndarray) -> None:
        """Adds an atom to the geometry.

        :param atomic_number: The atomic number of the atom.
        :param coords: The coordinates of the atom.
        :return:
        """
        self.atomic_numbers.append(atomic_number)
        self.coords.append(coords)
