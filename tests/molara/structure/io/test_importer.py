"""Test the importer.py module.

Note that some functionality of MoldenImporter is also tested in
test_aos.py, test_basisset.py, and test_mos.py.
Some functionality of XyzImporter is also tested in
test_structure_widget.py and test_main_window.py.
"""

from __future__ import annotations

from unittest import TestCase

import numpy as np
import pytest
from molara.structure.io.importer import FileFormatError, MoldenImporter


class TestMoldenImporter(TestCase):
    """Test the MoldenImporter class."""

    def setUp(self) -> None:
        """Set up the MoldenImporter object."""
        self.directory_input_files = "tests/input_files/molden"
        self.importer = MoldenImporter(f"{self.directory_input_files}/f2.molden")
        self.structure = self.importer.load()

    def test_get_atoms(self) -> None:
        """Test the get_atoms method."""
        msg = "No unit specified in molden Atoms input."
        with pytest.raises(FileFormatError, match=msg):
            self.importer.get_atoms(["abcdefg"])

        lines = [
            "[Atoms] Angs",
            "H 1 1 0.0 -1.0 1.1",
            "C 2 6 -4.0 2.0 3.2",
        ]
        atomic_numbers, coordinates = self.importer.get_atoms(lines)
        assert atomic_numbers == [1, 6]
        assert coordinates == [[0.0, -1.0, 1.1], [-4.0, 2.0, 3.2]]

        lines = [
            "[Atoms] AU",
            "Ir 1 77 2.0 1.4 10.1",
            "Mg 2 12 3.0 -0.2 4.4",
        ]
        atomic_numbers, coordinates = self.importer.get_atoms(lines)
        assert atomic_numbers == [77, 12]
        bohr_to_angstrom = 5.29177210903e-1
        assert np.isclose(
            coordinates,
            np.array([[2.0, 1.4, 10.1], [3.0, -0.2, 4.4]]) * bohr_to_angstrom,
        ).all()

    def test_get_basisset(self) -> None:
        """Test the get_basisset method."""
        lines = [
            "[STO]",
        ]
        msg = "STO type not implemented."
        with pytest.raises(FileFormatError, match=msg):
            self.importer.get_basisset(lines)
