"""Test the Mos class."""

from unittest import TestCase

from numpy.testing import assert_array_equal
import numpy as np
from molara.Molecule.io.importer import GeneralImporter
from molara.Eval.aos import calculate_aos
import matplotlib.pyplot as plt


class TestMos(TestCase):
    """Test the Basisset class."""

    def setUp(self) -> None:
        """Set up a basisset."""
        importer = GeneralImporter("../../input_files/molden/h2_cas.molden")
        molecules = importer.load()
        self.mos = molecules.mols[0].mos
        self.aos = molecules.mols[0].aos

    def test_mos(self) -> None:
        """Test if the mos are correct."""
        x = np.linspace(-5, 5, 1000)
        y = []

        print()
        for i in x:
            y.append(self.mos.calculate_mo_cartesian(1, self.aos, np.array([0.0, 0.0, i])))

        plt.plot(x, y)
        plt.show()
        assert False
