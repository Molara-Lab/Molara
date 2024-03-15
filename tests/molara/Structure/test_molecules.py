"""Test the Molecules class."""

from __future__ import annotations

from unittest import TestCase

import numpy as np
from molara.Structure.atom import Atom
from molara.Structure.molecule import Molecule
from molara.Structure.molecules import Molecules
from numpy.testing import assert_array_equal

__copyright__ = "Copyright 2024, Molara"


class TestMolecules(TestCase):
    """Test the Molecules class."""

    def setUp(self) -> None:
        """Set up a molecules object."""
        # Pentane
        self.num_atoms_pentane = 17
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
        self.atomic_nums_pentane = np.array(xyz_data_pentane[:, 0], dtype=int)
        self.coords_pentane = xyz_data_pentane[:, 1:]
        self.pentane = Molecule(self.atomic_nums_pentane, self.coords_pentane)

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
        )
        self.atomic_nums_glucose = np.array(xyz_data_glucose[:, 0], dtype=int)
        self.coords_glucose = xyz_data_glucose[:, 1:]
        self.glucose = Molecule(self.atomic_nums_glucose, self.coords_glucose)

        # Molecules object
        self.molecules = Molecules()
        self.molecules.add_molecule(self.pentane)
        self.molecules.add_molecule(self.glucose)
        self.num_molecules = 2

    def test_setup(self) -> None:
        """Test the result of the setUp routine."""
        # test pentane
        pentane, num_atoms_pentane = self.pentane, self.num_atoms_pentane
        atomic_nums_pentane, coords_pentane = self.atomic_nums_pentane, self.coords_pentane
        assert pentane.draw_bonds
        assert len(pentane.atoms) == num_atoms_pentane
        for atom_i, atomic_num_i, coords_i in zip(pentane.atoms, atomic_nums_pentane, coords_pentane):
            assert isinstance(atom_i, Atom)
            assert atom_i.atomic_number == atomic_num_i
            assert_array_equal(atom_i.position, coords_i)
        assert_array_equal(pentane.atomic_numbers, atomic_nums_pentane)
        assert_array_equal(pentane.unique_atomic_numbers, [6, 1])

        # test glucose
        glucose, num_atoms_glucose = self.glucose, self.num_atoms_glucose
        atomic_nums_glucose, coords_glucose = self.atomic_nums_glucose, self.coords_glucose
        assert glucose.draw_bonds
        assert len(glucose.atoms) == num_atoms_glucose
        for atom_i, atomic_num_i, coords_i in zip(glucose.atoms, atomic_nums_glucose, coords_glucose):
            assert isinstance(atom_i, Atom)
            assert atom_i.atomic_number == atomic_num_i
            assert_array_equal(atom_i.position, coords_i)
        assert_array_equal(glucose.atomic_numbers, atomic_nums_glucose)
        assert_array_equal(glucose.unique_atomic_numbers, [6, 8])

        # test molecules object
        assert self.molecules.num_mols == self.num_molecules
        #     first molecule: pentane
        assert self.molecules.mol_index == 0
        molecules_pentane = self.molecules.get_current_mol()
        assert isinstance(molecules_pentane, Molecule)
        assert molecules_pentane.draw_bonds
        assert len(molecules_pentane.atoms) == self.num_atoms_pentane
        for atom_i, atomic_num_i, coords_i in zip(molecules_pentane.atoms, atomic_nums_pentane, coords_pentane):
            assert isinstance(atom_i, Atom)
            assert atom_i.atomic_number == atomic_num_i
            assert_array_equal(atom_i.position, coords_i)
        assert_array_equal(molecules_pentane.atomic_numbers, atomic_nums_pentane)
        assert_array_equal(molecules_pentane.unique_atomic_numbers, [6, 1])
        #     second molecule: glucose
        self.molecules.set_next_mol()
        assert self.molecules.mol_index == 1
        molecules_glucose = self.molecules.get_current_mol()
        assert isinstance(molecules_glucose, Molecule)
        assert molecules_glucose.draw_bonds
        assert len(molecules_glucose.atoms) == self.num_atoms_glucose
        for atom_i, atomic_num_i, coords_i in zip(molecules_glucose.atoms, atomic_nums_glucose, coords_glucose):
            assert isinstance(atom_i, Atom)
            assert atom_i.atomic_number == atomic_num_i
            assert_array_equal(atom_i.position, coords_i)
        assert_array_equal(molecules_glucose.atomic_numbers, atomic_nums_glucose)
        assert_array_equal(molecules_glucose.unique_atomic_numbers, [6, 8])
        #    test switching to next / previous molecule
        self.molecules.set_previous_mol()
        assert self.molecules.mol_index == 0
        self.molecules.set_next_mol()
        assert self.molecules.mol_index == 1
        self.molecules.set_next_mol()
        assert self.molecules.mol_index == 0
        self.molecules.set_previous_mol()
        assert self.molecules.mol_index == 1

    # def test_copy(self) -> None:
    #     """Test the copy method."""
