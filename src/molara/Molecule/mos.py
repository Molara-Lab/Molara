"""Module for the Basisset class."""
from __future__ import annotations


class Mos:
    """Class to store either an STO or GTO basisset for each atom in the same order as in molecule."""

    def __init__(
        self,
        labels: list | None = None,
        energies: list | None = None,
        spins: list | None = None,
        occupations: list | None = None,
    ) -> None:
        """Initializes the Mos class.

        :param labels: list of labels for the mos
        :param energies: list of energies for the mos
        :param spins: list of spins for the mos
        :param occupations: list of occupations for the mos
        :return:
        """
        if labels is not None:
            self.labels = labels
        else:
            self.labels = []
        if energies is not None:
            self.energies = energies
        else:
            self.energies = []
        if spins is not None:
            self.spins = spins
        else:
            self.spins = []
        if occupations is not None:
            self.occupations = occupations
        else:
            self.occupations = []
        self.coefficients: list[list] = [[]]
