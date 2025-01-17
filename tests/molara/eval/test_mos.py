"""Test the molecular orbital code."""

from __future__ import annotations

from unittest import TestCase

import numpy as np

from molara.structure.basisset import BasisSet
from molara.structure.molecularorbitals import MolecularOrbitals

__copyright__ = "Copyright 2024, Molara"


class TestMolecularOrbitals(TestCase):
    """Test the molecular orbital code."""

    def setUp(self) -> None:
        """Initialize the program."""

    def test_mo_evaluation(self) -> None:
        """Test the calculation of the MO for a given electron position."""
        basis_set = BasisSet()
        coeffs = [[0.432423, 1.41341, 5, 0.00001]] * 5
        exps = [[0.1, 01.2, 2.3, 10.4]] * 5
        position = np.array([0.0, 0.0, 0.0])
        basis_set.generate_basis_functions(
            ["s", "p", "d", "f", "g"],
            coeffs,
            exps,
            position,
        )
        self.aos = []
        for basis_function in basis_set.basis_functions.values():
            self.aos.append(basis_function)

        mos = MolecularOrbitals()
        # fill array with numbers
        mos.coefficients = np.array(
            [
                [
                    0.432423,
                    3.41341,
                    5,
                    0.00001,
                    0.432423,
                    -1.41341,
                    5,
                    0.524001,
                    0.432423,
                    1.41341,
                    5,
                    3.00001,
                    0.432423,
                    -1.41341,
                    5,
                    0.450001,
                    0.432423,
                    1.41341,
                    5,
                    0.00001,
                    0.434442423,
                    1.243423341,
                    5,
                    0.00001,
                    0.432423,
                    1.41341,
                    5,
                    0.00001,
                    0.434442423,
                    1.243423341,
                    5,
                    0.00001,
                    0.432423,
                    1.41341,
                    -1.2345,
                ],
            ],
        ).T
        val = mos.get_mo_value(0, self.aos, np.array([0.10154165, 0.465418564, -1.498185465]))
        # Generated after comparing the mos with the mos of multiwfn.
        compared_val = 0.00907188975065531
        threshold = 1e-9
        assert np.abs(val - compared_val) < threshold
