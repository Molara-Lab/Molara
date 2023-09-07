import numpy as np
import pyrr

from .Atom import Atom
from ..Rendering.Sphere import Spheres


class Drawer:
    def __init__(self, atoms: [Atom], bonds: np.ndarray):
        self.subdivisions_sphere = 20
        self.subdivisions_cylinder = 20
        self.unique_spheres = [Spheres() for _ in range(119)]
        self.atoms = atoms
        self.bonds = bonds
        self.set_sphere_model_matrices()

    def set_atoms(self, atoms):
        self.atoms = atoms

    def reset_sphere_model_matrices(self):
        for sphere in self.unique_spheres:
            sphere.model_matrices = None

    def set_sphere_model_matrices(self):
        self.reset_sphere_model_matrices()
        for atom in self.atoms:
            if self.unique_spheres[atom.atomic_number].model_matrices is None:
                self.unique_spheres[atom.atomic_number] = Spheres(atom.cpk_color, self.subdivisions_sphere)
                self.unique_spheres[atom.atomic_number].model_matrices = calculate_sphere_model_matrix(atom)
            else:
                self.unique_spheres[atom.atomic_number].model_matrices = np.concatenate(
                    (self.unique_spheres[atom.atomic_number].model_matrices, calculate_sphere_model_matrix(atom))
                )
        # print(self.unique_spheres[1].model_matrices)


def calculate_sphere_model_matrix(atom):
    translation_matrix = pyrr.matrix44.create_from_translation(pyrr.Vector3(atom.position))
    scale_matrix = pyrr.matrix44.create_from_scale(pyrr.Vector3([atom.vdw_radius / 4] * 3))
    return np.array([np.array(scale_matrix @ translation_matrix, dtype=np.float32)], dtype=np.float32)
