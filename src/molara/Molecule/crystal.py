import re
from collections.abc import Sequence

import numpy as np
from numpy.typing import ArrayLike

from .atom import element_symbol_to_atomic_number
from .molecule import *


class Crystal(Molecule):
    """Creates a crystal supercell based on given particle positions in unit cell and lattice basis vectors.
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
        atomic_numbers: np.ndarray,
        coordinates: np.ndarray,
        basis_vectors: np.ndarray,
    ):
        self.atomic_numbers = atomic_numbers
        self.coordinates = coordinates
        self.basis_vectors = basis_vectors

        super().__init__(atomic_numbers, coordinates)

    # def make_supercell(self, supercell_dimensions: ArrayLike):
    #    coordinates_translation = []
    #    atomic_numbers_translation = []
    #    dim0, dim1, dim2 = supercell_dimensions
    #    for atomic_number_i, coordinates_i in zip(self.atomic_numbers, self.coordinates):
    #        coordinates_cartesian = np.dot(np.array(self.basis_vectors).T, coordinates_i)
    #        for i in range(dim0):
    #            for j in range(dim1):
    #                for k in range(dim2):
    #                    if (
    #                        coordinates_i[0] + i > dim0
    #                        or coordinates_i[1] + j > dim1
    #                        or coordinates_i[2] + k > dim2
    #                    ):
    #                        continue
    #                    new_coordinates = (
    #                        coordinates_cartesian
    #                        + i * self.basis_vectors[0]
    #                        + j * self.basis_vectors[1]
    #                        + k * self.basis_vectors[2]
    #                    )
    #                    coordinates_translation += [new_coordinates]
    #                    atomic_numbers_translation += [atomic_number_i]
    #    coordinates_translation = np.array(coordinates_translation)
    #    atomic_numbers_translation = np.array(atomic_numbers_translation, dtype=int)
    #    self.crystal = self.__init__(atomic_numbers_translation, coordinates_translation, self.basis_vectors)

    @classmethod
    def from_poscar(cls, file_path: str):
        with open(file_path) as file:
            lines = file.readlines()
        if not len(lines) >= 9:
            return False
        lines[0]
        scale_, latvec_a_, latvec_b_, latvec_c_ = lines[1:5]
        species_, numbers_ = lines[5].strip(), lines[6]
        mode, positions_ = lines[7].strip(), lines[8:]
        try:
            scale = float(scale_)
            latvec_a = np.fromstring(latvec_a_, sep=" ")
            latvec_b = np.fromstring(latvec_b_, sep=" ")
            latvec_c = np.fromstring(latvec_c_, sep=" ")
            species = re.split(r"\s+", species_)
            numbers = np.fromstring(numbers_, sep=" ", dtype=int)
            positions = np.array([np.fromstring(pos, sep=" ") for pos in positions_])
            basis_vectors = np.array([latvec_a, latvec_b, latvec_c])
        except ValueError:
            return False, "Error: faulty formatting of the POSCAR file."
        if len(numbers) != len(species) or len(positions) != len(species):
            return False, "Error: faulty formatting of the POSCAR file."
        if mode.lower() != "direct":
            return False, "Currently, Molara can only process direct mode in POSCAR files."
        atomic_numbers = np.array([element_symbol_to_atomic_number(symb) for symb in species], dtype=int)
        return cls(atomic_numbers, positions, scale * basis_vectors)
