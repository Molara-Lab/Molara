"""Module for the MolecularOrbital class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.eval.aos import calculate_aos
from molara.data.constants import ANGSTROM_TO_BOHR

if TYPE_CHECKING:
    from molara.structure.basisset import BasisFunction

__copyright__ = "Copyright 2024, Molara"


class MolecularOrbitals:
    """Class to store molecular orbitals and their information"""

    def __init__(
        self,
        labels: list | None = None,
        energies: list | None = None,
        spins: list | None = None,
        occupations: list | None = None,
        basisfunctions: list | None = None,
        type: str = "cartesian",
    ) -> None:
        """Initialize the MolecularOrbitals class with all their information.

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

        # TODO implement openshell case!
        self.unrestricted = False

        self.coefficients: np.ndarray = np.array([])
        self.coefficients_display: np.ndarray = np.array([])

# Construct transformation matrices for spherical to cartesian transformation
        self.t_sc_d = np.zeros((5, 6), dtype=np.float64)
        self.t_sc_f = np.zeros((7, 10), dtype=np.float64)
        self.t_sc_g = np.zeros((9, 15), dtype=np.float64)
        self.construct_transformation_matrices()

    def set_mo_coefficients(
        self, mo_coefficients: np.ndarray, spherical_order: str = "none"
    ) -> None:
        """Set the coefficients for the molecular orbitals and transform to cartesian ones.

        :param mo_coefficients: np.ndarray: coefficients for the mos
        :param spherical_order: string: spherical order of the coefficients, only molden supported. if none is given the
        coefficients are assumed to be in cartesian order
        """

        self.coefficients_display = mo_coefficients
        if spherical_order == "none":
            self.coefficients = mo_coefficients
        elif spherical_order == "molden":
            self.coefficients = self.spherical_to_cartesian_transformation(mo_coefficients)
        else:
            msg = f"The spherical_order {spherical_order} is not supported."
            raise TypeError(msg)

    def get_mo_value(  # noqa: C901
        self,
        index: int,
        aos: list[BasisFunction],
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
                np.array(electron_position, dtype=np.float64) * ANGSTROM_TO_BOHR,
                np.array(aos[i].position, dtype=np.float64) * ANGSTROM_TO_BOHR,
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

    def construct_transformation_matrices(self) -> None:
        """Construct the transformation matrices for the spherical to cartesian transformation"""

        dxx = 0
        dyy = 1
        dzz = 2
        dxy = 3
        dxz = 4
        dyz = 5

        d0 = 0
        d1c = 1
        d1s = 2
        d2c = 3
        d2s = 4

        fxxx = 0
        fyyy = 1
        fzzz = 2
        fxyy = 3
        fxxy = 4
        fxxz = 5
        fxzz = 6
        fyzz = 7
        fyyz = 8
        fxyz = 9

        f0 = 0
        f1c = 1
        f1s = 2
        f2c = 3
        f2s = 4
        f3c = 5
        f3s = 6

        gxxxx = 0
        gyyyy = 1
        gzzzz = 2
        gxxxy = 3
        gxxxz = 4
        gyyyx = 5
        gyyyz = 6
        gzzzx = 7
        gzzzy = 8
        gxxyy = 9
        gxxzz = 10
        gyyzz = 11
        gxxyz = 12
        gyyxz = 13
        gzzxy = 14

        g0 = 0
        g1c = 1
        g1s = 2
        g2c = 3
        g2s = 4
        g3c = 5
        g3s = 6
        g4c = 7
        g4s = 8

# The normalization takes place here according to Helgaker as well as in the aos.pyx file.
# d orbitals
        transformation_d = np.zeros((5, 6), dtype=np.float64)
        transformation_d[d0, dxx] = -1/2
        transformation_d[d0, dyy] = -1/2
        transformation_d[d0, dzz] = 1

# sqrt(3) is taken into account when calculating the aos values
        transformation_d[d1c, dxz] = 1

# sqrt(3) is taken into account when calculating the aos values
        transformation_d[d1s, dyz] = 1

        transformation_d[d2c, dxx] = np.sqrt(3)/2
        transformation_d[d2c, dyy] = -np.sqrt(3)/2

# sqrt(3) is taken into account when calculating the aos values
        transformation_d[d2s, dxy] = 1

        self.t_sc_d = transformation_d

# f orbitals
        transformation_f = np.zeros((7, 10), dtype=np.float64)
        transformation_f[f0, fzzz] = 1
# sqrt(5) is taken into account when calculating the aos values to yield -3/2
        transformation_f[f0, fxxz] = -3 * np.sqrt(5) / 10
        transformation_f[f0, fyyz] = -3 * np.sqrt(5) / 10

        transformation_f[f1c, fxxx] = -np.sqrt(6) / 4
# sqrt(5) is taken into account when calculating the aos values
        transformation_f[f1c, fxyy] = -np.sqrt(30) / 20
        transformation_f[f1c, fxzz] = np.sqrt(30) / 5

        transformation_f[f1s, fyyy] = -np.sqrt(6) / 4
# sqrt(5) is taken into account when calculating the aos values
        transformation_f[f1s, fxxy] = -np.sqrt(30) / 20
        transformation_f[f1s, fyzz] = np.sqrt(30) / 5

# sqrt(5) is taken into account when calculating the aos values
        transformation_f[f2c, fxxz] = np.sqrt(3) / 2
        transformation_f[f2c, fyyz] = -np.sqrt(3) / 2

# sqrt(15) is taken into account when calculating the aos values
        transformation_f[f2s, fxyz] = 1

# TODO AKS PROF. LÜCHOW WHY AMOLQC DOES THIS DIFFERENTLY? (|m| >= 3)
        transformation_f[f3c, fxxx] = np.sqrt(10) / 4
# sqrt(5) is taken into account when calculating the aos values
        transformation_f[f3c, fxyy] = -3 * np.sqrt(2) / 4

# TODO AKS PROF. LÜCHOW WHY AMOLQC DOES THIS DIFFERENTLY? (|m| >= 3)
        transformation_f[f3s, fyyy] = -np.sqrt(10) / 4
# sqrt(5) is taken into account when calculating the aos values
        transformation_f[f3s, fxxy] = 3 * np.sqrt(2) / 4
        self.t_sc_f = transformation_f

# g orbitals
        transformation_g = np.zeros((9, 15), dtype=np.float64)
        transformation_g[g0, gzzzz] = 1
        transformation_g[g0, gxxxx] = 3 / 8
        transformation_g[g0, gyyyy] = 3 / 8
# sqrt(7) * sqrt(5) / sqrt(3) is taken into account when calculating the aos values
        transformation_g[g0, gxxyy] = 3 * np.sqrt(105) / 140
        transformation_g[g0, gxxzz] = -3 * np.sqrt(105) / 35
        transformation_g[g0, gyyzz] = -3 * np.sqrt(105) / 35

# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g1c, gxxxz] = -3 * np.sqrt(70) / 28
# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g1c, gzzzx] = np.sqrt(70) / 7
# sqrt(7) * sqrt(5) is taken into account when calculating the aos values
        transformation_g[g1c, gyyxz] = -3 * np.sqrt(14) / 28

# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g1s, gyyyz] = -3 * np.sqrt(70) / 28
# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g1s, gzzzy] = np.sqrt(70) / 7
# sqrt(7) * sqrt(5) is taken into account when calculating the aos values
        transformation_g[g1s, gxxyz] = -3 * np.sqrt(14) / 28


        transformation_g[g2c, gxxxx] = -np.sqrt(5) / 4
        transformation_g[g2c, gyyyy] = np.sqrt(5) / 4
# sqrt(7) * sqrt(5) / sqrt(3) is taken into account when calculating the aos values
        transformation_g[g2c, gxxzz] = 3 * np.sqrt(21) / 14
        transformation_g[g2c, gyyzz] = -3 * np.sqrt(21) / 14

# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g2s, gxxxy] = -np.sqrt(35) / 14
        transformation_g[g2s, gyyyx] = -np.sqrt(35) / 14
# sqrt(7) * sqrt(5) is taken into account when calculating the aos values
        transformation_g[g2s, gzzxy] = 3 * np.sqrt(7) / 7

# TODO AKS PROF. LÜCHOW WHY AMOLQC DOES THIS DIFFERENTLY? (|m| >= 3)
# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g3c, gxxxz] = np.sqrt(10) / 4
# sqrt(7) * sqrt(5) is taken into account when calculating the aos values
        transformation_g[g3c, gyyxz] = -3 * np.sqrt(2) / 4

# TODO AKS PROF. LÜCHOW WHY AMOLQC DOES THIS DIFFERENTLY? (|m| >= 3)
# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g3s, gyyyz] = -np.sqrt(10) / 4
# sqrt(7) * sqrt(5) is taken into account when calculating the aos values
        transformation_g[g3s, gxxyz] = 3 * np.sqrt(2) / 4

# TODO AKS PROF. LÜCHOW WHY AMOLQC DOES THIS DIFFERENTLY? (|m| >= 3)
        transformation_g[g4c, gxxxx] = np.sqrt(35) / 8
        transformation_g[g4c, gyyyy] = np.sqrt(35) / 8
# sqrt(7) * sqrt(5) / sqrt(3) is taken into account when calculating the aos values
        transformation_g[g4c, gxxyy] = -3 * np.sqrt(3) / 4

# TODO AKS PROF. LÜCHOW WHY AMOLQC DOES THIS DIFFERENTLY? (|m| >= 3)
# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g4s, gxxxy] = np.sqrt(5) / 2
# sqrt(7) is taken into account when calculating the aos values
        transformation_g[g4s, gyyyx] = -np.sqrt(5) / 2
        self.t_sc_g = transformation_g

    def spherical_to_cartesian_transformation(self,
        mo_coefficients: np.ndarray) -> np.ndarray:
        """Transform spherical coefficients to cartesian coefficients.

        :param mo_coefficients: np.ndarray: coefficients for the mos
        :return: np.ndarray: cartesian coefficients
        """

        new_coefficients = []
        skip_counter = 0
        for mo in mo_coefficients:
            new_coefficients_temp = []
            index = 0
            for atom_basis in self.basisfunctions:
                for bf in atom_basis:
                    if skip_counter > 0:
                        skip_counter -= 1
                        continue
                    if "dxx" in bf:
                        d_coefficients_spherical = mo[index : index + 5]
                        d_coefficients_cart = np.dot(
                            d_coefficients_spherical, self.t_sc_d
                        )
                        new_coefficients_temp.extend(d_coefficients_cart)
                        skip_counter = 5
                        index += 5
                    elif "fxxx" in bf:
                        f_coefficients_spherical = mo[index : index + 7]
                        f_coefficients_cart = np.dot(
                            f_coefficients_spherical, self.t_sc_f
                        )
                        new_coefficients_temp.extend(f_coefficients_cart)
                        skip_counter = 9
                        index += 7
                    elif "gxxxx" in bf:
                        g_coefficients_spherical = mo[index : index + 9]
                        g_coefficients_cart = np.dot(
                            g_coefficients_spherical, self.t_sc_g
                        )
                        new_coefficients_temp.extend(g_coefficients_cart)
                        skip_counter = 14
                        index += 9
                    else:
                        new_coefficients_temp.append(mo[index])
                        index += 1
            new_coefficients.append(new_coefficients_temp)
        return np.array(new_coefficients, dtype=np.float64)
