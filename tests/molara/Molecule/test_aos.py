"""Test the basis set and check if normalized."""

from unittest import TestCase

from numpy.testing import assert_array_equal
import numpy as np
from molara.Molecule.io.importer import GeneralImporter
from molara.Eval.aos import calculate_aos
import matplotlib.pyplot as plt


class TestBasisset(TestCase):
    """Test the Basisset class."""

    def setUp(self) -> None:
        """Set up a basisset."""
        importer = GeneralImporter("../../input_files/molden/h2_cas.molden")
        molecules = importer.load()
        self.basisset = molecules.mols[0].atoms[0].basis_set
        self.electron_position = np.array([0.1, -0.234, 0.5])
        self.nuclear_position = np.array([0.0, 0.0, 0.0])

    def test_normalized(self) -> None:
        """Test if the basis set is normalized."""
        s = []
        p = []
        d = []
        f = []
        g = []
        pi = 0
        di = 0
        fi = 0
        gi = 0

        for orb in self.basisset.orbitals:
            if orb[0] == "s":
                s.append(
                    calculate_aos(
                        self.electron_position,
                        self.nuclear_position,
                        self.basisset.orbitals[orb].exponents,
                        self.basisset.orbitals[orb].coefficients,
                        orb[0],
                    )
                )
            elif orb[0] == "p" and pi % 3 == 0:
                p.append(
                    calculate_aos(
                        self.electron_position,
                        self.nuclear_position,
                        self.basisset.orbitals[orb].exponents,
                        self.basisset.orbitals[orb].coefficients,
                        orb[0],
                    )
                )
                pi += 1
        # assert False
