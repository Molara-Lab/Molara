"""Test the Crystal class."""

from __future__ import annotations

from importlib.util import find_spec
from unittest import TestCase

import numpy as np
import pytest
from molara.Structure.atom import elements
from molara.Structure.crystal import Crystal
from molara.Structure.io.exceptions import FileFormatError
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
        crystal = self.crystal
        supercell_dims = crystal.supercell_dims
        assert len(self.crystal.atoms) == (
            (supercell_dims[0] + 1) * (supercell_dims[1] + 1) * (supercell_dims[2] + 1)
            + supercell_dims[0] * supercell_dims[1] * supercell_dims[2]
        )
        assert len(crystal.atoms) == crystal.calc_number_of_supercell_atoms(self.supercell_dims)

        assert_array_equal(crystal.basis_vectors, self.basis_vectors)
        assert_array_equal(crystal.atomic_nums_unitcell, self.atomic_numbers)
        assert_array_equal(crystal.coords_unitcell, self.coordinates)

    def test_calc_number_of_supercell_atoms(self) -> None:
        """Test the calculation of the number of supercell atoms."""
        crystal = self.crystal
        assert crystal.calc_number_of_supercell_atoms([1, 1, 1]) == 9  # noqa: PLR2004
        assert crystal.calc_number_of_supercell_atoms([3, 4, 5]) == 180  # noqa: PLR2004

        crystal_test = Crystal(
            [2] * 6,
            [
                [0.0, 0.0, 0.25],
                [0.0, 0.25, 0.0],
                [0.0, 0.1, 0.0],
                [0.25, 0.0, 0.0],
                [0.1, 0.0, 0.0],
                [0.3, 0.0, 0.0],
            ],
            self.basis_vectors,
            [1, 1, 1],
        )
        num_ = crystal_test.calc_number_of_supercell_atoms([1, 1, 1])
        assert num_ == ((1 + 1) * (1 + 1) * 1 + 2 * (1 + 1) * 1 * (1 + 1) + 3 * 1 * (1 + 1) * (1 + 1))
        num_ = crystal_test.calc_number_of_supercell_atoms([10, 100, 1000])
        assert num_ == ((10 + 1) * (100 + 1) * 1000 + 2 * (10 + 1) * 100 * (1000 + 1) + 3 * 10 * (100 + 1) * (1000 + 1))

    def test_from_poscar_pymatgen(self) -> None:
        """Test the creation of a crystal from a POSCAR file."""
        supercell_dims = self.supercell_dims

        importer = PoscarImporter("examples/POSCAR/BN_POSCAR")
        if find_spec("pymatgen"):
            self.crystals_from_POSCAR_pymatgen = importer.load(use_pymatgen=True)
        else:
            with pytest.warns(UserWarning, match="pymatgen is not installed, using internal parser"):
                self.crystals_from_POSCAR_pymatgen = importer.load(use_pymatgen=True)

        self.crystals_from_POSCAR_parser = importer.load(use_pymatgen=False)

        self.crystal_from_POSCAR_pymatgen = self.crystals_from_POSCAR_pymatgen.get_current_mol()
        self.crystal_from_POSCAR_parser = self.crystals_from_POSCAR_parser.get_current_mol()
        self.crystal_from_POSCAR_pymatgen.make_supercell(self.supercell_dims)
        self.crystal_from_POSCAR_parser.make_supercell(self.supercell_dims)

        assert_array_equal(
            supercell_dims,
            self.crystal_from_POSCAR_pymatgen.supercell_dims,
        )
        assert len(self.crystal_from_POSCAR_pymatgen.atoms) == (
            (supercell_dims[0] + 1) * (supercell_dims[1] + 1) * (supercell_dims[2] + 1)
            + supercell_dims[0] * supercell_dims[1] * supercell_dims[2]
        )

        assert_array_equal(
            supercell_dims,
            self.crystal_from_POSCAR_parser.supercell_dims,
        )
        assert len(self.crystal_from_POSCAR_parser.atoms) == (
            (supercell_dims[0] + 1) * (supercell_dims[1] + 1) * (supercell_dims[2] + 1)
            + supercell_dims[0] * supercell_dims[1] * supercell_dims[2]
        )

        TestCrystal.assert_crystals_equal(self.crystal_from_POSCAR_pymatgen, self.crystal)
        TestCrystal.assert_crystals_equal(self.crystal_from_POSCAR_parser, self.crystal)

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

    @pytest.mark.skipif(not find_spec("ase"), reason="ASE is not installed.")
    def test_from_ase(self) -> None:
        """Test the creation of a crystal from an ASE atoms object."""
        from ase import Atoms

        atomic_numbers = [5, 7]
        coordinates = [[0.0, 0.0, 0.0], [0.25, 0.25, 0.25]]
        basis_vectors = [[0.0, 1.785, 1.785], [1.785, 0.0, 1.785], [1.785, 1.785, 0.0]]

        atoms = Atoms(
            scaled_positions=coordinates,
            numbers=atomic_numbers,
            cell=basis_vectors,
            pbc=True,
        )

        crystal = Crystal.from_ase(atoms)

        assert_array_equal(crystal.basis_vectors, basis_vectors)
        assert_array_equal(crystal.atomic_nums_unitcell, atomic_numbers)
        assert_array_equal(crystal.coords_unitcell, coordinates)

    @staticmethod
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

    def test_from_poscar_cartesian(self) -> None:
        """Test the creation of a crystal from a POSCAR file with cartesian coords."""
        importer = PoscarImporter("examples/POSCAR/BN_cartesian_POSCAR")
        self.crystals_from_POSCAR_c = importer.load(use_pymatgen=False)
        self.crystal_from_POSCAR_c = self.crystals_from_POSCAR_c.get_current_mol()
        self.crystal_from_POSCAR_c.make_supercell(self.supercell_dims)

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
            (elements["B"]["Atomic mass"] + elements["N"]["Atomic mass"]),
        )
        assert_almost_equal(self.crystal.volume_unitcell, 11.3748225, decimal=5)
        assert_almost_equal(self.crystal.density_unitcell, 3.6229802861472007, decimal=5)
        with pytest.raises(ValueError, match=r"Faulty shape of basis_vectors array. Shape must be \(3,3\)."):
            _ = self.crystal.calc_volume_unitcell([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])

    def test_toggle_bonds(self) -> None:
        """Test the toggle bonds routine."""
        # after instantiation, draw_bonds should be False by default,
        # and bonds should not have been calculated yet.
        assert not self.crystal.draw_bonds
        assert not self.crystal.bonds_calculated
        assert not self.crystal.has_bonds
        # after bonds toggle, bonds should have been calculated,
        # and draw_bonds should be set to True.
        self.crystal.toggle_bonds()
        assert self.crystal.draw_bonds
        assert self.crystal.bonds_calculated
        assert self.crystal.has_bonds
        # after a further bonds toggle, calculated bonds should still be there,
        # but draw_bonds should once again be set to False.
        self.crystal.toggle_bonds()
        assert not self.crystal.draw_bonds
        assert self.crystal.bonds_calculated
        assert self.crystal.has_bonds

    def test_copy(self) -> None:
        """Test the copy method."""
        _copy = self.crystal.copy()
        assert_array_equal(_copy.atomic_nums_unitcell, self.crystal.atomic_nums_unitcell)
        assert_array_equal(_copy.coords_unitcell, self.crystal.coords_unitcell)
        assert_array_equal(_copy.basis_vectors, self.crystal.basis_vectors)
        assert_array_equal(_copy.supercell_dims, self.crystal.supercell_dims)
        assert_array_equal(_copy.atomic_nums_supercell, self.crystal.atomic_nums_supercell)
        assert_array_equal(_copy.fractional_coords_supercell, self.crystal.fractional_coords_supercell)
        assert_array_equal(_copy.cartesian_coordinates_supercell, self.crystal.cartesian_coordinates_supercell)
        assert _copy.molar_mass == self.crystal.molar_mass
        assert _copy.volume_unitcell == self.crystal.volume_unitcell
        assert _copy.density_unitcell == self.crystal.density_unitcell

    def test_mul(self) -> None:
        """Test the multiplication operator."""
        _copy = self.crystal * self.supercell_dims
        assert_array_equal(_copy.atomic_nums_unitcell, self.crystal.atomic_nums_unitcell)
        assert_array_equal(_copy.coords_unitcell, self.crystal.coords_unitcell)
        assert_array_equal(_copy.basis_vectors, self.crystal.basis_vectors)
        assert_array_equal(_copy.supercell_dims, [2, 7, 4])
        assert_array_equal(_copy.atomic_nums_supercell, self.crystal.atomic_nums_supercell)
        assert_array_equal(_copy.fractional_coords_supercell, self.crystal.fractional_coords_supercell)
        assert_array_equal(_copy.cartesian_coordinates_supercell, self.crystal.cartesian_coordinates_supercell)
        # assert _copy.molar_mass == self.crystal.molar_mass * 2 * 7 * 4
        assert _copy.volume_unitcell == self.crystal.volume_unitcell
        assert _copy.density_unitcell == self.crystal.density_unitcell

    def test_no_edge_atoms(self) -> None:
        """Test the no_edge_atoms method."""
        importer = PoscarImporter("examples/POSCAR/O2_POSCAR")
        crystal = importer.load().get_current_mol()
        assert len(crystal.atoms) == 1 + 1

    def test_unitcell_boundaries_positions(self) -> None:
        """Test the unitcell_boundaries_positions method."""
        self.crystal.center_coordinates()  # necessary so that crystal.center is set
        positions = self.crystal.unitcell_boundaries_positions
        basis_vectors_matrix = np.array(self.basis_vectors)
        zero_vec = np.array([0, 0, 0])
        positions_comparison = (
            np.array(
                [
                    [zero_vec, basis_vectors_matrix[0]],
                    [zero_vec, basis_vectors_matrix[1]],
                    [zero_vec, basis_vectors_matrix[2]],
                    [basis_vectors_matrix[0], basis_vectors_matrix[0] + basis_vectors_matrix[1]],
                    [basis_vectors_matrix[0], basis_vectors_matrix[0] + basis_vectors_matrix[2]],
                    [basis_vectors_matrix[1], basis_vectors_matrix[1] + basis_vectors_matrix[0]],
                    [basis_vectors_matrix[1], basis_vectors_matrix[1] + basis_vectors_matrix[2]],
                    [basis_vectors_matrix[2], basis_vectors_matrix[2] + basis_vectors_matrix[1]],
                    [basis_vectors_matrix[2], basis_vectors_matrix[2] + basis_vectors_matrix[0]],
                    [
                        basis_vectors_matrix[0] + basis_vectors_matrix[1],
                        basis_vectors_matrix[0] + basis_vectors_matrix[1] + basis_vectors_matrix[2],
                    ],
                    [
                        basis_vectors_matrix[0] + basis_vectors_matrix[2],
                        basis_vectors_matrix[0] + basis_vectors_matrix[1] + basis_vectors_matrix[2],
                    ],
                    [
                        basis_vectors_matrix[1] + basis_vectors_matrix[2],
                        basis_vectors_matrix[0] + basis_vectors_matrix[1] + basis_vectors_matrix[2],
                    ],
                ],
                dtype=np.float32,
            )
            - self.crystal.center
        )
        assert_array_equal(positions, positions_comparison)
