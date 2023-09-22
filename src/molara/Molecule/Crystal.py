import re
from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike

from .Atom import element_symbol_to_atomic_number
from .Molecule import *


class Crystal(Molecule):
    """
    Creates a crystal supercell based on given particle positions in unit cell and lattice basis vectors.
    Particle positions are given in terms of the basis vectors:
    E.g. the position (0.5, 0.5, 0.) is always the center of a unit cell wall, regardless of the crystal system.

    :param atomic_numbers: contains the atomic numbers of the particles specified for the unit cell.
    :type atomic_numbers: numpy.array of int
    :param coordinates: Nx3 matrix of particle coordinates in the unit cell, in terms of the basis vectors.
    :type coordinates: numpy.ndarray of numpy.float64
    :param basis_vectors: 3x3 matrix of the lattice basis vectors.
    :type basis_vectors: numpy.ndarray of numpy.float64
    :param supercell_dimensions: side lengths of the supercell in terms of the cell constants
    :type supercell_dimensions: numpy.array of int
    """

    def __init__(
        self,
        atomic_numbers: Sequence[int],
        coordinates: Sequence[Sequence[float]],
        basis_vectors: Sequence[Sequence[float]],
    ):
        self.atomic_numbers_unitcell = atomic_numbers
        self.coordinates_unitcell = coordinates
        self.basis_vectors = basis_vectors
        self.make_supercell([2, 2, 2])

    def make_supercell(self, supercell_dimensions):
        steps_a = np.arange(supercell_dimensions[0] + 1)
        steps_b = np.arange(supercell_dimensions[1] + 1)
        steps_c = np.arange(supercell_dimensions[2] + 1)
        steps_a.shape = (1, 1, *steps_a.shape)
        steps_b.shape = (1, *steps_b.shape, 1)
        steps_c.shape = (1, 1, *steps_c.shape)
        translations_a = 1.0 * steps_a + 0.0 * steps_b + 0.0 * steps_c
        translations_b = 0.0 * steps_a + 1.0 * steps_b + 0.0 * steps_c
        translations_c = 0.0 * steps_a + 0.0 * steps_b + 1.0 * steps_c
        translation_vectors = np.array([translations_a.flatten(), translations_b.flatten(), translations_c.flatten()]).T

        num_unit_cells = translation_vectors.shape[0]
        self.fractional_coordinates_supercell = np.empty((0, 3), float)
        self.atomic_numbers_supercell = np.empty(0, int)
        for atomic_number_i, position_i in zip(self.atomic_numbers_unitcell, self.coordinates_unitcell):
            self.atomic_numbers_supercell = np.append(self.atomic_numbers_supercell, [atomic_number_i] * num_unit_cells)
            self.fractional_coordinates_supercell = np.append(
                self.fractional_coordinates_supercell, position_i + translation_vectors, axis=0
            )

        # remove positions outside of the supercell box
        ids_remove_a = np.where(self.fractional_coordinates_supercell[:, 0] > supercell_dimensions[0])
        ids_remove_b = np.where(self.fractional_coordinates_supercell[:, 1] > supercell_dimensions[1])
        ids_remove_c = np.where(self.fractional_coordinates_supercell[:, 2] > supercell_dimensions[2])
        ids_remove = np.unique(np.concatenate((ids_remove_a, ids_remove_b, ids_remove_c)))
        self.fractional_coordinates_supercell = np.delete(self.fractional_coordinates_supercell, ids_remove, axis=0)
        self.atomic_numbers_supercell = np.delete(self.atomic_numbers_supercell, ids_remove)

        # transform fractional to cartesian coordinates and instantiate atoms in super().__init__
        self.cartesian_coordinates_supercell = np.dot(self.fractional_coordinates_supercell, self.basis_vectors)
        super().__init__(self.atomic_numbers_supercell, self.cartesian_coordinates_supercell)

    @classmethod
    def from_POSCAR(cls, file_path: str):
        with open(file_path, "r") as file:
            lines = file.readlines()
        if not len(lines) >= 9:
            return False
        scale, latvec_a, latvec_b, latvec_c = lines[1:5]
        species, numbers = lines[5].strip(), lines[6]
        mode, positions = lines[7].strip(), lines[8:]
        try:
            scale = float(scale)
            latvec_a = np.fromstring(latvec_a, sep=" ")
            latvec_b = np.fromstring(latvec_b, sep=" ")
            latvec_c = np.fromstring(latvec_c, sep=" ")
            species = re.split(r"\s+", species)
            numbers = np.fromstring(numbers, sep=" ", dtype=int)
            positions = np.array([np.fromstring(pos, sep=" ") for pos in positions])
            basis_vectors = np.array([latvec_a, latvec_b, latvec_c])
        except ValueError:
            return False, "Error: faulty formatting of the POSCAR file."
        if len(numbers) != len(species) or len(positions) != len(species):
            return False, "Error: faulty formatting of the POSCAR file."
        if mode.lower() != "direct":
            return False, "Currently, Molara can only process direct mode in POSCAR files."
        atomic_numbers = np.array([element_symbol_to_atomic_number(symb) for symb in species], dtype=int)
        return cls(atomic_numbers, positions, scale * basis_vectors)
