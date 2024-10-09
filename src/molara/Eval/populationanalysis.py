from molara.structure.molecule import Molecule
from molara.structure.basisset import contracted_overlap
from molara.data.constants import ANGSTROM_TO_BOHR
import numpy as np


class PopulationAnalysis:
    """
    PopulationAnalysis class to check the basisset and molecular orbital coefficients
    """

    def __init__(self, molecule: Molecule):
        """
        Initialize the PopulationAnalysis class with a molecule object

        :param molecule: Molecule object
        """
        print("PopulationAnalysis")
        self.mo_type = molecule.mos.type
        self.molecule = molecule
        self.basis_functions_labels = molecule.mos.basis_functions
        self.basis_functions = []
        self.basis_functions_positions = []
        self.mo_coefficients = molecule.mos.coefficients
        for atom in molecule.atoms:
            for orbital_label, orbital in atom.basis_set.basis_functions.items():
                self.basis_functions.append(orbital)
                self.basis_functions_positions.append(atom.position * ANGSTROM_TO_BOHR)

        if self.mo_type == "cartesian":
            self.overlap_matrix_ao = np.zeros(
                (len(self.basis_functions), len(self.basis_functions))
            )
            self.overlap_matrix_mo = np.zeros(
                (len(self.basis_functions), len(self.basis_functions))
            )
            for i, basis_function_i in enumerate(self.basis_functions):
                for j, basis_function_j in enumerate(self.basis_functions):
                    self.overlap_matrix_ao[i, j] = contracted_overlap(
                        basis_function_j,
                        basis_function_i,
                        self.basis_functions_positions[j],
                        self.basis_functions_positions[i],
                    )
            self.overlap_matrix_mo = np.dot(
                self.mo_coefficients.T,
                np.dot(self.overlap_matrix_ao, self.mo_coefficients),
            )
            self.number_of_electrons = 0
            for occupation_number in molecule.mos.occupations:
                self.number_of_electrons += occupation_number
            n_occ = int(self.number_of_electrons / 2)
            self.d_matrix = (
                np.dot(
                    self.mo_coefficients[:, :n_occ], self.mo_coefficients[:, :n_occ].T
                )
                * 2
            )
            print(np.sum(self.d_matrix * self.overlap_matrix_ao))
        else:
            self.mo_coefficients_spherical = molecule.mos.coefficients_spherical
            self.transformation_matrix = (
                self.molecule.mos.transformation_matrix_spherical_cartesian
            )
            self.number_of_electrons = 0
            for occupation_number in molecule.mos.occupations:
                self.number_of_electrons += occupation_number
            self.overlap_matrix_ao = np.zeros(
                (len(self.basis_functions), len(self.basis_functions))
            )
            self.overlap_matrix_mo = np.zeros(
                (len(self.basis_functions), len(self.basis_functions))
            )
            for i, basis_function_i in enumerate(self.basis_functions):
                for j, basis_function_j in enumerate(self.basis_functions):
                    self.overlap_matrix_ao[i, j] = contracted_overlap(
                        basis_function_j,
                        basis_function_i,
                        self.basis_functions_positions[j],
                        self.basis_functions_positions[i],
                    )
            self.overlap_matrix_ao_spherical = np.dot(
                self.transformation_matrix,
                np.dot(self.overlap_matrix_ao, self.transformation_matrix.T),
            )
            self.overlap_matrix_mo = np.dot(
                self.mo_coefficients_spherical.T,
                np.dot(
                    self.overlap_matrix_ao_spherical, self.mo_coefficients_spherical
                ),
            )
            n_occ = int(self.number_of_electrons / 2)
            self.d_matrix = (
                np.dot(
                    self.mo_coefficients_spherical[:, :n_occ],
                    self.mo_coefficients_spherical[:, :n_occ].T,
                )
                * 2
            )
            print(np.sum(self.d_matrix * self.overlap_matrix_ao_spherical))
