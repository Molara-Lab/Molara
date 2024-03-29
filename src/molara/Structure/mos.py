"""Module for the Basisset class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.Eval.aos import calculate_aos

if TYPE_CHECKING:
    from molara.Structure.basisset import Orbital

__copyright__ = "Copyright 2024, Molara"


class Mos:
    """Class to store either an STO or GTO basisset for each atom in the same order as in molecule."""

    def __init__(
        self,
        labels: list | None = None,
        energies: list | None = None,
        spins: list | None = None,
        occupations: list | None = None,
    ) -> None:
        """Initialize the Mos class.

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
        self.coefficients: np.ndarray = np.array([])

    def calculate_mo_cartesian(  # noqa: C901
        self,
        index: int,
        aos: list[Orbital],
        electron_position: np.ndarray,
    ) -> float:
        """Calculate the value of one mo for a given electron position. Cartesian only!.

        :param index: index of the mo
        :param aos: list of all the aos
        :param electron_position: position of the electron
        :return: value of the mo
        """
        s = 0
        p = 1
        d = 2
        f = 3
        g = 4
        mo = 0
        mo_coefficients = self.coefficients[index]
        i = 0
        while i < len(mo_coefficients):
            shell = sum(aos[i].ijk)
            ao_values = calculate_aos(
                electron_position,
                aos[i].position,
                aos[i].exponents,
                aos[i].coefficients,
                shell,
            )
            if shell == s:
                mo += mo_coefficients[i] * ao_values[0]
                i += 1
            elif shell == p:
                for j in range(3):
                    mo += mo_coefficients[i] * ao_values[j]
                    i += 1
            elif shell == d:
                for j in range(6):
                    mo += mo_coefficients[i] * ao_values[j]
                    i += 1
            elif shell == f:
                for j in range(10):
                    mo += mo_coefficients[i] * ao_values[j]
                    i += 1
            elif shell == g:
                for j in range(15):
                    mo += mo_coefficients[i] * ao_values[j]
                    i += 1
            else:
                msg = f"The shell {shell} type is not supported."
                raise TypeError(msg)
        return mo
