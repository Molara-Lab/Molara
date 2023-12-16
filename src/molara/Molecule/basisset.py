"""Module for the Basisset class."""
from __future__ import annotations

import numpy as np

fact2 = [
    1,
    1,
    2,
    3,
    8,
    15,
    48,
    105,
    384,
    945,
    3840,
    10395,
    46080,
    135135,
    645120,
    2027025,
    10321920,
    34459425,
]


class Basisset:
    """Class to store either an STO or GTO basisset for each atom in the same order as in molecule."""

    def __init__(self, basis_type: str = "None") -> None:
        """Initializes the Basisset class.

        :param basis_type: str.
        :return:
        """
        self.basis_type: str = basis_type
        self.orbitals: dict = {}

        # self.generate_ijk()

    def generate_orbitals(  # noqa: PLR0915
        self,
        shells: list,
        exponents: list,
        coefficients: list,
    ) -> None:
        """Generates the orbitals for the basisset and normalizes the primitive functions.

        :param shells: list of shells
        :param exponents: list of exponents
        :param coefficients: list of coefficients
        :return:
        """
        i = 0
        si = 1
        pi = 1
        di = 1
        fi = 1
        gi = 1
        for shell in shells:
            ijks = generate_ijks(shell)
            if shell == "s":
                self.orbitals[f"s{si}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[0],
                    "norms": normalize_primitive_gtos(ijks[0], exponents[i]),
                }
                si += 1
                i += 1
            elif shell == "p":
                self.orbitals[f"px{pi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[0],
                    "norms": normalize_primitive_gtos(ijks[0], exponents[i]),
                }
                self.orbitals[f"py{pi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[1],
                    "norms": normalize_primitive_gtos(ijks[1], exponents[i]),
                }
                self.orbitals[f"pz{pi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[2],
                    "norms": normalize_primitive_gtos(ijks[2], exponents[i]),
                }
                pi += 1
                i += 1
            elif shell == "d":
                self.orbitals[f"dxx{di}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[0],
                    "norms": normalize_primitive_gtos(ijks[0], exponents[i]),
                }
                self.orbitals[f"dyy{di}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[1],
                    "norms": normalize_primitive_gtos(ijks[1], exponents[i]),
                }
                self.orbitals[f"dzz{di}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[2],
                    "norms": normalize_primitive_gtos(ijks[2], exponents[i]),
                }
                self.orbitals[f"dxy{di}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[3],
                    "norms": normalize_primitive_gtos(ijks[3], exponents[i]),
                }
                self.orbitals[f"dxz{di}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[4],
                    "norms": normalize_primitive_gtos(ijks[4], exponents[i]),
                }
                self.orbitals[f"dyz{di}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[5],
                    "norms": normalize_primitive_gtos(ijks[5], exponents[i]),
                }
                di += 1
                i += 1
            elif shell == "f":
                self.orbitals[f"fxxx{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[0],
                    "norms": normalize_primitive_gtos(ijks[0], exponents[i]),
                }
                self.orbitals[f"fyyy{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[1],
                    "norms": normalize_primitive_gtos(ijks[1], exponents[i]),
                }
                self.orbitals[f"fzzz{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[2],
                    "norms": normalize_primitive_gtos(ijks[2], exponents[i]),
                }
                self.orbitals[f"fxyy{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[3],
                    "norms": normalize_primitive_gtos(ijks[3], exponents[i]),
                }
                self.orbitals[f"fxxy{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[4],
                    "norms": normalize_primitive_gtos(ijks[4], exponents[i]),
                }
                self.orbitals[f"fxxz{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[5],
                    "norms": normalize_primitive_gtos(ijks[5], exponents[i]),
                }
                self.orbitals[f"fxzz{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[6],
                    "norms": normalize_primitive_gtos(ijks[6], exponents[i]),
                }
                self.orbitals[f"fyzz{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[7],
                    "norms": normalize_primitive_gtos(ijks[7], exponents[i]),
                }
                self.orbitals[f"fyyz{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[8],
                    "norms": normalize_primitive_gtos(ijks[8], exponents[i]),
                }
                self.orbitals[f"fxyz{fi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[9],
                    "norms": normalize_primitive_gtos(ijks[9], exponents[i]),
                }
                fi += 1
                i += 1
            elif shell == "g":
                self.orbitals[f"gxxxx{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[0],
                    "norms": normalize_primitive_gtos(ijks[0], exponents[i]),
                }
                self.orbitals[f"gyyyy{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[1],
                    "norms": normalize_primitive_gtos(ijks[1], exponents[i]),
                }
                self.orbitals[f"gzzzz{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[2],
                    "norms": normalize_primitive_gtos(ijks[2], exponents[i]),
                }
                self.orbitals[f"gxxxy{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[3],
                    "norms": normalize_primitive_gtos(ijks[3], exponents[i]),
                }
                self.orbitals[f"gxxxz{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[4],
                    "norms": normalize_primitive_gtos(ijks[4], exponents[i]),
                }
                self.orbitals[f"gyyyx{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[5],
                    "norms": normalize_primitive_gtos(ijks[5], exponents[i]),
                }
                self.orbitals[f"gyyyz{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[6],
                    "norms": normalize_primitive_gtos(ijks[6], exponents[i]),
                }
                self.orbitals[f"gzzzx{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[7],
                    "norms": normalize_primitive_gtos(ijks[7], exponents[i]),
                }
                self.orbitals[f"gzzzy{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[8],
                    "norms": normalize_primitive_gtos(ijks[8], exponents[i]),
                }
                self.orbitals[f"gxxyy{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[9],
                    "norms": normalize_primitive_gtos(ijks[9], exponents[i]),
                }
                self.orbitals[f"gxxzz{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[10],
                    "norms": normalize_primitive_gtos(ijks[10], exponents[i]),
                }
                self.orbitals[f"gyyzz{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[11],
                    "norms": normalize_primitive_gtos(ijks[11], exponents[i]),
                }
                self.orbitals[f"gxxyz{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[12],
                    "norms": normalize_primitive_gtos(ijks[12], exponents[i]),
                }
                self.orbitals[f"gyyxz{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[13],
                    "norms": normalize_primitive_gtos(ijks[13], exponents[i]),
                }
                self.orbitals[f"gzzxy{gi}"] = {
                    "exponents": exponents[i],
                    "coefficients": coefficients[i],
                    "ijk": ijks[14],
                    "norms": normalize_primitive_gtos(ijks[14], exponents[i]),
                }
                gi += 1
                i += 1
            else:
                msg = f"The shell {shell} type is not supported."
                raise TypeError(msg)


def normalize_primitive_gtos(ijk: list, exponents: list[float]) -> list[float]:
    """Normalizes the primitive gaussians.

    :param ijk: list of ijk values
    :param exponents: list of exponents
    :return: normalization factor
    """
    i = ijk[0]
    j = ijk[1]
    k = ijk[2]
    m = i + j + k

    fi = 1 if i == 0 else fact2[2 * i - 1]
    fj = 1 if j == 0 else fact2[2 * j - 1]
    fk = 1 if k == 0 else fact2[2 * k - 1]

    return [
        np.sqrt(
            (2 ** (2 * m + 1.5) * exponent ** (m + 1.5))
            / (fi * fj * fk * np.pi**1.5),
        )
        for exponent in exponents
    ]


def normalize_contracted_gtos(
    ijk: list,
    exponents: list[float],
    coefficients: list[float],
    norms: list[float],
) -> float:
    """Normalizes the contracted gaussians.

    :param ijk: list of ijk values
    :param exponents: list of exponents
    :param coefficients: list of coefficients
    :param norms: list of normalization factors
    :return: normalization factor
    """
    i = ijk[0]
    j = ijk[1]
    k = ijk[2]
    m = i + j + k

    fi = 1 if i == 0 else fact2[2 * i - 1]
    fj = 1 if j == 0 else fact2[2 * j - 1]
    fk = 1 if k == 0 else fact2[2 * k - 1]

    prefactor = (np.pi**1.5 * fi * fj * fk) / (2 ** (m))
    n = 0.0

    for ia in range(len(exponents)):
        for ib in range(len(exponents)):
            n += (coefficients[ia] * coefficients[ib] * norms[ia] * norms[ib]) / (
                exponents[ia] + exponents[ib]
            ) ** (m + 1.5)
    n = n * prefactor

    return n ** (-0.5)


def generate_ijks(shell: str) -> list[list]:
    """Generates the ijk values for the shells.

    :return:
    """
    if shell == "s":
        return [[0, 0, 0]]
    if shell == "p":
        return [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    if shell == "d":
        return [[2, 0, 0], [0, 2, 0], [0, 0, 2], [1, 1, 0], [1, 0, 1], [0, 1, 1]]
    if shell == "f":
        return [
            [3, 0, 0],
            [0, 3, 0],
            [0, 0, 3],
            [1, 2, 0],
            [2, 1, 0],
            [2, 0, 1],
            [1, 0, 2],
            [0, 1, 2],
            [0, 2, 1],
            [1, 1, 1],
        ]
    if shell == "g":
        return [
            [4, 0, 0],
            [0, 4, 0],
            [0, 0, 4],
            [3, 1, 0],
            [3, 0, 1],
            [1, 3, 0],
            [0, 3, 1],
            [1, 0, 3],
            [0, 1, 3],
            [2, 2, 0],
            [2, 0, 2],
            [0, 2, 2],
            [2, 1, 1],
            [1, 2, 1],
            [1, 1, 2],
        ]
    msg = f"The shell {shell} type is not supported."
    raise TypeError(msg)
