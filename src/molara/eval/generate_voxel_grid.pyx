"""Generates a 3D array of values of the mos of  molecule"""

cimport numpy as npc
import numpy as np
from cython.cimports.molara.eval.mos import calculate_mo_cartesian
from molara.data.constants import ANGSTROM_TO_BOHR

__copyright__ = "Copyright 2024, Molara"


cpdef generate_voxel_grid(
        double[:] origin,
        double[:, :] direction,
        double[:] voxel_size,
        int[:] voxel_count,
        aos,
        mo_coeff,
):
    """
    Generates a 3D array of values. The voxel grid is defined by the origin, direction, voxel size and voxel count.

    :param origin: The origin of the voxel grid
    :param direction: The direction of the voxel grid
    :param voxel_size: The size of each voxel
    :param voxel_count: The number of voxels in each direction
    :param aos: The atomic orbitals parameters
    :param mo_coeff: The molecular orbital coefficients
    :return: A 3D array of values
    """
    cdef int number_of_aos = len(aos)
    cdef double[:, :, :] voxel_grid = npc.ndarray(shape=(voxel_count[0], voxel_count[1], voxel_count[2]), dtype=np.float64)
    cdef double[:, :] orbital_positions = npc.ndarray(shape=(number_of_aos, 3), dtype=np.float64)
    cdef long[:,:] orbital_ijks = npc.ndarray(shape=(number_of_aos, 3), dtype=np.intp)
    cdef int max_length = 0, ao_index, i, j, k, l, len_ao
    cdef double[:] electron_position = npc.ndarray(shape=3)
    cdef double[:] electron_position_i = npc.ndarray(shape=3)
    cdef double[:] electron_position_j = npc.ndarray(shape=3)
    cdef double[:] electron_position_k = npc.ndarray(shape=3)
    cdef double scaled_direction
    cdef int voxel_count_i = voxel_count[0], voxel_count_j = voxel_count[1], voxel_count_k = voxel_count[2]



    for ao in aos:
        len_ao = len(ao.exponents)
        if len_ao > max_length:
            max_length = len_ao

    cdef double[:] aos_values = npc.ndarray(shape=number_of_aos)
    cdef double[:, :] orbital_exponents = npc.ndarray(shape=(number_of_aos, max_length), dtype=np.float64)
    cdef double[:, :] orbital_coefficients = npc.ndarray(shape=(number_of_aos, max_length), dtype=np.float64)
    cdef double[:, :] orbital_norms = npc.ndarray(shape=(number_of_aos, max_length), dtype=np.float64)
    cdef long[:] shells_temp = npc.ndarray(shape=number_of_aos, dtype=np.intp)
    cdef int skip_shells = 0, shell_index = 0
    cdef int number_of_shells = 0
    orbital_exponents[:,:] = 0
    orbital_coefficients[:,:] = 0
    orbital_norms[:,:] = 0
    orbital_positions[:,:] = 0
    orbital_ijks[:,:] = 0
    electron_position[:] = 0
    for ao_index, ao in enumerate(aos):
        for i in range(len(ao.exponents)):
            orbital_exponents[ao_index, i] = ao.exponents[i]
            orbital_coefficients[ao_index, i] = ao.coefficients[i]
            orbital_norms[ao_index, i] = ao.norms[i]
        for i in range(3):
            orbital_positions[ao_index, i] = ao.position[i] * ANGSTROM_TO_BOHR
            orbital_ijks[ao_index, i] = ao.ijk[i]
        if skip_shells == 0:
            if sum(ao.ijk) == 0:
                shells_temp[shell_index] = 0
            elif sum(ao.ijk) == 1:
                shells_temp[shell_index] = 1
                skip_shells = 2
            elif sum(ao.ijk) == 2:
                shells_temp[shell_index] = 2
                skip_shells = 5
            elif sum(ao.ijk) == 3:
                shells_temp[shell_index] = 3
                skip_shells = 9
            elif sum(ao.ijk) == 4:
                shells_temp[shell_index] = 4
                skip_shells = 14
            shell_index += 1
            number_of_shells += 1
        else:
            skip_shells -= 1

    cdef long[:] shells = npc.ndarray(shape=number_of_shells, dtype=np.intp)
    shells = shells_temp[:number_of_shells]


    for i in range(voxel_count_i):
        for l in range(3):
            scaled_direction = direction[0,l] * voxel_size[0] * i
            electron_position_i[l] = scaled_direction
        for j in range(voxel_count_j):
            for l in range(3):
                scaled_direction = direction[1, l] * voxel_size[1] * j
                electron_position_j[l] = scaled_direction
            for k in range(voxel_count_k):
                for l in range(3):
                    scaled_direction = direction[2, l] * voxel_size[2] * k
                    electron_position_k[l] = scaled_direction
                    electron_position[l] = ((electron_position_i[l] + electron_position_j[l] + electron_position_k[l]))
                    electron_position[l] = (electron_position[l] + origin[l]) * ANGSTROM_TO_BOHR
                voxel_grid[i, j, k] = calculate_mo_cartesian(
                    electron_position,
                    orbital_positions,
                    orbital_coefficients,
                    orbital_exponents,
                    orbital_norms,
                    shells,
                    mo_coeff,
                    aos_values,
                )

    return voxel_grid
