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

        assert len(self.crystal.atoms) == 2**3 + 1**3
        assert_array_equal(self.crystal.basis_vectors, basis_vectors)
        assert_array_equal(self.crystal.atomic_nums_unitcell, atomic_numbers)
        assert_array_equal(self.crystal.coords_unitcell, coordinates)

    def test_from_poscar(self) -> None:
        """Test the creation of a crystal from a POSCAR file."""
        self.crystal_from_POSCAR = Crystal.from_poscar("examples/POSCAR/boron_nitride")

        assert len(self.crystal_from_POSCAR.atoms) == 2**3 + 1
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
        self.crystal.make_supercell([3, 3, 3])
        assert len(self.crystal.atoms) == 4**3 + 3**3
