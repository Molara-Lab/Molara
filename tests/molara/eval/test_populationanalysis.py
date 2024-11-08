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
        assert pop_analysis.number_of_electrons == 10.0
        assert pop_analysis.calculated_number_of_electrons == 9.999999999981455

    def test_cartesian(self) -> None:
        """Test cartesian MO analysis."""
        path = "examples/molden/benzene.molden"
        importer = GeneralImporter(path)
        molecule = importer.load().mols[0]
        molecule.center_coordinates()
        pop_analysis = PopulationAnalysis(molecule)
        assert pop_analysis.number_of_electrons == 42.0
        assert pop_analysis.calculated_number_of_electrons == 41.999999999828034
