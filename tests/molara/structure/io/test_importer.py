"""Test the importer.py module.

Note that some functionality of MoldenImporter is also tested in
test_aos.py, test_basisset.py, and test_mos.py.
Some functionality of XyzImporter is also tested in
test_structure_widget.py and test_main_window.py.
"""

from __future__ import annotations

from unittest import TestCase, mock

import numpy as np
import pytest

from molara.structure.io.importer import (
    FileFormatError,
    GeneralImporter,
    MoldenImporter,
    QmImporter,
    XyzImporter,
)
from molara.structure.molecule import Molecule
from molara.structure.molecules import Molecules


class TestXyzImporter(TestCase):
    """Test the XyzImporter class."""

    def setUp(self) -> None:
        """Set up the XyzImporter object."""

    def test_load(self) -> None:
        """Test the load method of the XyzImporter class."""
        # test case in which elements are specified as atomic numbers,
        # rather than symbols (not in all lines, but in some)
        self.directory_input_files = "tests/input_files/xyz"
        self.importer = XyzImporter(f"{self.directory_input_files}/pentane_elements_numeric.xyz")
        structures = self.importer.load()
        assert isinstance(structures, Molecules)
        structure = structures.get_current_mol()
        assert isinstance(structure, Molecule)
        assert (structure.atomic_numbers == np.array([6, 1, 1, 6, 1, 1, 6, 1, 1, 1, 6, 1, 1, 6, 1, 1, 1])).all()


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


class TestQmImporter(TestCase):
    """Test the QmImporter class."""

    def setUp(self) -> None:
        """Set up the QmImporter object."""

    def test_init(self) -> None:
        """Test the __init__ method."""
        # test case that cclib is not installed
        msg = "Could not import cclib."
        with mock.patch("builtins.__import__", side_effect=ImportError):  # noqa: SIM117
            with pytest.raises(FileFormatError, match=msg):
                QmImporter("tests/does/not/matter/if/path/exists/file.type").load()


class TestGeneralImporter(TestCase):
    """Test the GeneralImporter class."""

    def setUp(self) -> None:
        """Set up the GeneralImporter object."""

    def test_init(self) -> None:
        """Test the __init__ method."""
        # test case that cclib is not installed
        msg = "Could not open file."
        with mock.patch("builtins.__import__", side_effect=ImportError):  # noqa: SIM117
            with pytest.raises(FileFormatError, match=msg):
                GeneralImporter("tests/does/not/matter/if/path/exists/file.unknowntype").load()
