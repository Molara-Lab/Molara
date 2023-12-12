"""Test the Crystal class."""

from __future__ import annotations

from unittest import TestCase

import numpy as np
from molara.Molecule.crystal import Crystal
from numpy.testing import assert_array_equal


class TestCrystal(TestCase):
    """Test the Crystal class."""

    def setUp(self) -> None:
        """Set up a crystal."""
        atomic_numbers = [5, 7]
        coordinates = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
        basis_vectors = [[0.0, 1.785, 1.785], [1.785, 0.0, 1.785], [1.785, 1.785, 0.0]]
        self.crystal = Crystal(atomic_numbers, coordinates, basis_vectors)
        supercell_dimensions = self.crystal.supercell_dimensions
        assert len(self.crystal.atoms) == (
            (supercell_dimensions[0]+1)*(supercell_dimensions[1]+1)*(supercell_dimensions[2]+1)
            + supercell_dimensions[0]*supercell_dimensions[1]*supercell_dimensions[2]
        )
        assert_array_equal(self.crystal.basis_vectors, basis_vectors)
        assert_array_equal(self.crystal.atomic_nums_unitcell, atomic_numbers)
        assert_array_equal(self.crystal.coords_unitcell, coordinates)

    def test_from_poscar(self) -> None:
        """Test the creation of a crystal from a POSCAR file."""
        self.crystal_from_POSCAR = Crystal.from_poscar("examples/POSCAR/boron_nitride")

        supercell_dimensions = self.crystal.supercell_dimensions
        assert len(self.crystal.atoms) == (
            (supercell_dimensions[0]+1)*(supercell_dimensions[1]+1)*(supercell_dimensions[2]+1)
            + supercell_dimensions[0]*supercell_dimensions[1]*supercell_dimensions[2]
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
        # assert self.crystal_from_POSCAR == self.crystal

    def test_make_supercell(self) -> None:
        """Test the supercell generation."""
        supercell_dimensions = [3, 3, 3]
        self.crystal.make_supercell(supercell_dimensions)
        assert_array_equal(
            self.crystal.supercell_dimensions,
            supercell_dimensions
        )
        assert len(self.crystal.atoms) == (
            (supercell_dimensions[0]+1)*(supercell_dimensions[1]+1)*(supercell_dimensions[2]+1)
            + supercell_dimensions[0]*supercell_dimensions[1]*supercell_dimensions[2]
        )