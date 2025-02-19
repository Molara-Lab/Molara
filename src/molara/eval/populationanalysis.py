"""PopulationAnalysis class to check the basisset and molecular orbital coefficients for normalization."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from molara.structure.basisset import contracted_overlap
from molara.util.constants import ANGSTROM_TO_BOHR

if TYPE_CHECKING:
    from molara.structure.molecule import Molecule


class PopulationAnalysis:
    """PopulationAnalysis class to check the basisset and molecular orbital coefficients."""

    def __init__(self, molecule: Molecule) -> None:
        """Initialize the PopulationAnalysis class with a molecule object and calculate the number of electrons.

        :param molecule: Molecule object
        """
        self.mo_type = molecule.mos.basis_type
        self.molecule = molecule
        self.basis_functions_labels = molecule.mos.basis_functions
        self.basis_functions = []
        self.basis_functions_positions = []
        self.mo_coefficients = molecule.mos.coefficients

        # get the basis functions and positions
        for atom in molecule.atoms:
            for orbital in atom.basis_set.basis_functions.values():
                self.basis_functions.append(orbital)
                self.basis_functions_positions.append(atom.position * ANGSTROM_TO_BOHR)

        # Get the occupations and number of electrons
        self.number_of_electrons = sum(molecule.mos.occupations)
        self.occ_vector = np.array(molecule.mos.occupations)
        self.occ_matrix = np.diag(self.occ_vector)

        # calculate the overlap matrix for cartesian basis functions
        self.overlap_matrix_ao = np.zeros(
            (len(self.basis_functions), len(self.basis_functions)),
        )
        self.calculate_ao_overlap_cartesian()

        # initialize the overlap matrix for spherical basis functions
        self.overlap_matrix_ao_spherical: np.ndarray = np.array([])

        # initialize the overlap matrix for molecular orbitals
        self.overlap_matrix_mo: np.ndarray = np.array([])

        if self.mo_type == "Cartesian":
            self.d_matrix = np.dot(
                self.mo_coefficients[:, :],
                np.dot(self.occ_matrix, self.mo_coefficients[:, :].T),
            )
            self.population_matrix = self.d_matrix * self.overlap_matrix_ao
        else:
            self.mo_coefficients_spherical = molecule.mos.coefficients_spherical
            self.transformation_matrix = self.molecule.mos.transformation_matrix_spherical_cartesian
            self.overlap_matrix_ao_spherical = np.dot(
                self.transformation_matrix,
                np.dot(self.overlap_matrix_ao, self.transformation_matrix.T),
            )
            self.d_matrix = np.dot(
                self.mo_coefficients_spherical[:, :],
                np.dot(self.occ_matrix, self.mo_coefficients_spherical[:, :].T),
            )
            self.population_matrix = self.d_matrix * self.overlap_matrix_ao_spherical

        self.calculated_number_of_electrons = np.sum(self.population_matrix)

    def calculate_ao_overlap_cartesian(self) -> None:
        """Calculate the overlap matrix using cartesian basis functions."""
        for i, basis_function_i in enumerate(self.basis_functions):
            for j in range(i, len(self.basis_functions)):
                basis_function_j = self.basis_functions[j]
                self.overlap_matrix_ao[i, j] = contracted_overlap(
                    basis_function_j,
                    basis_function_i,
                    self.basis_functions_positions[j],
                    self.basis_functions_positions[i],
                )
                self.overlap_matrix_ao[j, i] = self.overlap_matrix_ao[i, j]
