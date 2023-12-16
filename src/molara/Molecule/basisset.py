"""Module for the Basisset class."""
from __future__ import annotations


class Basisset:
    """Class to store either an STO or GTO basisset for each atom in the same order as in molecule."""

    def __init__(self, basis_type: str = "None") -> None:
        """Initializes the Basisset class.

        :param basis_type: str.
        :return:
        """
        self.basis_type: str = basis_type
        self.basisset: list = [
            {
                "shells": [],
                "exponents": [],
                "coefficients": [],
            },
        ]
