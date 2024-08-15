"""Test imports of crystal structures from various file formats."""

from __future__ import annotations

from importlib.util import find_spec
from unittest import TestCase, mock

import pytest
from numpy.testing import assert_array_equal

from molara.structure.crystals import Crystals
from molara.structure.io.exceptions import FileFormatError
from molara.structure.io.importer import PymatgenImporter, VasprunImporter


@pytest.mark.skipif(not find_spec("pymatgen"), reason="pymatgen not installed")
class TestPymatgenImporter(TestCase):
    """Test the PymatgenImporter class."""

    def setUp(self) -> None:
        """Set up the PymatgenImporter object."""
        self.importer = PymatgenImporter("examples/POSCAR/BN_POSCAR")
        self.structure = self.importer.load()

    def test_load(self) -> None:
        """Test the load method of the PymatgenImporter class."""
        assert isinstance(self.structure, Crystals)
        current_mol = self.structure.get_current_mol()
        assert_array_equal(current_mol.atomic_nums_unitcell, [5, 7])
        assert_array_equal(
            current_mol.coords_unitcell,
            [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]],
        )


class TestVasprunImporter(TestCase):
    """Test the VasprunImporter class."""

    def setUp(self) -> None:
        """Set up the VasprunImporter object."""
        if find_spec("pymatgen"):
            self.importer = VasprunImporter("tests/output_files/vasp/vasprun_Si.xml")
            with pytest.warns(UserWarning, match="No POTCAR file with matching TITEL fields was found in"):
                self.structure = self.importer.load()
        else:
            with pytest.raises(FileFormatError):
                self.importer = VasprunImporter("tests/output_files/vasp/vasprun_Si.xml")

    @pytest.mark.skipif(not find_spec("pymatgen"), reason="pymatgen not installed")
    def test_load(self) -> None:
        """Test the load method of the VasprunImporter class."""
        assert isinstance(self.structure, Crystals)
        current_mol = self.structure.get_current_mol()
        assert_array_equal(current_mol.atomic_nums_unitcell, [14])
        assert_array_equal(
            current_mol.coords_unitcell,
            [[0.0, 0.0, 0.0]],
        )

        # test case that pymatgen is not installed
        with mock.patch("builtins.__import__", side_effect=ImportError):  # noqa: SIM117
            with pytest.raises(FileFormatError):
                VasprunImporter("tests/output_files/vasp/vasprun_Si.xml").load()
