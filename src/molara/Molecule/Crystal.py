import re

import numpy as np
import numpy.typing as npt

from .Atom import element_symbol_to_atomic_number
from .Molecule import *

standard_supercell = np.array([1, 1, 1], dtype=int)


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
        atomic_numbers: npt.ArrayLike,
        coordinates: npt.ArrayLike,
        basis_vectors: npt.ArrayLike,
        supercell_dimensions: npt.ArrayLike = standard_supercell,
    ):
        coordinates_translation = []
        atomic_numbers_translation = []
        dim0, dim1, dim2 = supercell_dimensions
        for atomic_number_i, coordinates_i in zip(atomic_numbers, coordinates):
            coordinates_cartesian = np.dot(basis_vectors.T, coordinates_i)
            for i in range(dim0 + 1):
                for j in range(dim1 + 1):
                    for k in range(dim2 + 1):
                        if coordinates_i[0] + i > dim0 or coordinates_i[1] + j > dim1 or coordinates_i[2] + k > dim2:
                            continue
                        new_coordinates = (
                            coordinates_cartesian + i * basis_vectors[0] + j * basis_vectors[1] + k * basis_vectors[2]
                        )
                        coordinates_translation += [new_coordinates]
                        atomic_numbers_translation += [atomic_number_i]

        coordinates_translation = np.array(coordinates_translation)
        atomic_numbers_translation = np.array(atomic_numbers_translation, dtype=int)
        super().__init__(atomic_numbers_translation, coordinates_translation)


def read_POSCAR(file_path: str):
    with open(file_path, "r") as file:
        lines = file.readlines()
    if not len(lines) >= 9:
        return False
    lines[0]
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
    return Crystal(atomic_numbers, positions, scale * basis_vectors)
