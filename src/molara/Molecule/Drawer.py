import numpy as np
import pyrr

from molara.Molecule.Atom import Atom
from molara.Rendering.Cylinder import Cylinders
from molara.Rendering.Sphere import Spheres


class Drawer:
    def __init__(self, atoms: [Atom], bonds: np.ndarray) -> None:
        self.subdivisions_sphere = 15
        self.subdivisions_cylinder = 20
        self.unique_spheres = [Spheres() for _ in range(119)]
        self.unique_cylinders = [Cylinders() for _ in range(119)]
        self.atoms = atoms
        self.bonds = bonds
        self.set_sphere_model_matrices()
        self.set_cylinder_model_matrices()

    def set_atoms(self, atoms: [Atom]) -> None:
        """
        Sets the atoms to be displayed.
        :param atoms: List of atoms to be displayed.
        :return:
        """
        self.atoms = atoms

    def reset_Spheres_model_matrices(self) -> None:
        """
        Resets the model matrices for the spheres.
        :return:
        """
        for sphere in self.unique_spheres:
            sphere.model_matrices = None

    def reset_Cylinders_model_matrices(self) -> None:
        """
        Resets the model matrices for the cylinders.
        :return:
        """
        for cylinder in self.unique_cylinders:
            cylinder.model_matrices = None

    def set_cylinder_model_matrices(self) -> None:
        """
        Sets the model matrices for the cylinders.
        :return:
        """
        self.reset_Cylinders_model_matrices()
        for atom in self.atoms:
            if self.unique_cylinders[atom.atomic_number].model_matrices is None:
                self.unique_cylinders[atom.atomic_number] = Cylinders(atom.cpk_color, self.subdivisions_cylinder)
        for bond in self.bonds:
            if bond[0] != -1:
                model_matrices = calculate_bond_cylinders_model_matrix(self.atoms[bond[0]], self.atoms[bond[1]])
                if self.unique_cylinders[self.atoms[bond[0]].atomic_number].model_matrices is None:
                    self.unique_cylinders[self.atoms[bond[0]].atomic_number].model_matrices = model_matrices[0]
                else:
                    self.unique_cylinders[self.atoms[bond[0]].atomic_number].model_matrices = np.concatenate(
                        (self.unique_cylinders[self.atoms[bond[0]].atomic_number].model_matrices, model_matrices[0])
                    )
                if self.unique_cylinders[self.atoms[bond[1]].atomic_number].model_matrices is None:
                    self.unique_cylinders[self.atoms[bond[1]].atomic_number].model_matrices = model_matrices[1]
                else:
                    self.unique_cylinders[self.atoms[bond[1]].atomic_number].model_matrices = np.concatenate(
                        (self.unique_cylinders[self.atoms[bond[1]].atomic_number].model_matrices, model_matrices[1])
                    )

    def set_sphere_model_matrices(self) -> None:
        """
        Sets the model matrices for the spheres.
        :return:
        """
        self.reset_Spheres_model_matrices()
        for atom in self.atoms:
            if self.unique_spheres[atom.atomic_number].model_matrices is None:
                self.unique_spheres[atom.atomic_number] = Spheres(atom.cpk_color, self.subdivisions_sphere)
                self.unique_spheres[atom.atomic_number].model_matrices = calculate_sphere_model_matrix(atom)
            else:
                self.unique_spheres[atom.atomic_number].model_matrices = np.concatenate(
                    (self.unique_spheres[atom.atomic_number].model_matrices, calculate_sphere_model_matrix(atom))
                )


def calculate_sphere_model_matrix(atom: Atom) -> np.ndarray:
    """
    Calculates the model matrix for an atom displayed as a sphere.
    :param atom: Atom
    :return: Model matrix for the sphere.
    """
    # Calculate the translation matrix to translate the sphere to the correct position.
    translation_matrix = pyrr.matrix44.create_from_translation(pyrr.Vector3(atom.position))
    # Calculate the scale matrix to scale the sphere to the correct size.
    scale_matrix = pyrr.matrix44.create_from_scale(pyrr.Vector3([atom.vdw_radius / 6] * 3))
    # Return the model matrix for the sphere.
    return np.array([np.array(scale_matrix @ translation_matrix, dtype=np.float32)], dtype=np.float32)


def calculate_bond_cylinders_model_matrix(atom1: Atom, atom2: Atom) -> np.ndarray:
    """
    Calculates the model matrix for a cylinder between two atoms.
    :param atom1: Atom1
    :param atom2: Atom2
    :return: Model matrix for the cylinder between atom1 and atom2.
    """
    difference = atom1.position - atom2.position
    # Calculate the length of the cylinder.
    length = np.linalg.norm(difference)
    mid_point = (atom1.position + atom2.position) / 2
    # calculate the point 1 quarter between the 2 atoms
    position_1 = mid_point - difference / 4
    # calculate the point 3 quarter between the 2 atoms
    position_2 = mid_point + difference / 4
    # Calculate the rotation axis to rotate the cylinder to the correct orientation.
    y_axis = np.array([0, 1, 0], dtype=np.float32)
    if abs(y_axis @ difference) != 1:
        rotation_axis = np.cross(y_axis, difference)
        # Calculate the angle to rotate the cylinder to the correct orientation.
        rotation_angle = np.arccos(
            np.clip(
                np.dot(difference, y_axis) / (np.linalg.norm(difference)),
                -1,
                1,
            )
        )
    else:
        rotation_axis = np.array([0, 0, 1], dtype=np.float32)
        rotation_angle = 0
    translation_matrix_1 = pyrr.matrix44.create_from_translation(pyrr.Vector3(position_1))
    translation_matrix_2 = pyrr.matrix44.create_from_translation(pyrr.Vector3(position_2))
    # Calculate the rotation matrix to rotate the cylinder to the correct orientation.
    rotation_matrix = pyrr.matrix44.create_from_axis_rotation(rotation_axis, rotation_angle)
    # Calculate the scale matrix to scale the cylinder to the correct length.
    scale = pyrr.Vector3([0.15] * 3)
    scale[1] = length / 2
    scale_matrix = pyrr.matrix44.create_from_scale(pyrr.Vector3(scale))
    # Return the model matrix for the cylinder.
    rotation_scale_matrix = scale_matrix @ rotation_matrix
    return np.array(
        [
            np.array([rotation_scale_matrix @ translation_matrix_2], dtype=np.float32),
            np.array([rotation_scale_matrix @ translation_matrix_1], dtype=np.float32),
        ],
        dtype=np.float32,
    )
