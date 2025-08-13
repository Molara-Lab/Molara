"""Contain the class for the marching squares algorithm."""

import numpy as np
from libc.stdint cimport int64_t
from libc.math cimport abs
from cython import boundscheck, exceptval, cdivision


# Numbering of the corners of the grid and the edges:

# 3---------2    -----3-----
# |         |    |         |
# |         |    2         1
# |         |    |         |
# 0---------1    -----0-----




@exceptval(check=False)
@boundscheck(False)
@cdivision(True)
cpdef void marching_squares(double[:, :] grid,
                     double iso_value,
                     double[:] origin,
                     double[:, :] voxel_size,
                     int64_t[:] voxel_number,
                     float[:, :] lines_1,
                     float[:, :] lines_2,
                     ):
    """Perform the marching squares algorithm on a 2D grid.

    :param grid: 2D array representing the grid
    :param iso_value: The isoline value
    """
    cdef int64_t i, j, vertex_count_1, vertex_count_2, phase, ei, c11, c12, c21, c22, prefactor
    cdef double[:] corners
    cdef float[:] p11, p12, p21, p22, vertex1, vertex2
    cdef float t1, t2, v11, v12, v21, v22
    cdef int64_t[:, :] voxel_indices, edges_1_2


    corners = np.zeros(4, dtype=np.float64)

    p11 = np.zeros(3, dtype=np.float32)
    p12 = np.zeros(3, dtype=np.float32)
    p21 = np.zeros(3, dtype=np.float32)
    p22 = np.zeros(3, dtype=np.float32)

    vertex1 = np.zeros(3, dtype=np.float32)
    vertex2 = np.zeros(3, dtype=np.float32)

    vertex_count_1 = 0
    vertex_count_2 = 0
    voxel_indices = np.zeros((4, 2), dtype=np.int64)
    edges_1_2 = np.zeros((2, 4), dtype=np.int64)
    for i in range(voxel_number[0] - 1):
        voxel_indices[0, 0] = i
        voxel_indices[1, 0] = i + 1
        voxel_indices[2, 0] = i + 1
        voxel_indices[3, 0] = i
        for j in range(voxel_number[1] - 1):
            voxel_indices[0, 1] = j
            voxel_indices[1, 1] = j
            voxel_indices[2, 1] = j + 1
            voxel_indices[3, 1] = j + 1
            # The 4 corners of the voxel
            corners[0] = grid[i, j]
            corners[1] = grid[i + 1, j]
            corners[2] = grid[i + 1, j + 1]
            corners[3] = grid[i, j + 1]

            # Get the edges of the square
            get_edges(edges_1_2, iso_value, corners)

            for phase in range(2):
                prefactor = 1 if phase == 0 else -1
                for ei in range(2):
                    if edges_1_2[phase, ei * 2] == -1:
                        break
                    c11 = edge_vertex_indices[edges_1_2[phase][ei * 2], 0]
                    c12 = edge_vertex_indices[edges_1_2[phase][ei * 2], 1]
                    c21 = edge_vertex_indices[edges_1_2[phase][ei * 2 + 1], 0]
                    c22 = edge_vertex_indices[edges_1_2[phase][ei * 2 + 1], 1]

                    p11[0] = origin[0] + voxel_indices[c11, 0] * voxel_size[0, 0] + voxel_indices[c11, 1] * voxel_size[1, 0]
                    p11[1] = origin[1] + voxel_indices[c11, 0] * voxel_size[0, 1] + voxel_indices[c11, 1] * voxel_size[1, 1]
                    p11[2] = origin[2] + voxel_indices[c11, 0] * voxel_size[0, 2] + voxel_indices[c11, 1] * voxel_size[1, 2]
                    p12[0] = origin[0] + voxel_indices[c12, 0] * voxel_size[0, 0] + voxel_indices[c12, 1] * voxel_size[1, 0]
                    p12[1] = origin[1] + voxel_indices[c12, 0] * voxel_size[0, 1] + voxel_indices[c12, 1] * voxel_size[1, 1]
                    p12[2] = origin[2] + voxel_indices[c12, 0] * voxel_size[0, 2] + voxel_indices[c12, 1] * voxel_size[1, 2]
                    p21[0] = origin[0] + voxel_indices[c21, 0] * voxel_size[0, 0] + voxel_indices[c21, 1] * voxel_size[1, 0]
                    p21[1] = origin[1] + voxel_indices[c21, 0] * voxel_size[0, 1] + voxel_indices[c21, 1] * voxel_size[1, 1]
                    p21[2] = origin[2] + voxel_indices[c21, 0] * voxel_size[0, 2] + voxel_indices[c21, 1] * voxel_size[1, 2]
                    p22[0] = origin[0] + voxel_indices[c22, 0] * voxel_size[0, 0] + voxel_indices[c22, 1] * voxel_size[1, 0]
                    p22[1] = origin[1] + voxel_indices[c22, 0] * voxel_size[0, 1] + voxel_indices[c22, 1] * voxel_size[1, 1]
                    p22[2] = origin[2] + voxel_indices[c22, 0] * voxel_size[0, 2] + voxel_indices[c22, 1] * voxel_size[1, 2]

                    v11 = corners[c11]
                    v12 = corners[c12]
                    v21 = corners[c21]
                    v22 = corners[c22]

                    t1 = calculate_interpolation_value(iso_value * prefactor, v11, v12)
                    t2 = calculate_interpolation_value(iso_value * prefactor, v21, v22)

                    vertex1[0] = p11[0] + t1 * (p12[0] - p11[0])
                    vertex1[1] = p11[1] + t1 * (p12[1] - p11[1])
                    vertex1[2] = p11[2] + t1 * (p12[2] - p11[2])
                    vertex2[0] = p21[0] + t2 * (p22[0] - p21[0])
                    vertex2[1] = p21[1] + t2 * (p22[1] - p21[1])
                    vertex2[2] = p21[2] + t2 * (p22[2] - p21[2])

                    if phase == 0:
                        lines_1[vertex_count_1, :] = vertex1
                        lines_1[vertex_count_1 + 1, :] = vertex2
                        vertex_count_1 += 2
                    elif phase == 1:
                        lines_2[vertex_count_2, :] = vertex1
                        lines_2[vertex_count_2 + 1, :] = vertex2
                        vertex_count_2 += 2

    lines_1[-1, -1] = <float>(vertex_count_1)
    lines_2[-1, -1] = <float>(vertex_count_2)

@exceptval(check=False)
@boundscheck(False)
@cdivision(True)
cpdef inline double calculate_interpolation_value(
    double iso,
    float v1,
    float v2,
):
    """Calculate the interpolation factor between two corner points.

    :param iso: isovalue
    :param v1: value of the first vertex
    :param v2: value of the second vertex
    """
    if abs(v2 - v1) < 1e-6:
        return 0.5
    return (iso - v1) / (v2 - v1)

@exceptval(check=False)
@boundscheck(False)
@cdivision(True)
cpdef inline void get_edges(
    int64_t[:,:]edges_result,
    double isovalue,
    double[:] voxel_values,
):
    """Get the edges for the voxels if the lie above the surface.

    :param edges_result: edges of the isosurface to be returned
    :param isovalue: value of the isosurface
    :param voxel_values: values of the voxels
    """
    cdef int64_t line_table_index_1 = 0
    cdef int64_t line_table_index_2 = 0
    cdef int64_t i
    cdef double mean

    # same as doing line_table_index_1 + 2**i
    for i in range(4):
        if voxel_values[i] > isovalue:
            line_table_index_1 |= 1 << i
        if voxel_values[i] < -isovalue:
            line_table_index_2 |= 1 << i
    mean = 0.25 * (voxel_values[0] + voxel_values[1] + voxel_values[2] + voxel_values[3])
    if line_table_index_1 == 5:
        if mean < isovalue:
            line_table_index_1 = 10
    if line_table_index_1 == 10:
        if mean < isovalue:
            line_table_index_1 = 5
    if line_table_index_2 == 5:
        if mean > -isovalue:
            line_table_index_2 = 10
    if line_table_index_2 == 10:
        if mean > -isovalue:
            line_table_index_2 = 5
    edges_result[0, :] = line_table[line_table_index_1]
    edges_result[1, :] = line_table[line_table_index_2]


cdef int64_t[:, :] edge_vertex_indices = np.array([
    [0, 1],
    [1, 2],
    [3, 0],
    [2, 3],
], dtype=np.int64
)

cdef int64_t[:, :] line_table = np.array([
    [-1, -1, -1, -1], # case 0: 0000
    [0, 2, -1, -1], # case 1: 0001
    [0, 1, -1, -1], # case 2: 0010
    [1, 2, -1, -1], # case 3: 0011
    [1, 3, -1, -1], # case 4: 0100
    [0, 1, 2, 3], # case 5: 0101
    [0, 3, -1, -1], # case 6: 0110
    [2, 3, -1, -1], # case 7: 0111
    [2, 3, -1, -1], # case 8: 1000
    [0, 3, -1, -1], # case 9: 1001
    [0, 2, 1, 3], # case 10: 1010
    [1, 3, -1, -1], # case 11: 1011
    [1, 2, -1, -1], # case 12: 1100
    [0, 1, -1, -1], # case 13: 1101
    [0, 2, -1, -1], # case 14: 1110
    [-1, -1, -1, -1], # case 15: 1111
], dtype=np.int64
)
