"""Module for the Basisset class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.eval.aos import calculate_aos

if TYPE_CHECKING:
    from molara.structure.basisset import Orbital

__copyright__ = "Copyright 2024, Molara"


class Mos:
    """Class to store either an STO or GTO basisset for each atom in the same order as in molecule."""

    def __init__(
        self,
        labels: list | None = None,
        energies: list | None = None,
        spins: list | None = None,
        occupations: list | None = None,
        basisfunctions: list | None = None,
        type: str = "cartesian",
    ) -> None:
        """Initialize the Mos class.

        :param labels: list of labels for the mos
        :param energies: list of energies for the mos
        :param spins: list of spins for the mos
        :param occupations: list of occupations for the mos
        :param basisfunctions: list of basisfunctions for the mos
        :param type: str: type of the mos, either cartesian or spherical
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
        if basisfunctions is not None:
            self.basisfunctions = basisfunctions
        else:
            self.basisfunctions = []
        self.type = type

        self.coefficients: np.ndarray = np.array([])
        self.coefficients_display: np.ndarray = np.array([])

    def set_mo_coefficients(
        self, mo_coefficients: np.ndarray, spherical_order: str = "none"
    ) -> None:
        """Set the coefficients for the mos and transform to cartesian ones.

        :param mo_coefficients: np.ndarray: coefficients for the mos
        :param spherical_order: string: spherical order of the coefficients, only orca supported if none is given the
        coefficients are assumed to be in cartesian order
        """

        self.coefficients_display = mo_coefficients
        if spherical_order == "none":
            self.coefficients = mo_coefficients
        elif spherical_order == "orca":
            self.coefficients = spherical_to_cartesian_transformation(
                mo_coefficients, self.basisfunctions, spherical_order
            )
        else:
            msg = f"The spherical_order {spherical_order} is not supported."
            raise TypeError(msg)

    def get_mo_value(  # noqa: C901
        self,
        index: int,
        aos: list[Orbital],
        electron_position: np.ndarray,
    ) -> float:
        """Calculate the value of one mo for a given electron position. Cartesian only!.

        :param index: index of the mo
        :param aos: list of all the aos
        :param electron_position: position of the electron in angstrom
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
        ao_values = np.zeros(15)
        while i < len(mo_coefficients):
            shell = sum(aos[i].ijk)
            calculate_aos(
                np.array(electron_position, dtype=np.float64) * 1.889726124565062,
                np.array(aos[i].position, dtype=np.float64) * 1.889726124565062,
                np.array(aos[i].exponents, dtype=np.float64),
                np.array(aos[i].coefficients, dtype=np.float64),
                np.array(aos[i].norms, dtype=np.float64),
                shell,
                ao_values,
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
            print(mo, i)
        return mo


def spherical_to_cartesian_transformation(
    mo_coefficients: np.ndarray, basisfunctions: list, spherical_order: str
) -> np.ndarray:
    """Transform spherical coefficients to cartesian coefficients.

    :param mo_coefficients: np.ndarray: coefficients for the mos
    :param spherical_order: string: spherical order of the coefficients, only orca supported.
    :return: np.ndarray: cartesian coefficients
    """

    orca_transformation_d = np.array(
        [
            [-1 / 2, -1 / 2, 1, 0, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
            [np.sqrt(3) / 2, -np.sqrt(3) / 2, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0],
        ],
        dtype=np.float64,
    )

    orca_transformation_f = np.array(
        [
            [0, 0, 1, 0, -3 * np.sqrt(5) / 10, 0, -3 * np.sqrt(5) / 10, 0, 0, 0],
            [-np.sqrt(6) / 4, 0, 0, 0, 0, -np.sqrt(30) / 20, 0, np.sqrt(30) / 5, 0, 0],
            [0, -np.sqrt(6) / 4, 0, -np.sqrt(30) / 20, 0, 0, 0, 0, np.sqrt(30) / 5, 0],
            [0, 0, 0, 0, np.sqrt(3) / 2, 0, -np.sqrt(3) / 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [-np.sqrt(10) / 4, 0, 0, 0, 0, 3 * np.sqrt(2) / 4, 0, 0, 0, 0],
            [0, np.sqrt(10) / 4, 0, -3 * np.sqrt(2) / 4, 0, 0, 0, 0, 0, 0],
        ],
        dtype=np.float64,
    )

    orca_transformation_g = np.array(
        [
            [
                3 / 8,
                3 / 8,
                1,
                0,
                0,
                0,
                0,
                0,
                0,
                3 * np.sqrt(105) / 140,
                -3 * np.sqrt(105) / 35,
                -3 * np.sqrt(105) / 35,
                0,
                0,
                0,
            ],
            [
                0,
                0,
                0,
                0,
                -3 * np.sqrt(70) / 28,
                0,
                0,
                np.sqrt(70) / 7,
                0,
                0,
                0,
                0,
                0,
                -3 * np.sqrt(14) / 28,
                0,
            ],
            [
                0,
                0,
                0,
                0,
                0,
                0,
                -3 * np.sqrt(70) / 28,
                0,
                np.sqrt(70) / 7,
                0,
                0,
                0,
                -3 * np.sqrt(14) / 28,
                0,
                0,
            ],
            [
                -np.sqrt(5) / 4,
                np.sqrt(5) / 4,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                3 * np.sqrt(21) / 14,
                -3 * np.sqrt(21) / 14,
                0,
                0,
                0,
            ],
            [
                0,
                0,
                0,
                -np.sqrt(35) / 14,
                0,
                -np.sqrt(35) / 14,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                3 * np.sqrt(7) / 7,
            ],
            [
                0,
                0,
                0,
                0,
                -np.sqrt(10) / 4,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                3 * np.sqrt(2) / 4,
                0,
            ],
            [
                0,
                0,
                0,
                0,
                0,
                0,
                np.sqrt(10) / 4,
                0,
                0,
                0,
                0,
                0,
                -3 * np.sqrt(2) / 4,
                0,
                0,
            ],
            [
                -np.sqrt(35) / 8,
                -np.sqrt(35) / 8,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                3 * np.sqrt(3) / 4,
                0,
                0,
                0,
                0,
                0,
            ],
            [0, 0, 0, -np.sqrt(5) / 2, 0, np.sqrt(5) / 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ],
        dtype=np.float64,
    )

    new_coefficients = []
    skip_counter = 0
    for mo in mo_coefficients:
        new_coefficients_temp = []
        index = 0
        for atom_basis in basisfunctions:
            for bf in atom_basis:
                if skip_counter > 0:
                    skip_counter -= 1
                    continue
                if "dxx" in bf:
                    d_coefficients_spherical = mo[index : index + 5]
                    d_coefficients_cart = np.dot(
                        d_coefficients_spherical, orca_transformation_d
                    )
                    new_coefficients_temp.extend(d_coefficients_cart)
                    skip_counter = 5
                    index += 5
                elif "fxxx" in bf:
                    f_coefficients_spherical = mo[index : index + 7]
                    f_coefficients_cart = np.dot(
                        f_coefficients_spherical, orca_transformation_f
                    )
                    new_coefficients_temp.extend(f_coefficients_cart)
                    skip_counter = 9
                    index += 7
                elif "gxxxx" in bf:
                    g_coefficients_spherical = mo[index : index + 9]
                    g_coefficients_cart = np.dot(
                        g_coefficients_spherical, orca_transformation_g
                    )
                    new_coefficients_temp.extend(g_coefficients_cart)
                    skip_counter = 14
                    index += 9
                else:
                    new_coefficients_temp.append(mo[index])
                    index += 1
        new_coefficients.append(new_coefficients_temp)
    return np.array(new_coefficients)
