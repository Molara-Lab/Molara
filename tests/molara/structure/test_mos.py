"""Test the Mos class."""

from __future__ import annotations

from unittest import TestCase

import numpy as np

from molara.structure.io.importer import GeneralImporter

__copyright__ = "Copyright 2024, Molara"


class TestMos(TestCase):
    """Test the Mos class."""

    def setUp(self) -> None:
        """Set up a basisset."""
        importer = GeneralImporter("tests/input_files/molden/h2_cas.molden")
        molecules = importer.load()
        self.mos = molecules.mols[0].mos
        self.aos = molecules.mols[0].aos

    def test_mos(self) -> None:
        """Test if the mos are correct.

        Tests still need to be implemented.
        """
        np.linspace(-5, 5, 1000)

        # print()
        # [self.mos.calculate_mo_cartesian(1, self.aos, np.array([0.0, 0.0, i])) for i in x]

        # plt.plot(x, y)
        # plt.show()
        assert True
