"""Test the Molecules class."""

from __future__ import annotations

from unittest import TestCase

import numpy as np
from molara.Molecule.atom import Atom
from molara.Molecule.molecule import Molecule
from numpy.testing import assert_array_equal

__copyright__ = "Copyright 2024, Molara"


class TestMolecules(TestCase):
    """Test the Molecules class."""

    def test_setup(self) -> None:
        """Set up a molecules object."""
        # Pentane
        num_atoms_pentane = 17
        xyz_data_pentane = np.array(
            [
                [6, -0.06119, -0.14438, -0.09006],
                [1, -0.06046, -0.76500, 0.81047],
                [1, 0.04110, -0.82551, -0.94388],
                [6, 1.13633, 0.80196, -0.06785],
                [1, 1.04730, 1.50136, 0.77446],
                [1, 1.16482, 1.40068, -0.98213],
                [6, 2.43464, 0.02076, 0.06562],
                [1, 2.42913, -0.60381, 0.96237],
                [1, 3.28623, 0.69990, 0.13111],
                [1, 2.58851, -0.63256, -0.80327],
                [6, -1.39343, 0.59934, -0.18301],
                [1, -1.35021, 1.39778, -0.92849],
                [1, -1.60573, 1.07576, 0.78352],
                [6, -2.52277, -0.35635, -0.53888],
                [1, -3.48791, 0.04616, -0.21351],
                [1, -2.38991, -1.33607, -0.06587],
                [1, -2.57051, -0.50852, -1.61872],
            ],
        )
        atomic_numbers_pentane = np.array(xyz_data_pentane[:, 0], dtype=int)
        coordinates_pentane = xyz_data_pentane[:, 1:]
        self.pentane = Molecule(atomic_numbers_pentane, coordinates_pentane)

        # Glucose
        num_atoms_glucose = 12
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
        )
        atomic_numbers_glucose = np.array(xyz_data_glucose[:, 0], dtype=int)
        coordinates_glucose = xyz_data_glucose[:, 1:]
        self.glucose = Molecule(atomic_numbers_glucose, coordinates_glucose)

        assert self.pentane.draw_bonds
        assert len(self.pentane.atoms) == num_atoms_pentane
        for atom_i in self.pentane.atoms:
            assert isinstance(atom_i, Atom)
        assert_array_equal(self.pentane.atomic_numbers, atomic_numbers_pentane)
        assert_array_equal(self.pentane.unique_atomic_numbers, [6, 1])

        assert self.glucose.draw_bonds
        assert len(self.glucose.atoms) == num_atoms_glucose
        for atom_i in self.glucose.atoms:
            assert isinstance(atom_i, Atom)
        assert_array_equal(self.glucose.atomic_numbers, atomic_numbers_glucose)
        assert_array_equal(self.glucose.unique_atomic_numbers, [6, 8])

    # def test_copy(self) -> None:
    #     """Test the copy method."""
