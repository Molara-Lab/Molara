"""Test the atomic orbital code."""

from __future__ import annotations

from unittest import TestCase

import numpy as np

from molara.eval.aos import calculate_aos
from molara.structure.basisset import BasisSet

__copyright__ = "Copyright 2024, Molara"


class TestAtomicOrbitals(TestCase):
    """Test the molecular orbital code."""

    def setUp(self) -> None:
        """Initialize the program."""
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

    def test_ao_evaluation(self) -> None:
        """Test the calculation of the AO for a given electron position."""
        electron_coords = np.array([0.10154165, 0.465418564, -1.498185465])
        # get the all the different basis functions
        # Generated after comparing the mos with the mos of multiwfn.
        compare_vals = []

        for i in range(len(self.aos)):
            ao = self.aos[i]
            aos_vals = np.zeros(15, dtype=np.float64)
            shell = sum(ao.ijk)
            _ = calculate_aos(
                electron_coords,
                ao.position,
                ao.exponents,
                ao.coefficients,
                ao.norms,
                shell,
                aos_vals,
            )
            compare_vals.append(aos_vals)
        new_compare_vals = np.array(compare_vals)
        reference_sum = 0.6126802927318897
        assert sum(new_compare_vals.flatten()) == reference_sum
