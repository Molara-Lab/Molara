"""Generates a 3D array of values of the mos of  molecule"""

cimport numpy as npc
import numpy as np
from cython.cimports.molara.eval.mos import calculate_mo_cartesian
from cython import boundscheck, exceptval, wraparound

from molara.util.constants import ANGSTROM_TO_BOHR
from libc.stdint cimport int64_t

cdef double ANGSTROM_TO_BOHR_ = ANGSTROM_TO_BOHR

__copyright__ = "Copyright 2024, Molara"


cpdef generate_voxel_grid(
        double[:] origin,
        double[:,:] voxel_size,
        int64_t[:] voxel_count,
        aos,
        mo_coeff,
        cut_off_distances,
):
    """
    Generates a 3D array of values. The voxel grid is defined by the origin, voxel size and voxel count.

    :param origin: The origin of the voxel grid
    :param voxel_size: A 2D array (3x3) defining the size of voxels in each direction
    :param voxel_count: The number of voxels in each direction
    :param aos: The atomic orbitals parameters
    :param mo_coeff: The molecular orbital coefficients
    :return: A 3D array of values
    """
    cdef int number_of_aos = len(aos)
    cdef double[:, :, :] voxel_grid = npc.ndarray(shape=(voxel_count[0], voxel_count[1], voxel_count[2]), dtype=np.float64)
    cdef double[:, :] orbital_positions = npc.ndarray(shape=(number_of_aos, 3), dtype=np.float64)
    cdef int64_t[:,:] orbital_ijks = npc.ndarray(shape=(number_of_aos, 3), dtype=np.intp)
    cdef int max_length = 0, ao_index, len_ao
    cdef double[:] electron_position = npc.ndarray(shape=3)
    cdef int voxel_count_i = voxel_count[0], voxel_count_j = voxel_count[1], voxel_count_k = voxel_count[2]



    for ao in aos:
        len_ao = len(ao.exponents)
        if len_ao > max_length:
            max_length = len_ao

    cdef double[:] aos_values = npc.ndarray(shape=number_of_aos)
    cdef double[:, :] orbital_exponents = npc.ndarray(shape=(number_of_aos, max_length), dtype=np.float64)
    cdef double[:, :] orbital_coefficients = npc.ndarray(shape=(number_of_aos, max_length), dtype=np.float64)
    cdef double[:, :] orbital_norms = npc.ndarray(shape=(number_of_aos, max_length), dtype=np.float64)
    cdef int64_t[:] shells_temp = npc.ndarray(shape=number_of_aos, dtype=np.int64)
    cdef int skip_shells = 0, shell_index = 0
    cdef int number_of_shells = 0

    # Prepare the data
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

    cdef int64_t[:] shells = npc.ndarray(shape=number_of_shells, dtype=np.int64)
    shells = shells_temp[:number_of_shells]

    cdef double[3] voxel_size_i = [voxel_size[0, 0],
                                  voxel_size[0, 1],
                                  voxel_size[0, 2]]
    cdef double[3] voxel_size_j = [voxel_size[1, 0],
                                  voxel_size[1, 1],
                                  voxel_size[1, 2]]
    cdef double[3] voxel_size_k = [voxel_size[2, 0],
                                  voxel_size[2, 1],
                                  voxel_size[2, 2]]

    # Calculate the grid
    voxel_grid_loops(
        electron_position,
        voxel_grid,
        voxel_size_i,
        voxel_size_j,
        voxel_size_k,
        voxel_count_i,
        voxel_count_j,
        voxel_count_k,
        origin,
        orbital_positions,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        shells,
        mo_coeff,
        aos_values,
        cut_off_distances,
    )
    return voxel_grid

@exceptval(check=False)
@boundscheck(False)
@wraparound(False)
cdef inline void voxel_grid_loops(
        double[:] electron_position,
        double[:, :, :] voxel_grid,
        double[:] voxel_size_i,
        double[:] voxel_size_j,
        double[:] voxel_size_k,
        int voxel_count_i,
        int voxel_count_j,
        int voxel_count_k,
        double[:] origin,
        double[:,:] orbital_positions,
        double[:,:] orbital_coefficients,
        double[:,:] orbital_exponents,
        double[:,:] orbital_norms,
        int64_t[:] shells,
        double[:] mo_coeff,
        double[:] aos_values,
        double[:] cut_off_distances) nogil:

    cdef int i, j, k
    cdef double[3] electron_position_i, electron_position_j, electron_position_k

    for i in range(voxel_count_i):
        electron_position_i[0] = voxel_size_i[0] * i
        electron_position_i[1] = voxel_size_i[1] * i
        electron_position_i[2] = voxel_size_i[2] * i
        for j in range(voxel_count_j):
            electron_position_j[0] = voxel_size_j[0] * j
            electron_position_j[1] = voxel_size_j[1] * j
            electron_position_j[2] = voxel_size_j[2] * j
            for k in range(voxel_count_k):
                electron_position_k[0] = voxel_size_k[0] * k
                electron_position_k[1] = voxel_size_k[1] * k
                electron_position_k[2] = voxel_size_k[2] * k
                electron_position[0] = (electron_position_i[0] + electron_position_j[0] + electron_position_k[0])
                electron_position[1] = (electron_position_i[1] + electron_position_j[1] + electron_position_k[1])
                electron_position[2] = (electron_position_i[2] + electron_position_j[2] + electron_position_k[2])
                electron_position[0] = (electron_position[0] + origin[0]) * ANGSTROM_TO_BOHR_
                electron_position[1] = (electron_position[1] + origin[1]) * ANGSTROM_TO_BOHR_
                electron_position[2] = (electron_position[2] + origin[2]) * ANGSTROM_TO_BOHR_

                voxel_grid[i, j, k] = calculate_mo_cartesian(
                    electron_position,
                    orbital_positions,
                    orbital_coefficients,
                    orbital_exponents,
                    orbital_norms,
                    shells,
                    mo_coeff,
                    aos_values,
                    cut_off_distances,
                )
