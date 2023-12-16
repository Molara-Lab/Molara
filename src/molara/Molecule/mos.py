"""Module for the Basisset class."""
from __future__ import annotations


class Mos:
    """Class to store either an STO or GTO basisset for each atom in the same order as in molecule."""

    def __init__(self, symmetry: str = "", energy: float = 0.0, spin: int = 1, occupation: float = 0.0) -> None:
        """Initializes the Mos class.

        :param symmetry: Symmetry of the molecular orbital.
        :param energy: Energy of the molecular orbital.
        :param spin: Spin of the molecular orbital.
        :param occupation: Occupation of the molecular orbital.
        :return:
        """
        self.symmetry: str = symmetry
        self.energy: float = energy
        self.spin: int = spin
        self.occupation: float = occupation
