"""Module for the Basisset class."""

from __future__ import annotations

import numpy as np

__copyright__ = "Copyright 2024, Molara"

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
    """Class for either a STO or GTO basisset for each atom in the same order as in molecule.

    GTOs are gaussian type orbitals, STOs are slater type orbitals.
    """

    def __init__(self, basis_type: str = "None") -> None:
        """Initialize the Basisset class.

        :param basis_type: str.
        :return:
        """
        self.basis_type: str = basis_type
        self.orbitals: dict = {}
        self.orbitals_list: list = []

        # self.generate_ijk()

    def generate_orbitals(  # noqa: C901
        self,
        shells: list,
        exponents: list,
        coefficients: list,
        position: np.ndarray,
    ) -> None:
        """Generate the orbitals for the basisset and normalizes the primitive functions.

        :param shells: list of shells
        :param exponents: list of exponents
        :param coefficients: list of coefficients
        :param position: list of positions
        :return:
        """
        i = 0
        si = 1
        pi = 1
        di = 1
        fi = 1
        gi = 1
        orbs = [
            [
                "s",
            ],
            [
                "px",
                "py",
                "pz",
            ],
            [
                "dxx",
                "dyy",
                "dzz",
                "dxy",
                "dxz",
                "dyz",
            ],
            [
                "fxxx",
                "fyyy",
                "fzzz",
                "fxyy",
                "fxxy",
                "fxxz",
                "fxzz",
                "fyzz",
                "fyyz",
                "fxyz",
            ],
            [
                "gxxxx",
                "gyyyy",
                "gzzzz",
                "gxxxy",
                "gxxxz",
                "gyyyx",
                "gyyyz",
                "gzzzx",
                "gzzzy",
                "gxxyy",
                "gxxzz",
                "gyyzz",
                "gxxyz",
                "gyyxz",
                "gzzxy",
            ],
        ]
        for shell in shells:
            ijks: list[list] | np.ndarray = generate_ijks(shell)
            coefficients[i] = np.array(coefficients[i])
            exponents[i] = np.array(exponents[i])
            ijks = np.array(ijks, dtype=int)
            if shell == "s":
                self.orbitals[f"s{si}"] = Orbital(
                    ijks[0],
                    exponents[i],
                    coefficients[i],
                    position,
                )
                si += 1
                i += 1
            elif shell == "p":
                for j, orb in enumerate(orbs[1]):
                    self.orbitals[f"{orb}{pi}"] = Orbital(
                        ijks[j],
                        exponents[i],
                        coefficients[i],
                        position,
                    )
                pi += 1
                i += 1
            elif shell == "d":
                for j, orb in enumerate(orbs[2]):
                    self.orbitals[f"{orb}{di}"] = Orbital(
                        ijks[j],
                        exponents[i],
                        coefficients[i],
                        position,
                    )
                di += 1
                i += 1
            elif shell == "f":
                for j, orb in enumerate(orbs[3]):
                    self.orbitals[f"{orb}{fi}"] = Orbital(
                        ijks[j],
                        exponents[i],
                        coefficients[i],
                        position,
                    )
                fi += 1
                i += 1
            elif shell == "g":
                for j, orb in enumerate(orbs[4]):
                    self.orbitals[f"{orb}{gi}"] = Orbital(
                        ijks[j],
                        exponents[i],
                        coefficients[i],
                        position,
                    )
                gi += 1
                i += 1
            else:
                msg = f"The shell {shell} type is not supported."
                raise TypeError(msg)
            self.orbitals_list = list(self.orbitals.values())


class Orbital:
    """Class to store either an STO or GTO."""

    def __init__(
        self,
        ijk: np.ndarray,
        exponents: np.ndarray,
        coefficients: np.ndarray,
        position: np.ndarray,
    ) -> None:
        """Initialize the orbital class.

        :param ijk: list of ijk values
        :param exponents: list of exponents
        :param coefficients: list of coefficients
        :param position: position of the orbital
        :return:
        """
        self.ijk = ijk
        self.exponents = exponents
        self.norms = calculate_normalization_primitive_gtos(ijk, exponents)
        self.coefficients = coefficients * calculate_normalization_contracted_gtos(
            ijk,
            exponents,
            coefficients,
            self.norms,
        )
        self.position = position


def calculate_normalization_primitive_gtos(
    ijk: np.ndarray,
    exponents: np.ndarray,
) -> np.ndarray:
    """Normalize the primitive gaussians.

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

    return np.array(
        [
            np.sqrt(
                (2 ** (2 * m + 1.5) * exponent ** (m + 1.5)) / (fi * fj * fk * np.pi**1.5),
            )
            for exponent in exponents
        ],
    )


def calculate_normalization_contracted_gtos(
    ijk: np.ndarray,
    exponents: np.ndarray,
    coefficients: np.ndarray,
    norms: np.ndarray,
) -> float:
    """Normalize the contracted gaussians.

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
            n += (coefficients[ia] * coefficients[ib] * norms[ia] * norms[ib]) / (exponents[ia] + exponents[ib]) ** (
                m + 1.5
            )
    n = n * prefactor

    return n ** (-0.5)


def generate_ijks(shell: str) -> list[list]:
    """Generate the ijk values for the shells.

    :param shell: name of the atomic orbital shell (s/p/d/f)
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
