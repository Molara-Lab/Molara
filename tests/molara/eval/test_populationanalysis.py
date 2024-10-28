"""Test the populationanalysis code."""

from __future__ import annotations

from unittest import TestCase

from molara.eval.populationanalysis import PopulationAnalysis
from molara.structure.io.importer import GeneralImporter

__copyright__ = "Copyright 2024, Molara"


class TestPopulationanalysis(TestCase):
    """Test the molecular orbital code."""

    def setUp(self) -> None:
        """Initialize the program."""

    def test_spherical(self) -> None:
        """Test spherical MO analysis."""
        path = "examples/molden/h2o.molden"
        importer = GeneralImporter(path)
        molecule = importer.load().mols[0]
        molecule.center_coordinates()
        pop_analysis = PopulationAnalysis(molecule)
        exact_number_of_electrons = 10.0
        calculated_number_of_electrons = 10.00000007019219
        assert pop_analysis.number_of_electrons == exact_number_of_electrons
        assert pop_analysis.calculated_number_of_electrons == calculated_number_of_electrons

    def test_cartesian(self) -> None:
        """Test cartesian MO analysis."""
        path = "examples/molden/benzene.molden"
        importer = GeneralImporter(path)
        molecule = importer.load().mols[0]
        molecule.center_coordinates()
        pop_analysis = PopulationAnalysis(molecule)
        exact_number_of_electrons = 42.0
        calculated_number_of_electrons = 42.00000051583379
        assert pop_analysis.number_of_electrons == exact_number_of_electrons
        assert pop_analysis.calculated_number_of_electrons == calculated_number_of_electrons
