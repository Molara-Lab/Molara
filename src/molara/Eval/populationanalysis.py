from molara.structure.molecule import Molecule
from molara.structure.basisset import contracted_overlap
import numpy as np
import time as t

class PopulationAnalysis:
    """
    PopulationAnalysis class to check the basisset and molecular orbital coefficients
    """

    def __init__(self, molecule: Molecule):
        """
        Initialize the PopulationAnalysis class with a molecule object

        :param molecule: Molecule object
        """
        start = t.time()
        self.molecule = molecule
        self.basis_functions = []
        self.basis_functions_positions = []
        self.mo_coefficients = molecule.mos.coefficients.transpose()
        for atom in molecule.atoms:
            for orbital_label, orbital in atom.basis_set.basis_functions.items():
                print(orbital_label)
                self.basis_functions.append(orbital)
                self.basis_functions_positions.append(atom.position * 1.8897259886)
        print(len(self.basis_functions))
        self.overlap_matrix_ao = np.zeros((len(self.basis_functions), len(self.basis_functions)))
        self.overlap_matrix_mo = np.zeros((len(self.basis_functions), len(self.basis_functions)))
        for i, basis_function_i in enumerate(self.basis_functions):
            for j, basis_function_j in enumerate(self.basis_functions):
                self.overlap_matrix_ao[i, j] = contracted_overlap(basis_function_j,
                                                          basis_function_i,
                                                          self.basis_functions_positions[j],
                                                          self.basis_functions_positions[i])
        self.overlap_matrix_mo = np.dot(self.mo_coefficients.T, np.dot(self.overlap_matrix_ao, self.mo_coefficients))
        np.set_printoptions(linewidth=np.inf, precision=8, threshold=np.inf)
        self.number_of_electrons = 0
        for occupation_number in molecule.mos.occupations:
            self.number_of_electrons += occupation_number
        n_occ = int(self.number_of_electrons / 2)
        d_matrix = np.dot(self.mo_coefficients[:, :n_occ], self.mo_coefficients[:, :n_occ].T) * 2
        print(self.overlap_matrix_mo)
        print()
        print(d_matrix)
        print()
        print(np.sum(d_matrix * self.overlap_matrix_ao))
        print(t.time() - start)


