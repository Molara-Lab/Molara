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


class BasisSet:
    """Class for either an STO or GTO basis set for each atom, in the same order as in the molecule.

    GTOs are Gaussian-type orbitals; STOs are Slater-type orbitals.
    """

    def __init__(self, basis_type: str = "None") -> None:
        """Initialize the Basisset class.

        :param basis_type: Can be either GTO or STO. This will be worked on in the future, currently only GTOs.
        :return:
        """
        self.basis_type: str = basis_type
        self.basis_functions: dict = {}

    def generate_basis_functions(  # noqa: C901
        self,
        shells: list,
        exponents: list,
        coefficients: list,
        position: np.ndarray,
        normalization_mode: str = "none",
    ) -> None:
        """Generate the basis functions for the basis set and normalizes the primitive functions if needed.

        :param shells: list of shells (can be s, p, d, f, or g)
        :param exponents: list of exponents of the primitive Gauss functions
        :param coefficients: list of the contraction coefficients of the primitive Gauss functions
        :param position: list of the centers of the primitive Gauss functions
        :param normalization_mode: mode for normalization of the basis functions some programs prenormalize
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
                self.basis_functions[f"s{si}"] = BasisFunction(
                    ijks[0],
                    exponents[i],
                    coefficients[i],
                    position,
                    normalization_mode,
                )
                si += 1
                i += 1
            elif shell == "p":
                for j, orb in enumerate(orbs[1]):
                    self.basis_functions[f"{orb}{pi}"] = BasisFunction(
                        ijks[j],
                        exponents[i],
                        coefficients[i],
                        position,
                        normalization_mode,
                    )
                pi += 1
                i += 1
            elif shell == "d":
                for j, orb in enumerate(orbs[2]):
                    self.basis_functions[f"{orb}{di}"] = BasisFunction(
                        ijks[j],
                        exponents[i],
                        coefficients[i],
                        position,
                        normalization_mode,
                    )
                di += 1
                i += 1
            elif shell == "f":
                for j, orb in enumerate(orbs[3]):
                    self.basis_functions[f"{orb}{fi}"] = BasisFunction(
                        ijks[j],
                        exponents[i],
                        coefficients[i],
                        position,
                        normalization_mode,
                    )
                fi += 1
                i += 1
            elif shell == "g":
                for j, orb in enumerate(orbs[4]):
                    self.basis_functions[f"{orb}{gi}"] = BasisFunction(
                        ijks[j],
                        exponents[i],
                        coefficients[i],
                        position,
                        normalization_mode,
                    )
                gi += 1
                i += 1
            else:
                msg = f"The shell {shell} type is not supported."
                raise TypeError(msg)


class BasisFunction:
    """Class to store a GTO."""

    def __init__(
        self,
        ijk: np.ndarray,
        exponents: np.ndarray,
        coefficients: np.ndarray,
        position: np.ndarray,
        normalization_mode: str,
    ) -> None:
        """Initialize the BasisFunction class.

        :param ijk: list of ijk values
        :param exponents: list of exponents
        :param coefficients: list of coefficients
        :param position: position of the orbital
        :param normalization_mode: mode for normalization of the basis functions some programs prenormalize
        :return:
        """
        self.position = position
        self.ijk = ijk
        self.exponents = exponents
        self.norms = np.zeros(len(coefficients))

        if normalization_mode == "orca":
            self.norms[:] = 1.0
        elif normalization_mode == "molpro":
            self.norms[:] = calculate_normalization_primitive_gtos(ijk, exponents)
        elif normalization_mode == "none":
            # maybe create warning class and print a warning here
            self.norms[:] = calculate_normalization_primitive_gtos(ijk, exponents)

        self.coefficients = coefficients * calculate_normalization_contracted_gtos(
            ijk,
            exponents,
            coefficients,
            self.norms,
        )


def hermite_coefs(  # noqa: PLR0913
    i: int,
    j: int,
    t: int,
    qx: float,
    a: float,
    b: float,
) -> float:
    """Recursive definition of Hermite Gaussian coefficients.

    Returns a float.
    :param i: orbital angular momentum number on Gaussian 'a'
    :param j: orbital angular momentum number on Gaussian 'b'
    :param t: number nodes in Hermite (depends on type of integral,
                e.g. always zero for overlap integrals)
    :param qx: distance between origins of Gaussian 'a' and 'b'
    :param a: orbital exponent on Gaussian 'a' (e.g. alpha in the text)
    :param b: orbital exponent on Gaussian 'b' (e.g. beta in the text)
    """
    p = a + b
    q = a * b / p
    if (t < 0) or (t > (i + j)):
        return 0.0  # out of bounds for t
    if i == j == t == 0:
        # base case
        return np.exp(-q * qx * qx)  # K_AB

    if j == 0:
        # decrement index i
        return (
            (1 / (2 * p)) * hermite_coefs(i - 1, j, t - 1, qx, a, b)
            - (q * qx / a) * hermite_coefs(i - 1, j, t, qx, a, b)
            + (t + 1) * hermite_coefs(i - 1, j, t + 1, qx, a, b)
        )

    # decrement index j
    return (
        (1 / (2 * p)) * hermite_coefs(i, j - 1, t - 1, qx, a, b)
        + (q * qx / b) * hermite_coefs(i, j - 1, t, qx, a, b)
        + (t + 1) * hermite_coefs(i, j - 1, t + 1, qx, a, b)
    )


def primitive_overlap(  # noqa: PLR0913
    a: float,
    lmn1: np.ndarray,
    a_xyz: np.ndarray,
    b: float,
    lmn2: np.ndarray,
    b_xyz: np.ndarray,
) -> float:
    """Evaluate overlap integral between two Gaussians.

    Returns a float.
    :param a: orbital exponent on Gaussian 'a' (e.g. alpha in the text)
    :param b: orbital exponent on Gaussian 'b' (e.g. beta in the text)
    :param lmn1: int tuple containing orbital angular momentum (e.g. (1,0,0))
          for Gaussian 'a'
    :param lmn2: int tuple containing orbital angular momentum for Gaussian 'b'
    :param a_xyz: list containing origin of Gaussian 'a', e.g. [1.0, 2.0, 0.0]
    :param b_xyz: list containing origin of Gaussian 'b'
    """
    l1, m1, n1 = lmn1  # shell angular momentum on Gaussian 'a'
    l2, m2, n2 = lmn2  # shell angular momentum on Gaussian 'b'

    s1 = hermite_coefs(l1, l2, 0, a_xyz[0] - b_xyz[0], a, b)  # X
    s2 = hermite_coefs(m1, m2, 0, a_xyz[1] - b_xyz[1], a, b)  # Y
    s3 = hermite_coefs(n1, n2, 0, a_xyz[2] - b_xyz[2], a, b)  # Z
    return s1 * s2 * s3 * np.power(np.pi / (a + b), 1.5)


def contracted_overlap(
    a: BasisFunction,
    b: BasisFunction,
    a_xyz: np.ndarray,
    b_xyz: np.ndarray,
) -> float:
    """Evaluate overlap between two contracted Gaussians.

    Returns a float.
    :param a: contracted Gaussian 'a', BasisFunction object
    :param b: contracted Gaussian 'b', BasisFunction object
    :param a_xyz: list containing origin of contracted Gaussian 'a' in atomic units
    :param b_xyz: list containing origin of contracted Gaussian 'b' in atomic units
    :return: overlap between contracted Gaussians 'a' and 'b'
    """
    s = 0.0
    for ia, ca in enumerate(a.coefficients):
        for ib, cb in enumerate(b.coefficients):
            s += (
                a.norms[ia]
                * b.norms[ib]
                * ca
                * cb
                * primitive_overlap(
                    a.exponents[ia],
                    a.ijk,
                    a_xyz,
                    b.exponents[ib],
                    b.ijk,
                    b_xyz,
                )
            )
    return s


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
    n *= prefactor

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
