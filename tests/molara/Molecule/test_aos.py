"""Test the aos module."""
from __future__ import annotations

from unittest import TestCase

import matplotlib.pyplot as plt
import numpy as np
from molara.Eval.aos import calculate_aos
from molara.Molecule.io.importer import GeneralImporter
from numpy.testing import assert_array_equal


class TestAos(TestCase):
    """Test the Aos class."""

    def setUp(self) -> None:
        """Set up a basisset."""
        importer = GeneralImporter("tests/input_files/molden/h2_cas.molden")
        molecules = importer.load()
        self.basisset = molecules.mols[0].atoms[0].basis_set
        self.electron_position = np.array([0.1, -0.234, 0.5])
        self.nuclear_position = np.array([0.0, 0.0, 0.0])

    def test_aos(self) -> None:
        """Test if the aos are correct.

        Tests still need to be implemented.
        """
        s = []
        p = []
        pi = 0

        for orb in self.basisset.orbitals:
            if orb[0] == "s":
                s.append(
                    calculate_aos(
                        self.electron_position,
                        self.nuclear_position,
                        self.basisset.orbitals[orb].exponents,
                        self.basisset.orbitals[orb].coefficients,
                        0,
                    ),
                )
            elif orb[0] == "p" and pi % 3 == 0:
                p.append(
                    calculate_aos(
                        self.electron_position,
                        self.nuclear_position,
                        self.basisset.orbitals[orb].exponents,
                        self.basisset.orbitals[orb].coefficients,
                        1,
                    ),
                )
                pi += 1
        # assert False
