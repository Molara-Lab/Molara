"""Test the Crystal class."""

from __future__ import annotations

from unittest import TestCase

from molara.Structure.atom import elements
from molara.Structure.crystal import Crystal
from molara.Structure.io.importer import PoscarImporter
from numpy.testing import assert_almost_equal, assert_array_equal

__copyright__ = "Copyright 2024, Molara"


class TestCrystal(TestCase):
    """Test the Crystal class."""

    def setUp(self) -> None:
        """Set up a crystal."""
        self.atomic_numbers = [5, 7]
        self.coordinates = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
        self.basis_vectors = [[0.0, 1.785, 1.785], [1.785, 0.0, 1.785], [1.785, 1.785, 0.0]]
        self.supercell_dims = [2, 7, 4]
        self.crystal = Crystal(self.atomic_numbers, self.coordinates, self.basis_vectors, self.supercell_dims)

    def test_setup(self) -> None:
        """Test the result of the setUp routine."""
        supercell_dims = self.crystal.supercell_dims
        assert len(self.crystal.atoms) == (
            (supercell_dims[0] + 1) * (supercell_dims[1] + 1) * (supercell_dims[2] + 1)
            + supercell_dims[0] * supercell_dims[1] * supercell_dims[2]
        )
        assert_array_equal(self.crystal.basis_vectors, self.basis_vectors)
        assert_array_equal(self.crystal.atomic_nums_unitcell, self.atomic_numbers)
        assert_array_equal(self.crystal.coords_unitcell, self.coordinates)

    def test_from_poscar(self) -> None:
        """Test the creation of a crystal from a POSCAR file."""
        supercell_dims = self.supercell_dims
        importer = PoscarImporter("examples/POSCAR/boron_nitride", supercell_dims)
        self.crystals_from_POSCAR = importer.load()
        self.crystal_from_POSCAR = self.crystals_from_POSCAR.get_current_mol()

        assert_array_equal(
            supercell_dims,
            self.crystal_from_POSCAR.supercell_dims,
        )
        assert len(self.crystal_from_POSCAR.atoms) == (
            (supercell_dims[0] + 1) * (supercell_dims[1] + 1) * (supercell_dims[2] + 1)
            + supercell_dims[0] * supercell_dims[1] * supercell_dims[2]
        )
        assert_array_equal(
            self.crystal_from_POSCAR.basis_vectors,
            self.crystal.basis_vectors,
        )
        assert_array_equal(
            self.crystal_from_POSCAR.atomic_nums_supercell,
            self.crystal.atomic_nums_supercell,
        )
        assert_array_equal(
            self.crystal_from_POSCAR.atomic_nums_unitcell,
            self.crystal.atomic_nums_unitcell,
        )
        assert_array_equal(
            self.crystal_from_POSCAR.fractional_coords_supercell,
            self.crystal.fractional_coords_supercell,
        )
        assert_array_equal(
            self.crystal_from_POSCAR.cartesian_coordinates_supercell,
            self.crystal.cartesian_coordinates_supercell,
        )
        assert_array_equal(
            self.crystal_from_POSCAR.coords_unitcell,
            self.crystal.coords_unitcell,
        )

    def test_from_poscar_cartesian(self) -> None:
        """Test the creation of a crystal from a POSCAR file with cartesian coords."""
        supercell_dims = self.supercell_dims
        importer = PoscarImporter("examples/POSCAR/boron_nitride_cartesian", supercell_dims)
        self.crystals_from_POSCAR_c = importer.load()
        self.crystal_from_POSCAR_c = self.crystals_from_POSCAR_c.get_current_mol()

        assert_almost_equal(
            self.crystal_from_POSCAR_c.fractional_coords_supercell,
            self.crystal.fractional_coords_supercell,
            decimal=5,
        )

    def test_make_supercell(self) -> None:
        """Test the supercell generation."""
        supercell_dims = [3, 3, 3]
        self.crystal.make_supercell(supercell_dims)
        assert_array_equal(
            self.crystal.supercell_dims,
            supercell_dims,
        )
        assert len(self.crystal.atoms) == (
            (supercell_dims[0] + 1) * (supercell_dims[1] + 1) * (supercell_dims[2] + 1)
            + supercell_dims[0] * supercell_dims[1] * supercell_dims[2]
        )

    def test_properties(self) -> None:
        """Test the properties of the crystal."""
        assert self.crystal.molar_mass == float(
            (elements[5]["atomic_weight"] + elements[7]["atomic_weight"]),
        )
        assert_almost_equal(self.crystal.volume_unitcell, 11.3748225, decimal=5)
        assert_almost_equal(self.crystal.density_unitcell, 3.6229802861472007, decimal=5)

    def test_copy(self) -> None:
        """Test the copy method."""
        copy = self.crystal.copy()
        assert_array_equal(copy.atomic_nums_unitcell, self.crystal.atomic_nums_unitcell)
        assert_array_equal(copy.coords_unitcell, self.crystal.coords_unitcell)
        assert_array_equal(copy.basis_vectors, self.crystal.basis_vectors)
        assert_array_equal(copy.supercell_dims, self.crystal.supercell_dims)
        assert_array_equal(copy.atomic_nums_supercell, self.crystal.atomic_nums_supercell)
        assert_array_equal(copy.fractional_coords_supercell, self.crystal.fractional_coords_supercell)
        assert_array_equal(copy.cartesian_coordinates_supercell, self.crystal.cartesian_coordinates_supercell)
        assert copy.molar_mass == self.crystal.molar_mass
        assert copy.volume_unitcell == self.crystal.volume_unitcell
        assert copy.density_unitcell == self.crystal.density_unitcell