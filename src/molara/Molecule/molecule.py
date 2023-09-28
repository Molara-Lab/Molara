from __future__ import annotations

import numpy as np
import numpy.typing as npt

from .atom import Atom, element_symbol_to_atomic_number
from .drawer import Drawer


class Molecule:
    def __init__(self, atomic_numbers: np.ndarray, coordinates: np.ndarray) -> None:
        self.atomic_numbers = np.array(atomic_numbers)
        self.atoms = []
        self.vdw_rads: list[np.float32] = []
        self.subdivisions = 20
        self.unique_atomic_numbers: list[int] = []
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

    def center_coordinates(self) -> None:
        coordinates = np.array([atom.position for atom in self.atoms])
        center = np.average(coordinates, weights=[atom.atomic_mass for atom in self.atoms], axis=0)
        for _i, atom in enumerate(self.atoms):
            atom.position -= center
        self.drawer.set_atoms(self.atoms)
        self.drawer.set_sphere_model_matrices()
        self.drawer.set_cylinder_model_matrices()


def read_xyz(file_path: str) -> Molecule:
    with open(file_path) as file:
        lines = file.readlines()

        num_atoms = int(lines[0])
        atomic_numbers = []
        coordinates = []

        for line in lines[2 : 2 + num_atoms]:
            atom_info = line.split()
            if atom_info[0].isnumeric():
                atomic_numbers.append(int(atom_info[0]))
            else:
                atomic_numbers.append(element_symbol_to_atomic_number(atom_info[0]))
            coordinates.append([float(coord) for coord in atom_info[1:4]])

    file.close()

    return Molecule(np.array(atomic_numbers), np.array(coordinates))


def read_coord(file_path: str) -> Molecule:
    """Imports a coord file
    Returns the Molecule.
    """
    with open(file_path) as file:
        lines = file.readlines()  # To skip first row

    atomic_numbers = []
    coordinates = []

    for line in lines[1:]:
        if "$" in line:
            break

        atom_info = line.split()
        if atom_info[-1].isnumeric():
            atomic_numbers.append(int(atom_info[-1]))
        else:
            atom_info[-1] = atom_info[-1].capitalize()
            atomic_numbers.append(element_symbol_to_atomic_number(atom_info[-1]))
        coordinates.append([float(coord) * 0.529177249 for coord in atom_info[:3]])

    return Molecule(np.array(atomic_numbers), np.array(coordinates))
