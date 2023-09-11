import numpy as np

from molara.Molecule.Molecule import *

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

    def __init__(self, atomic_numbers, coordinates, basis_vectors, supercell_dimensions=standard_supercell):
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
