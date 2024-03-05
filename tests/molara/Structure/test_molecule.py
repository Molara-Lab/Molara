"""Test the Molecule class."""

from __future__ import annotations

from unittest import TestCase

import numpy as np
from molara.Structure.atom import Atom
from molara.Structure.molecule import Molecule
from numpy.testing import assert_array_equal

__copyright__ = "Copyright 2024, Molara"


class TestMolecule(TestCase):
    """Test the Molecule class."""

    def setUp(self) -> None:
        """Set up some Molecule objects."""
        self.num_atoms_ccl4 = 5
        xyz_data_ccl4 = np.array(
            [
                [6, 0.000000, 0.000000, 0.000000],
                [17, 0.000000, 0.000000, 1.750000],
                [17, 1.649916, 0.000000, -0.583333],
                [17, -0.824958, -1.428869, -0.583333],
                [17, -0.824958, 1.428869, -0.583333],
            ],
        )
        self.atomic_nums_ccl4 = np.array(xyz_data_ccl4[:, 0], dtype=int)
        self.coords_ccl4 = xyz_data_ccl4[:, 1:]
        self.ccl4 = Molecule(self.atomic_nums_ccl4, self.coords_ccl4)

        self.num_atoms_water = 3
        xyz_data_water = np.array(
            [
                [1, 0.7493682, 0.4424329, 0.0000000],
                [1, -0.7493682, 0.4424329, 0.0000000],
                [8, 0.0000000, -0.1653507, 0.0000000],
            ],
        )
        self.atomic_nums_water = np.array(xyz_data_water[:, 0], dtype=int)
        self.coords_water = xyz_data_water[:, 1:]
        self.water = Molecule(self.atomic_nums_water, self.coords_water)

    def test_setup(self) -> None:
        """Test the setup of the Molecule objects."""
        # test ccl4
        ccl4, num_atoms_ccl4 = self.ccl4, self.num_atoms_ccl4
        atomic_nums_ccl4, coords_ccl4 = self.atomic_nums_ccl4, self.coords_ccl4
        assert ccl4.draw_bonds
        assert len(ccl4.atoms) == num_atoms_ccl4
        for atom_i, atomic_num_i, coords_i in zip(ccl4.atoms, atomic_nums_ccl4, coords_ccl4):
            assert isinstance(atom_i, Atom)
            assert atom_i.atomic_number == atomic_num_i
            assert_array_equal(atom_i.position, coords_i)
        assert_array_equal(ccl4.atomic_numbers, atomic_nums_ccl4)
        assert_array_equal(ccl4.unique_atomic_numbers, [6, 17])
        bond_vectors_ccl4 = np.array([self.coords_ccl4[i] - self.coords_ccl4[0] for i in range(1, 5)])
        bond_vectors_ccl4_object = np.array(
            [atom_i.position - self.ccl4.atoms[0].position for atom_i in self.ccl4.atoms[1:]],
        )
        assert_array_equal(bond_vectors_ccl4_object, bond_vectors_ccl4)

        # test water
        water, num_atoms_water = self.water, self.num_atoms_water
        atomic_nums_water, coords_water = self.atomic_nums_water, self.coords_water
        assert water.draw_bonds
        assert len(water.atoms) == num_atoms_water
        for atom_i, atomic_num_i, coords_i in zip(water.atoms, atomic_nums_water, coords_water):
            assert isinstance(atom_i, Atom)
            assert atom_i.atomic_number == atomic_num_i
            assert_array_equal(atom_i.position, coords_i)
        assert_array_equal(water.atomic_numbers, atomic_nums_water)
        assert_array_equal(water.unique_atomic_numbers, [1, 8])
        bond_vectors_water = np.array([self.coords_water[i] - self.coords_water[0] for i in range(1, 3)])
        bond_vectors_water_object = np.array(
            [atom_i.position - self.water.atoms[0].position for atom_i in self.water.atoms[1:]],
        )
        assert_array_equal(bond_vectors_water_object, bond_vectors_water)

    def test_toggle_bonds(self) -> None:
        """Test the toggle bonds routine."""
        # after instantiation, draw_bonds should be True by default,
        # and bonds should have been calculated.
        assert self.ccl4.draw_bonds
        assert self.ccl4.bonds_calculated
        assert self.ccl4.has_bonds
        # after bonds toggle, draw_bonds should be set to False.
        self.ccl4.toggle_bonds()
        assert not self.ccl4.draw_bonds
        assert self.ccl4.bonds_calculated
        assert self.ccl4.has_bonds
        # after a further bonds toggle, draw_bonds be True again.
        self.ccl4.toggle_bonds()
        assert self.ccl4.draw_bonds
        assert self.ccl4.bonds_calculated
        assert self.ccl4.has_bonds

    def test_copy(self) -> None:
        """Test the copy routine."""
        copy = self.ccl4.copy()
        assert_array_equal(copy.atomic_numbers, self.ccl4.atomic_numbers)
        assert copy.molar_mass == self.ccl4.molar_mass
        for atom_copy, atom_ccl4 in zip(copy.atoms, self.ccl4.atoms):
            assert_array_equal(atom_copy.position, atom_ccl4.position)
        assert copy.draw_bonds == self.ccl4.draw_bonds

        self.ccl4.toggle_bonds()
        copy = self.ccl4.copy()
        assert copy.draw_bonds == self.ccl4.draw_bonds

    def test_compute_collision(self) -> None:
        """Test the compute_collision routine."""
        # def compute_collision(self: Structure | Crystal | Molecule, coordinate: np.ndarray) -> int | None:
        dist_threshold = 1e-10
        just_below = 0.99 * dist_threshold
        just_above = 1.01 * dist_threshold
        collision_coords1 = self.coords_ccl4[0]
        collision_coords21 = self.coords_ccl4[1] + np.array([just_below, 0.0, 0.0])
        collision_coords22 = self.coords_ccl4[1] + np.array([0.0, just_below, 0.0])
        collision_coords23 = self.coords_ccl4[1] + np.array([0.0, 0.0, just_below])
        collision_coords31 = self.coords_ccl4[2] + np.array([just_above, 0.0, 0.0])
        collision_coords32 = self.coords_ccl4[2] + np.array([0.0, just_above, 0.0])
        collision_coords33 = self.coords_ccl4[2] + np.array([0.0, 0.0, just_above])
        just_below = 0.99 * dist_threshold / np.sqrt(3)
        just_above = 1.01 * dist_threshold / np.sqrt(3)
        collision_coords4 = self.coords_ccl4[3] + np.array([just_below, -just_below, -just_below])
        collision_coords5 = self.coords_ccl4[4] + np.array([-just_above, just_above, -just_above])

        id1, id2, id4 = 0, 1, 3
        assert self.ccl4.compute_collision(collision_coords1) == id1
        assert self.ccl4.compute_collision(collision_coords21) == id2
        assert self.ccl4.compute_collision(collision_coords22) == id2
        assert self.ccl4.compute_collision(collision_coords23) == id2
        assert self.ccl4.compute_collision(collision_coords31) is None
        assert self.ccl4.compute_collision(collision_coords32) is None
        assert self.ccl4.compute_collision(collision_coords33) is None
        assert self.ccl4.compute_collision(collision_coords4) == id4
        assert self.ccl4.compute_collision(collision_coords5) is None

    def test_center_coordinates(self) -> None:
        """Test the center_coordinates routine."""
        # test ccl4
        self.ccl4.center_coordinates()
        assert_array_equal(np.mean(self.ccl4.coords, axis=0), np.zeros(3))
        # test water
        self.water.center_coordinates()
        assert_array_equal(np.mean(self.water.coords, axis=0), np.zeros(3))
