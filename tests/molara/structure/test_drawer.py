"""Test the Atom class."""

from __future__ import annotations

from unittest import TestCase

import numpy as np
from numpy.testing import assert_array_equal

from molara.rendering.cylinder import Cylinder
from molara.rendering.sphere import Sphere
from molara.structure.atom import Atom
from molara.structure.drawer import Drawer


class TestDrawer(TestCase):
    """Test the Drawer class."""

    def setUp(self) -> None:
        """Set up drawer object(s)."""
        # Glucose
        self.num_atoms_glucose = 12
        xyz_data_glucose = np.array(
            [
                [6, 35.884, 30.895, 49.120],
                [6, 36.177, 29.853, 50.124],
                [6, 37.296, 30.296, 51.074],
                [6, 38.553, 30.400, 50.259],
                [6, 38.357, 31.290, 49.044],
                [6, 39.559, 31.209, 48.082],
                [8, 34.968, 30.340, 48.234],
                [8, 34.923, 29.775, 50.910],
                [8, 37.441, 29.265, 52.113],
                [8, 39.572, 30.954, 51.086],
                [8, 37.155, 30.858, 48.364],
                [8, 39.261, 32.018, 46.920],
            ],
            dtype=np.float32,
        )
        self.atomic_nums_glucose = np.array(xyz_data_glucose[:, 0], dtype=int)
        self.coords_glucose = xyz_data_glucose[:, 1:]
        self.atoms_glucose = [
            Atom(atomic_num_i, pos_i) for atomic_num_i, pos_i in zip(self.atomic_nums_glucose, self.coords_glucose)
        ]
        # no bonds for now
        self.bonds_glucose = np.array(
            [
                [[-1]],
            ],
        )
        draw_bonds = False
        self.drawer_glucose = Drawer(
            self.atoms_glucose,
            self.bonds_glucose,
            draw_bonds,
        )

    def test_setup(self) -> None:
        """Test the Drawer setup."""
        subdivisions_sphere = 20
        subdivisions_cylinder = 20
        assert self.drawer_glucose.subdivisions_sphere == subdivisions_sphere
        assert self.drawer_glucose.subdivisions_cylinder == subdivisions_cylinder
        assert isinstance(self.drawer_glucose.sphere, Sphere)
        assert isinstance(self.drawer_glucose.cylinder, Cylinder)
        assert isinstance(self.drawer_glucose.atoms, list)
        assert isinstance(self.drawer_glucose.atom_positions, np.ndarray)
        assert isinstance(self.drawer_glucose.atom_colors, np.ndarray)
        assert isinstance(self.drawer_glucose.atom_scales, np.ndarray)
        assert self.drawer_glucose.atom_positions.shape == (self.num_atoms_glucose, 3)
        assert self.drawer_glucose.atom_colors.shape == (self.num_atoms_glucose, 3)
        assert self.drawer_glucose.atom_scales.shape == (self.num_atoms_glucose, 3)
        for atom_i_drawer, pos_i_drawer, atom_i_test, atomic_num_i_test, pos_i_test in zip(
            self.drawer_glucose.atoms,
            self.drawer_glucose.atom_positions,
            self.atoms_glucose,
            self.atomic_nums_glucose,
            self.coords_glucose,
        ):
            assert isinstance(atom_i_drawer, Atom)
            assert atom_i_drawer == atom_i_test
            assert atom_i_drawer.atomic_number == atomic_num_i_test
            assert_array_equal(pos_i_drawer, pos_i_test)
            assert_array_equal(pos_i_drawer, atom_i_drawer.position)

        assert isinstance(self.drawer_glucose.sphere_model_matrices, np.ndarray)
        assert isinstance(self.drawer_glucose.sphere_translation_matrices, np.ndarray)
        assert isinstance(self.drawer_glucose.sphere_scale_matrices, np.ndarray)
        assert self.drawer_glucose.sphere_model_matrices.shape == (self.num_atoms_glucose, 4, 4)
        assert self.drawer_glucose.sphere_translation_matrices.shape == (self.num_atoms_glucose, 4, 4)
        assert self.drawer_glucose.sphere_scale_matrices.shape == (self.num_atoms_glucose, 4, 4)

    def test_reset_atom_model_matrices(self) -> None:
        """Test resets of model matrices for the spheres."""
        self.drawer_glucose.reset_atom_model_matrices()
        assert isinstance(self.drawer_glucose.sphere_model_matrices, np.ndarray)
        assert_array_equal(self.drawer_glucose.sphere_model_matrices, np.array([], dtype=np.float32))

    def test_reset_cylinders_model_matrices(self) -> None:
        """Test resets of model matrices for the cylinders."""
        self.drawer_glucose.reset_cylinders_model_matrices()
        assert isinstance(self.drawer_glucose.cylinder_model_matrices, np.ndarray)
        assert_array_equal(self.drawer_glucose.cylinder_model_matrices, np.array([], dtype=np.float32))

    def test_reset_atom_colors(self) -> None:
        """Test resets of the colors for the spheres."""
        self.drawer_glucose.reset_atom_colors()
        assert isinstance(self.drawer_glucose.atom_colors, np.ndarray)
        assert_array_equal(self.drawer_glucose.atom_colors, np.array([], dtype=np.float32))
