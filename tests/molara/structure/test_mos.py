"""Test the Mos class."""

from __future__ import annotations

import sys
import unittest
from unittest import TestCase

import numpy as np
from numpy.testing import assert_allclose

from molara.structure.io.importer import GeneralImporter

__copyright__ = "Copyright 2024, Molara"


@unittest.skipIf(sys.version_info <= (3, 11), "Test skipped for Python versions <= 3.11 due to compatibility issues.")
class TestMos(TestCase):
    """Test the Mos class."""

    def setUp(self) -> None:
        """Set up a basisset."""
        importer = GeneralImporter("tests/input_files/molden/h2_cas.molden")
        molecules = importer.load()
        self.mos = molecules.mols[0].mos
        self.aos = molecules.mols[0].basis_set

    def test_mos_metadata(self) -> None:
        """Test if loaded MO metadata and array dimensions are consistent."""
        assert self.mos.coefficients.shape == (12, 12)
        assert self.mos.coefficients_display.shape == (12, 12)
        assert len(self.mos.energies) == self.mos.coefficients.shape[1]
        assert len(self.mos.occupations) == self.mos.coefficients.shape[1]
        assert len(self.mos.labels) == self.mos.coefficients.shape[1]
        assert len(self.mos.spins) == self.mos.coefficients.shape[1]

    def test_get_mo_value(self) -> None:
        """Test deterministic MO values at a fixed electron position."""
        electron_position = np.array([0.1, -0.234, 0.5])
        expected_values = np.array(
            [
                0.2586827696049223,
                -0.35871647879438867,
                -0.0836466538035357,
            ],
        )
        calculated_values = np.array(
            [self.mos.get_mo_value(i, self.aos, electron_position) for i in range(3)],
        )
        assert_allclose(calculated_values, expected_values, rtol=0, atol=1e-12)

    def test_calculate_cut_offs(self) -> None:
        """Test MO cutoff distances for the first molecular orbital."""
        expected_cutoffs = np.array(
            [
                29.949748743718594,
                35.577889447236184,
                11.658291457286433,
                32.562814070351756,
                29.949748743718594,
                35.577889447236184,
                11.658291457286433,
                32.562814070351756,
            ],
        )
        cutoffs = self.mos.calculate_cut_offs(self.aos, orbital=0)
        assert cutoffs.shape == (8,)
        assert_allclose(cutoffs, expected_cutoffs, rtol=0, atol=1e-12)
