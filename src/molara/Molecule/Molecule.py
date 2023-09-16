import numpy as np
import numpy.typing as npt

from .Atom import Atom, element_symbol_to_atomic_number
from .Drawer import Drawer


class Molecule:
    def __init__(self, atomic_numbers: npt.ArrayLike, coordinates: npt.ArrayLike):
        self.atomic_numbers = np.array(atomic_numbers)
        self.atoms = []
        self.vdw_rads = []
        self.subdivisions = 20
        self.unique_atomic_numbers = []
        for i, atomic_number in enumerate(atomic_numbers):
            atom = Atom(atomic_number, coordinates[i])
            self.atoms.append(atom)
            if atomic_number not in self.unique_atomic_numbers:
                self.unique_atomic_numbers.append(atomic_number)

        self.bonded_pairs = self.calculate_bonds()
        self.drawer = Drawer(self.atoms, self.bonded_pairs)

    def calculate_bonds(self):
        bonded_pairs = []

        vdw_radii = np.array([atom.vdw_radius for atom in self.atoms])
        coordinates = np.array([atom.position for atom in self.atoms])

        for i in range(len(self.atoms)):
            atom1_coord = coordinates[i]
            atom1_radius = vdw_radii[i]

            distances = np.linalg.norm(coordinates - atom1_coord, axis=1)
            mean_radii = (vdw_radii + atom1_radius) / 1.75

            bonded_indices = np.where(distances <= mean_radii)[0]
            bonded_pairs.extend([(i, j) for j in bonded_indices if j > i])

        if bonded_pairs:
            return np.array(bonded_pairs)

        return np.array([[-1, -1]], dtype=np.int_)

    def add_atom(self, atomic_number: int, coordinate: npt.ArrayLike):
        atom = Atom(atomic_number, coordinate)
        self.atoms.append(atom)
        self.bonded_pairs = self.calculate_bonds()

    def remove_atom(self, index: int):
        self.atoms.pop(index)
        self.bonded_pairs = self.calculate_bonds()

    def center_coordinates(self):
        coordinates = np.array([atom.position for atom in self.atoms])
        center = np.average(coordinates, weights=[atom.atomic_mass for atom in self.atoms], axis=0)
        for _i, atom in enumerate(self.atoms):
            atom.position -= center
        self.drawer.set_atoms(self.atoms)
        self.drawer.set_sphere_model_matrices()
        self.drawer.set_cylinder_model_matrices()
