"""Test the basis set and check if normalized."""
from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import TestCase

import numpy as np
from molara.Structure.io.importer import GeneralImporter
from numpy.testing import assert_array_almost_equal_nulp

if TYPE_CHECKING:
    from molara.Structure.basisset import Orbital

__copyright__ = "Copyright 2024, Molara"


class TestBasisset(TestCase):
    """Test the Basisset class."""

    def setUp(self) -> None:
        """Set up a basisset."""
        importer = GeneralImporter("tests/input_files/molden/h2_cas.molden")
        molecules = importer.load()
        self.basisset = molecules.mols[0].atoms[0].basis_set
        self.correct_matrix = np.array(
            [
                [1.0, 0.9695444742892854, 0.7785233616946461, 0.0, 0.0, 0.0],
                [
                    0.9695444742892855,
                    0.9999999999999999,
                    0.8972992962394406,
                    0.0,
                    0.0,
                    0.0,
                ],
                [
                    0.7785233616946463,
                    0.8972992962394406,
                    0.9999999999999999,
                    0.0,
                    0.0,
                    0.0,
                ],
                [0.0, 0.0, 0.0, 0.9999999999999999, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.9999999999999999, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.9999999999999999],
            ],
        )

    def test_normalized(self) -> None:
        """Test if the basis set is normalized."""
        overlap_matrix = np.zeros(
            (len(self.basisset.orbitals), len(self.basisset.orbitals)),
        )
        for i, orb1 in enumerate(self.basisset.orbitals):
            for j, orb2 in enumerate(self.basisset.orbitals):
                overlap_matrix[i, j] = contracted_overlap(
                    self.basisset.orbitals[orb1],
                    self.basisset.orbitals[orb2],
                    np.array([0.0, 0.0, 0.0]),
                    np.array([0.0, 0.0, 0.0]),
                )
        assert_array_almost_equal_nulp(overlap_matrix, self.correct_matrix, 2)


def hermite_coefs(
    i: int, j: int, t: int, qx: float, a: float, b: float
) -> float:  # noqa: PLR0913
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
        return np.exp(-q * qx * qx)  # K_AB elif j == 0:

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
    """Evaluates overlap integral between two Gaussians.

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
    a: Orbital,
    b: Orbital,
    a_xyz: np.ndarray,
    b_xyz: np.ndarray,
) -> float:
    """Evaluates overlap between two contracted Gaussians.

    Returns a float.
    :param a: contracted Gaussian 'a', BasisFunction object
    :param b: contracted Gaussian 'b', BasisFunction object
    :param a_xyz: list containing origin of contracted Gaussian 'a'
    :param b_xyz: list containing origin of contracted Gaussian 'b'
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
