"""Function for rendering atom labels."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from molara.rendering.camera import Camera
    from molara.structure.structure import Structure


def init_atom_number(structure: Structure) -> tuple[np.ndarray, np.ndarray]:
    """Initialize the labels for numbering atoms.

    :param structure: Structure object
    """
    number_of_atoms = len(structure.atoms)

    # Initialize the arrays for the atom numbers.
    positions_3d = np.zeros((number_of_atoms, 3), dtype=np.float32)
    digits = np.zeros(number_of_atoms, dtype=np.int32)

    return digits, positions_3d


def calculate_atom_number_arrays(
    digits: np.ndarray,
    positions_3d: np.ndarray,
    structure: Structure,
    camera: Camera,
) -> None:
    """Calculate the arrays for the atom numbers.

    :param digits: The digits to be displayed.
    :param positions_3d: The 3D positions of the atoms.
    :param structure: Structure object
    :param camera: Camera object
    """
    number_of_atoms = len(structure.atoms)

    i = 0
    while i < number_of_atoms:
        atom_position_3d = structure.atoms[i].position

        atom_cam_vec = camera.position - atom_position_3d
        atom_cam_vec /= np.linalg.norm(atom_cam_vec)
        position_number_3d = (
            atom_position_3d
            + atom_cam_vec
            * structure.drawer.sphere_default_radius
            * structure.drawer.sphere_scale
            * structure.atoms[i].vdw_radius
            * 1.75
        )
        positions_3d[i] = position_number_3d
        digits[i] = i + 1

        i += 1
