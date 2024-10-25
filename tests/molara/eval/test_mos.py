"""Test the molecular orbital code."""

from __future__ import annotations

from unittest import TestCase

import numpy as np

from molara.structure.io.importer import GeneralImporter

__copyright__ = "Copyright 2024, Molara"


class TestMolecularOrbitals(TestCase):
    """Test the molecular orbital code."""

    def setUp(self) -> None:
        """Initialize the program."""
        pass

    def test_mo_evaluation(self) -> None:
        """Test the calculation of the MO for a given electron position."""
        path = "examples/molden/h2o.molden"
        importer = GeneralImporter(path)
        molecule = importer.load().mols[0]
        molecule.center_coordinates()
        self.mos = molecule.mos
        self.aos = molecule.basis_set
        val = self.mos.get_mo_value(1, self.aos, np.array([0.10154165, 0.465418564, -1.498185465]))
        # Generated after comparing the mos with the mos of multiwfn.
        reference = 0.009741653204777932
        assert val == reference
        
        path = "examples/molden/SPDFG_orbitals.molden"
        importer = GeneralImporter(path)
        molecule = importer.load().mols[0]
        molecule.center_coordinates()
        self.mos = molecule.mos
        self.aos = molecule.basis_set
        val = self.mos.get_mo_value(20, self.aos, np.array([0.10154165, 0.465418564, -1.498185465]))
        # Generated after comparing the mos with the mos of multiwfn.
        reference = 0.00041210939470218426
        assert val == reference
