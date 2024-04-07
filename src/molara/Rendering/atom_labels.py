"""Function for rendering atom labels."""

import numpy as np
from molara.Structure.structure import Structure
from molara.Structure.molecule import Molecule
from molara.Rendering.camera import Camera


def init_atom_number(structure: Structure) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Initialize the labels for numbering atoms.

    :param structure: Structure object
    """
    assert isinstance(structure, Molecule)
    number_of_atoms = len(structure.atoms)

    # initialize the positions array, taking into account, the number of digits for all numbers. The first atom has
    # index 1.
    if number_of_atoms < 10:
        number_of_digits = number_of_atoms
    else:
        # the number of digits for the first 9 atoms is 9.
        number_of_digits = 9
        number_of_atoms -= 9
        # Calculate the number of digits for the atoms from 10 to 99.
        temp_number = number_of_atoms % 100
        number_of_digits += 2 * temp_number
        number_of_atoms = number_of_atoms // 100
        # Calculate the number of digits for the atoms from 100 to 999.
        temp_number = number_of_atoms % 10
        number_of_digits += 3 * temp_number * 100
        number_of_atoms = number_of_atoms // 10
        # No more than 999 atoms can be labeled.

    # Initialize the arrays for the atom numbers.
    positions = np.zeros((number_of_digits, 2), dtype=np.float32)
    digits = np.zeros(number_of_digits, dtype=np.int32)
    scales = np.zeros(number_of_digits, dtype=np.float32)

    return positions, digits, scales, number_of_digits


def calculate_atom_number_arrays(positions: np.ndarray,
                                 digits: np.ndarray,
                                 scales: np.ndarray,
                                 structure: Structure, camera: Camera) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculate the arrays for the atom numbers.

    :param positions: Positions of the numbers.
    :param digits: The digits to be displayed.
    :param scales: The scales of the numbers.
    :param structure: Structure object
    """
    assert isinstance(structure, Molecule)
    number_of_atoms = len(structure.atoms)

    digits_offset = 0.35
    digits_width = 0.21
    screen_positions = np.zeros(2, dtype=np.float32)

    i = 0
    digit_index = 0
    while i < number_of_atoms:
        atom_position_3d = structure.atoms[i].position
        rel_atom_position_3d = atom_position_3d - camera.position
        distance_atom_camera = np.linalg.norm(rel_atom_position_3d)
        inv_distance_atom_camera = 1 / distance_atom_camera

        scale = inv_distance_atom_camera * 0.2
        rel_atom_position_3d /= distance_atom_camera
        dir_cam_target = camera.target - camera.position
        dir_cam_target /= np.linalg.norm(dir_cam_target)
        min_size = 0.01

        # check if scale too small or atom behind camera. (dirty)
        if scale < min_size or np.dot(rel_atom_position_3d, dir_cam_target) < 0:
            if i < 9:
                scales[digit_index] = 0
                digit_index += 1
            elif i < 99:
                scales[digit_index] = 0
                digit_index += 1
                scales[digit_index] = 0
                digit_index += 1
            elif i < 999:
                scales[digit_index] = 0
                digit_index += 1
                scales[digit_index] = 0
                digit_index += 1
                scales[digit_index] = 0
                digit_index += 1
            i += 1
            continue

        atom_positions_cam_space = camera.view_matrix_inv[:3,:3] @ rel_atom_position_3d
        atom_positions_clip_space = atom_positions_cam_space / camera.projection_matrix_inv[1, 1]
        screen_positions[0] = - atom_positions_clip_space[0] / atom_positions_cam_space[2]
        screen_positions[1] = - atom_positions_clip_space[1] / atom_positions_cam_space[2]

        scaled_digits_offset = digits_offset * scale
        scaled_digits_width = digits_width * scale

        if i < 9:
            positions[digit_index] = screen_positions
            digits[digit_index] = i + 1
            scales[digit_index] = scale
            digit_index += 1
        elif i < 99:
            offset_array = np.array([scaled_digits_offset, 0], dtype=np.float32)
            positions[digit_index,:] = screen_positions - offset_array
            digits[digit_index] = (i + 1) // 10

            scales[digit_index] = scale
            digit_index += 1
            positions[digit_index,:] = screen_positions + offset_array
            digits[digit_index] = (i + 1) % 10

            scales[digit_index] = scale
            digit_index += 1
        elif i < 999:
            offset_array = np.array([scaled_digits_width + scaled_digits_offset, 0], dtype=np.float32)
            positions[digit_index,:] = screen_positions - offset_array
            digits[digit_index] = (i + 1) // 100

            scales[digit_index] = scale
            digit_index += 1
            positions[digit_index,:] = screen_positions
            digits[digit_index] = ((i + 1) // 10) % 10

            scales[digit_index] = scale
            digit_index += 1
            positions[digit_index,:] = screen_positions + offset_array
            digits[digit_index] = (i + 1) % 10

            scales[digit_index] = scale
            digit_index += 1

        i += 1

    return positions, digits, scales
