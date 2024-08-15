"""Test imports of crystal structures from various file formats."""

from __future__ import annotations

from importlib.util import find_spec
from typing import TYPE_CHECKING
from unittest import TestCase, mock

import pytest
from numpy.testing import assert_almost_equal, assert_array_equal

from molara.structure.crystals import Crystals
from molara.structure.io.exceptions import FileFormatError
from molara.structure.io.importer import PoscarImporter, PymatgenImporter, VasprunImporter

if TYPE_CHECKING:
    from molara.structure.crystal import Crystal


def assert_crystals_equal(crystal1: Crystal, crystal2: Crystal) -> None:
    """Check whether two crystal objects have the same contents.

    :param crystal1: first crystal of the comparison
    :param crystal2: second crystal of the comparison
    """
    assert_array_equal(
        crystal1.basis_vectors,
        crystal2.basis_vectors,
    )
    assert_array_equal(
        crystal1.atomic_nums_supercell,
        crystal2.atomic_nums_supercell,
    )
    assert_array_equal(
        crystal1.atomic_nums_unitcell,
        crystal2.atomic_nums_unitcell,
    )
    assert_array_equal(
        crystal1.fractional_coords_supercell,
        crystal2.fractional_coords_supercell,
    )
    assert_array_equal(
        crystal1.cartesian_coordinates_supercell,
        crystal2.cartesian_coordinates_supercell,
    )
    assert_array_equal(
        crystal1.coords_unitcell,
        crystal2.coords_unitcell,
    )


@pytest.mark.skipif(not find_spec("pymatgen"), reason="pymatgen not installed")
class TestPymatgenImporter(TestCase):
    """Test the PymatgenImporter class."""

    def setUp(self) -> None:
        """Set up the PymatgenImporter object."""
        self.importer = PymatgenImporter("examples/POSCAR/BN_POSCAR")
        self.supercell_dims = [4, 5, 2]

        # test case that pymatgen is not installed
        with mock.patch("builtins.__import__", side_effect=ImportError):
            msg = "pymatgen is not installed and internal importer not successful, cannot read files"
            with pytest.warns(ImportError, match=msg):
                self.importer.load(use_pymatgen=True)

        crystals = self.importer.load(use_pymatgen=True)
        assert isinstance(crystals, Crystals)
        self.crystal = crystals.get_current_mol()

    def test_load(self) -> None:
        """Test the load method of the PymatgenImporter class."""
        crystal = self.crystal
        assert_array_equal(crystal.atomic_nums_unitcell, [5, 7])
        assert_array_equal(
            crystal.coords_unitcell,
            [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]],
        )
        supercell_dims = self.supercell_dims
        self.crystal.make_supercell(supercell_dims)
        assert_array_equal(
            supercell_dims,
            self.crystal_from_POSCAR_pymatgen.supercell_dims,
        )
        assert len(self.crystal_from_POSCAR_pymatgen.atoms) == (
            (supercell_dims[0] + 1) * (supercell_dims[1] + 1) * (supercell_dims[2] + 1)
            + supercell_dims[0] * supercell_dims[1] * supercell_dims[2]
        )
        # TestCrystal.assert_crystals_equal(self.crystal_from_POSCAR_pymatgen, self.crystal)
        # TestCrystal.assert_crystals_equal(self.crystal_from_POSCAR_parser, self.crystal)


class TestPoscarImporter(TestCase):
    """Test the PoscarImporter class."""

    def setUp(self) -> None:
        """Set up the PoscarImporter object."""
        self.supercell_dims = [4, 5, 2]
        self.importer = PoscarImporter("examples/POSCAR/BN_POSCAR")
        self.crystal = self.importer.load(use_pymatgen=False).get_current_mol()
        self.crystal.make_supercell(self.supercell_dims)

    def test_load(self) -> None:
        """Test the load method of the PoscarImporter class."""
        supercell_dims = self.supercell_dims
        assert_array_equal(
            supercell_dims,
            self.crystal.supercell_dims,
        )
        assert len(self.crystal.atoms) == (
            (supercell_dims[0] + 1) * (supercell_dims[1] + 1) * (supercell_dims[2] + 1)
            + supercell_dims[0] * supercell_dims[1] * supercell_dims[2]
        )

    def test_from_poscar_cartesian(self) -> None:
        """Test the creation of a crystal from a POSCAR file with cartesian coords."""
        importer = PoscarImporter("examples/POSCAR/BN_cartesian_POSCAR")
        crystals = importer.load(use_pymatgen=False)
        crystal = crystals.get_current_mol()
        crystal.make_supercell(self.supercell_dims)

        assert_almost_equal(
            crystal.fractional_coords_supercell,
            self.crystal.fractional_coords_supercell,
            decimal=5,
        )

    def test_from_poscar_faulty(self) -> None:
        """Test the handling of faulty POSCAR files."""
        # file incomplete: length of lines < 8
        importer = PoscarImporter("tests/input_files/poscar/faulty_SrTiO3_POSCAR")
        with pytest.raises(FileFormatError, match=r"Error: faulty formatting of the POSCAR file."):
            _ = importer.load(use_pymatgen=False)
        # number formatting: scale factor is not a float
        importer = PoscarImporter("tests/input_files/poscar/faulty_BN_POSCAR")
        with pytest.raises(FileFormatError, match=r"Error: faulty formatting of the POSCAR file."):
            _ = importer.load(use_pymatgen=False)
        # number formatting: basis vector component is not a float
        importer = PoscarImporter("tests/input_files/poscar/faulty_Ba2YCu3O7_POSCAR")
        with pytest.raises(FileFormatError, match=r"Error: faulty formatting of the POSCAR file."):
            _ = importer.load(use_pymatgen=False)
        # number formatting: number of (Mg) atoms is not an integer
        importer = PoscarImporter("tests/input_files/poscar/faulty_Mg3Sb2_POSCAR")
        with pytest.raises(FileFormatError, match=r"Error: faulty formatting of the POSCAR file."):
            _ = importer.load(use_pymatgen=False)
        # number formatting: position component is not a float
        importer = PoscarImporter("tests/input_files/poscar/faulty_O2_POSCAR")
        with pytest.raises(FileFormatError, match=r"Error: faulty formatting of the POSCAR file."):
            _ = importer.load(use_pymatgen=False)
        # file incomplete: number of (O) atoms is missing
        importer = PoscarImporter("tests/input_files/poscar/faulty_BN_cartesian_POSCAR")
        with pytest.raises(FileFormatError, match=r"Error: faulty formatting of the POSCAR file."):
            _ = importer.load(use_pymatgen=False)


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
