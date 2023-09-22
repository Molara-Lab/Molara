from unittest import TestCase

import numpy as np
from molara.Molecule.Crystal import Crystal
from numpy.testing import assert_array_equal


class TestCrystal(TestCase):
    def setUp(self):
        atomic_numbers = [5, 7]
        coordinates = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
        basis_vectors = [[0.0, 1.785, 1.785], [1.785, 0.0, 1.785], [1.785, 1.785, 0.0]]
        self.crystal = Crystal(atomic_numbers, coordinates, basis_vectors)

        assert len(self.crystal.atoms) == 2**3 + 1**3
        assert_array_equal(self.crystal.basis_vectors, basis_vectors)
        assert_array_equal(self.crystal.atomic_numbers_unitcell, atomic_numbers)
        assert_array_equal(self.crystal.coordinates_unitcell, coordinates)

    def test_from_POSCAR(self):
        self.crystal_from_POSCAR = Crystal.from_POSCAR("examples/POSCAR/boron_nitride")

        assert len(self.crystal_from_POSCAR.atoms) == 2**3 + 1
        assert_array_equal(self.crystal_from_POSCAR.basis_vectors, self.crystal.basis_vectors)
        assert_array_equal(self.crystal_from_POSCAR.atomic_numbers_supercell, self.crystal.atomic_numbers_supercell)
        assert_array_equal(self.crystal_from_POSCAR.atomic_numbers_unitcell, self.crystal.atomic_numbers_unitcell)
        assert_array_equal(
            self.crystal_from_POSCAR.fractional_coordinates_supercell, self.crystal.fractional_coordinates_supercell
        )
        assert_array_equal(
            self.crystal_from_POSCAR.cartesian_coordinates_supercell, self.crystal.cartesian_coordinates_supercell
        )
        assert_array_equal(self.crystal_from_POSCAR.coordinates_unitcell, self.crystal.coordinates_unitcell)
        # assert self.crystal_from_POSCAR == self.crystal

    def test_make_supercell(self):
        self.crystal.make_supercell([3, 3, 3])
        assert len(self.crystal.atoms) == 4**3 + 3**3
