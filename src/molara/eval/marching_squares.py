"""Contain the class for the marching squares algorithm."""

import numpy as np

# Numbering of the corners of the grid and the edges:

# 3---------2    -----3-----
# |         |    |         |
# |         |    2         1
# |         |    |         |
# 0---------1    -----0-----



edge_vertex_indices = np.array([
    [0, 1],
    [1, 2],
    [3, 0],
    [2, 3],
])

line_table = np.array([
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
])

def marching_squares(grid,
                     iso_value,
                     origin,
                     voxel_size,
                     voxel_number,
                     lines_1,
                     lines_2,
                     ) -> int:
    """Perform the marching squares algorithm on a 2D grid.

    :param grid: 2D array representing the grid
    :param iso_value: The isoline value
    """
    corners = np.zeros(4)
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

                    p11 = origin + voxel_indices[c11, 0] * voxel_size[0] + voxel_indices[c11, 1] * voxel_size[1]
                    p12 = origin + voxel_indices[c12, 0] * voxel_size[0] + voxel_indices[c12, 1] * voxel_size[1]
                    p21 = origin + voxel_indices[c21, 0] * voxel_size[0] + voxel_indices[c21, 1] * voxel_size[1]
                    p22 = origin + voxel_indices[c22, 0] * voxel_size[0] + voxel_indices[c22, 1] * voxel_size[1]

                    v11 = corners[c11]
                    v12 = corners[c12]
                    v21 = corners[c21]
                    v22 = corners[c22]

                    t1 = calculate_interpolation_value(iso_value * prefactor, v11, v12)
                    t2 = calculate_interpolation_value(iso_value * prefactor, v21, v22)

                    vertex1 = p11 + t1 * (p12 - p11)
                    vertex2 = p21 + t2 * (p22 - p21)

                    if phase == 0:
                        lines_1[vertex_count_1, :] = vertex1
                        lines_1[vertex_count_1 + 1, :] = vertex2
                        vertex_count_1 += 2
                    elif phase == 1:
                        lines_2[vertex_count_2, :] = vertex1
                        lines_2[vertex_count_2 + 1, :] = vertex2
                        vertex_count_2 += 2

    lines_1[-1, -1] = float(vertex_count_1)
    lines_2[-1, -1] = float(vertex_count_2)
    return 0

def  calculate_interpolation_value(
    iso,
    v1,
    v2,
):
    """Calculate the interpolation factor between two corner points.

    :param iso: isovalue
    :param v1: value of the first vertex
    :param v2: value of the second vertex
    """
    if np.abs(v2 - v1) < 1e-6:
        return 0.5
    return (iso - v1) / (v2 - v1)


def get_edges(
    edges_result,
    isovalue,
    voxel_values,
):
    """Get the edges for the voxels if the lie above the surface.

    :param edges_result: edges of the isosurface to be returned
    :param isovalue: value of the isosurface
    :param voxel_values: values of the voxels
    :param phase: phase of the orbital
    :return: vertices and indices of the isosurface
    """
    line_table_index_1 = int(0)
    line_table_index_2 = int(0)
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

