"""Calculates the isosurface for a given voxel grid."""

from __future__ import annotations

import numpy as np
from libc.stdint cimport int64_t
from libc.math cimport sqrt
from cython import boundscheck, exceptval, cdivision

@exceptval(check=False)
@boundscheck(False)
@cdivision(True)
cpdef int marching_cubes(
    double[:, :, :] grid,
    double isovalue,
    double[:] origin,
    double[:] voxel_size,
    int64_t[:] voxel_number,
    float[:] vertices_1,
    float[:] vertices_2,
):
    """Calculate the isosurface for a given voxel grid.

    :param grid: 3D numpy array containing the values of the voxels
    :param isovalue: value of the isosurface
    :param origin: origin of the voxel grids (position of the 0, 0, 0 entry)
    :param voxel_size: size of the voxels in each direction
    :param voxel_number: number of voxels in each direction
    :param vertices_1: vertices of the isosurface to be returned. The last entry is the number of vertices
    :param vertices_2: vertices of the isosurface of the other phase to be returned. The number of vertices is saved
    :return: vertices and indices of the isosurface
    """
    cdef int64_t x_voxels, y_voxels, z_voxels, phase, prefactor, ei, vertices_count_1
    cdef int64_t vertices_count_2, c11, c12, c21, c22, c31, c32
    cdef int i, j, k
    cdef double[:] voxel_values
    cdef float[:] p11, p12, p21, p22, p31, p32, vertex1, vertex2, vertex3, n1, n2, n3, n_corner_1, n_corner_2
    cdef float v11, v12, v21, v22, v31, v32, t1, t2, t3
    cdef int64_t[:, :] edges_1_2, voxel_indices

    x_voxels = voxel_number[0]
    y_voxels = voxel_number[1]
    z_voxels = voxel_number[2]

    p11 = np.zeros(3, dtype=np.float32)
    p12 = np.zeros(3, dtype=np.float32)
    p21 = np.zeros(3, dtype=np.float32)
    p22 = np.zeros(3, dtype=np.float32)
    p31 = np.zeros(3, dtype=np.float32)
    p32 = np.zeros(3, dtype=np.float32)

    vertex1 = np.zeros(3, dtype=np.float32)
    vertex2 = np.zeros(3, dtype=np.float32)
    vertex3 = np.zeros(3, dtype=np.float32)
    n1 = np.zeros(3, dtype=np.float32)
    n2 = np.zeros(3, dtype=np.float32)
    n3 = np.zeros(3, dtype=np.float32)
    n_corner_1 = np.zeros(3, dtype=np.float32)
    n_corner_2 = np.zeros(3, dtype=np.float32)

    voxel_indices = np.zeros((8, 3), dtype=np.int64)
    voxel_values = np.zeros(8, dtype=np.float64)

    edges_1_2 = np.zeros((2, 16), dtype=np.int64)

    vertices_count_1 = 0
    vertices_count_2 = 0

    for i in range(x_voxels - 1):
        # Calculate the 8 indices of the current voxel
        voxel_indices[0, 0] = i
        voxel_indices[1, 0] = i
        voxel_indices[2, 0] = i + 1
        voxel_indices[3, 0] = i + 1
        voxel_indices[4, 0] = i
        voxel_indices[5, 0] = i
        voxel_indices[6, 0] = i + 1
        voxel_indices[7, 0] = i + 1

        for j in range(y_voxels - 1):
            # Calculate the 8 indices of the current voxel
            voxel_indices[0, 1] = j
            voxel_indices[1, 1] = j
            voxel_indices[2, 1] = j
            voxel_indices[3, 1] = j
            voxel_indices[4, 1] = j + 1
            voxel_indices[5, 1] = j + 1
            voxel_indices[6, 1] = j + 1
            voxel_indices[7, 1] = j + 1

            for k in range(z_voxels - 1):
                # Calculate the 8 indices of the current voxel
                voxel_indices[0, 2] = k + 1
                voxel_indices[1, 2] = k
                voxel_indices[2, 2] = k
                voxel_indices[3, 2] = k + 1
                voxel_indices[4, 2] = k + 1
                voxel_indices[5, 2] = k
                voxel_indices[6, 2] = k
                voxel_indices[7, 2] = k + 1

                # Calculate the 8 indices of the current voxel
                voxel_values[0] = grid[i, j, k + 1]
                voxel_values[1] = grid[i, j, k]
                voxel_values[2] = grid[i + 1, j, k]
                voxel_values[3] = grid[i + 1, j, k + 1]
                voxel_values[4] = grid[i, j + 1, k + 1]
                voxel_values[5] = grid[i, j + 1, k]
                voxel_values[6] = grid[i + 1, j + 1, k]
                voxel_values[7] = grid[i + 1, j + 1, k + 1]
                get_edges(edges_1_2, isovalue, voxel_values)
                for phase in range(2):
                    prefactor = 1 if phase == 0 else -1
                    for ei in range(5):
                        if edges_1_2[phase, ei * 3] == -1:
                            break
                        c11 = edge_vertex_indices[edges_1_2[phase][ei * 3], 0]
                        c12 = edge_vertex_indices[edges_1_2[phase][ei * 3], 1]
                        c21 = edge_vertex_indices[edges_1_2[phase][ei * 3 + 1], 0]
                        c22 = edge_vertex_indices[edges_1_2[phase][ei * 3 + 1], 1]
                        c31 = edge_vertex_indices[edges_1_2[phase][ei * 3 + 2], 0]
                        c32 = edge_vertex_indices[edges_1_2[phase][ei * 3 + 2], 1]

                        # unrolling loop: calulcation of the 3D coordinates of the vertices
                        p11[0] = origin[0] + voxel_size[0] * voxel_indices[c11, 0]
                        p11[1] = origin[1] + voxel_size[1] * voxel_indices[c11, 1]
                        p11[2] = origin[2] + voxel_size[2] * voxel_indices[c11, 2]
                        p12[0] = origin[0] + voxel_size[0] * voxel_indices[c12, 0]
                        p12[1] = origin[1] + voxel_size[1] * voxel_indices[c12, 1]
                        p12[2] = origin[2] + voxel_size[2] * voxel_indices[c12, 2]
                        p21[0] = origin[0] + voxel_size[0] * voxel_indices[c21, 0]
                        p21[1] = origin[1] + voxel_size[1] * voxel_indices[c21, 1]
                        p21[2] = origin[2] + voxel_size[2] * voxel_indices[c21, 2]
                        p22[0] = origin[0] + voxel_size[0] * voxel_indices[c22, 0]
                        p22[1] = origin[1] + voxel_size[1] * voxel_indices[c22, 1]
                        p22[2] = origin[2] + voxel_size[2] * voxel_indices[c22, 2]
                        p31[0] = origin[0] + voxel_size[0] * voxel_indices[c31, 0]
                        p31[1] = origin[1] + voxel_size[1] * voxel_indices[c31, 1]
                        p31[2] = origin[2] + voxel_size[2] * voxel_indices[c31, 2]
                        p32[0] = origin[0] + voxel_size[0] * voxel_indices[c32, 0]
                        p32[1] = origin[1] + voxel_size[1] * voxel_indices[c32, 1]
                        p32[2] = origin[2] + voxel_size[2] * voxel_indices[c32, 2]

                        v11 = voxel_values[c11]
                        v12 = voxel_values[c12]
                        v21 = voxel_values[c21]
                        v22 = voxel_values[c22]
                        v31 = voxel_values[c31]
                        v32 = voxel_values[c32]

                        t1 = calculate_interpolation_value(
                            isovalue * prefactor,
                            v11,
                            v12,
                        )
                        t2 = calculate_interpolation_value(
                            isovalue * prefactor,
                            v21,
                            v22,
                        )
                        t3 = calculate_interpolation_value(
                            isovalue * prefactor,
                            v31,
                            v32,
                        )

                        # Get normals
                        calculate_normal_vertex(
                            n1,
                            n_corner_1,
                            n_corner_2,
                            grid,
                            voxel_indices[c11, :],
                            voxel_indices[c12, :],
                            t1,
                            )
                        calculate_normal_vertex(
                            n2,
                            n_corner_1,
                            n_corner_2,
                            grid,
                            voxel_indices[c21, :],
                            voxel_indices[c22, :],
                            t2,
                            )
                        calculate_normal_vertex(
                            n3,
                            n_corner_1,
                            n_corner_2,
                            grid,
                            voxel_indices[c31, :],
                            voxel_indices[c32, :],
                            t3,
                            )

                        # Get vertices (unrolled loop)
                        vertex1[0] = p11[0] + t1 * (p12[0] - p11[0])
                        vertex1[1] = p11[1] + t1 * (p12[1] - p11[1])
                        vertex1[2] = p11[2] + t1 * (p12[2] - p11[2])
                        vertex2[0] = p21[0] + t2 * (p22[0] - p21[0])
                        vertex2[1] = p21[1] + t2 * (p22[1] - p21[1])
                        vertex2[2] = p21[2] + t2 * (p22[2] - p21[2])
                        vertex3[0] = p31[0] + t3 * (p32[0] - p31[0])
                        vertex3[1] = p31[1] + t3 * (p32[1] - p31[1])
                        vertex3[2] = p31[2] + t3 * (p32[2] - p31[2])

                        # get the normals (unrolled loop)
                        n1[0] = -prefactor * n1[0]
                        n1[1] = -prefactor * n1[1]
                        n1[2] = -prefactor * n1[2]
                        n2[0] = -prefactor * n2[0]
                        n2[1] = -prefactor * n2[1]
                        n2[2] = -prefactor * n2[2]
                        n3[0] = -prefactor * n3[0]
                        n3[1] = -prefactor * n3[1]
                        n3[2] = -prefactor * n3[2]

                        if phase == 0:
                            vertices_1[vertices_count_1:vertices_count_1 + 3] = vertex1
                            vertices_count_1 += 3
                            vertices_1[vertices_count_1:vertices_count_1 + 3] = n1
                            vertices_count_1 += 3
                            vertices_1[vertices_count_1:vertices_count_1 + 3] = vertex2
                            vertices_count_1 += 3
                            vertices_1[vertices_count_1:vertices_count_1 + 3] = n2
                            vertices_count_1 += 3
                            vertices_1[vertices_count_1:vertices_count_1 + 3] = vertex3
                            vertices_count_1 += 3
                            vertices_1[vertices_count_1:vertices_count_1 + 3] = n3
                            vertices_count_1 += 3
                        else:
                            vertices_2[vertices_count_2:vertices_count_2 + 3] = vertex1
                            vertices_count_2 += 3
                            vertices_2[vertices_count_2:vertices_count_2 + 3] = n1
                            vertices_count_2 += 3
                            vertices_2[vertices_count_2:vertices_count_2 + 3] = vertex2
                            vertices_count_2 += 3
                            vertices_2[vertices_count_2:vertices_count_2 + 3] = n2
                            vertices_count_2 += 3
                            vertices_2[vertices_count_2:vertices_count_2 + 3] = vertex3
                            vertices_count_2 += 3
                            vertices_2[vertices_count_2:vertices_count_2 + 3] = n3
                            vertices_count_2 += 3

    vertices_1[-1] = <float>vertices_count_1
    vertices_2[-1] = <float>vertices_count_2

    return 0

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
    return (iso - v1) / (v2 - v1)


cpdef inline void calculate_normal_corner(
    float[:] n,
    double[:, :, :]grid,
    int64_t[:] corner_index,
):
    """Calculate the normal of a corner of a voxel.

    :param n: normal of the corner to be returned
    :param grid: 3D numpy array containing the values of the voxels
    :param corner_index: index of the corner
    :return: normal of the corner
    """
    cdef int64_t x, y, z, max_x, max_y, max_z, x_minus, x_plus, y_minus, y_plus, z_minus, z_plus
    cdef float dx, dy, dz, norm_of_result


    x = corner_index[0]
    y = corner_index[1]
    z = corner_index[2]
    max_x = grid.shape[0]
    max_y = grid.shape[1]
    max_z = grid.shape[2]
    x_minus = max(x - 1, 0)
    x_plus = min(x + 1, max_x - 1)
    y_minus = max(y - 1, 0)
    y_plus = min(y + 1, max_y - 1)
    z_minus = max(z - 1, 0)
    z_plus = min(z + 1, max_z - 1)
    dx = grid[x_plus, y, z] - grid[x_minus, y, z]
    dy = grid[x, y_plus, z] - grid[x, y_minus, z]
    dz = grid[x, y, z_plus] - grid[x, y, z_minus]
    norm_of_result = sqrt(dx * dx + dy * dy + dz * dz)
    n[0] = dx / norm_of_result
    n[1] = dy / norm_of_result
    n[2] = dz / norm_of_result


cpdef void calculate_normal_vertex(
    float[:] n,
    float[:] n1,
    float[:] n2,
    double[:, :, :] grid,
    int64_t[:] corner_index_a,
    int64_t[:] corner_index_b,
    double t1,
):
    """Calculate the normal of a vertex. And means it to smooth shade.

    :param n: normal of the vertex to be returned
    :param n_corner_1: normal of the first corner already initialized for speed up
    :param n_corner_2: normal of the second corner already initialized for speed up
    :param grid: 3D numpy array containing the values of the voxels
    :param corner_index_a: index of the first corner
    :param corner_index_b: index of the second corner
    :param t1: interpolation factor
    :return: normal of the vertex
    """
    cdef float norm_of_n

    calculate_normal_corner(n1, grid, corner_index_a)
    calculate_normal_corner(n2, grid, corner_index_b)
    n[0] = n1[0] + t1 * (n2[0] - n1[0])
    n[1] = n1[1] + t1 * (n2[1] - n1[1])
    n[2] = n1[2] + t1 * (n2[2] - n1[2])
    norm_of_n = sqrt(n[0] * n[0] + n[1] * n[1] + n[2] * n[2])
    n[0] /= norm_of_n
    n[1] /= norm_of_n
    n[2] /= norm_of_n


cpdef void get_edges(
    int64_t[:, :] edges_result,
    double isovalue,
    double[:] voxel_values,
):
    """Get the edges for the voxels if the lie above the surface.

    :param edges_result: edges of the isosurface to be returned
    :param isovalue: value of the isosurface
    :param voxel_values: values of the voxels
    :param phase: phase of the orbital
    :return: vertices and indices of the isosurface
    """
    cdef int64_t triangle_table_index_1 = 0
    cdef int64_t triangle_table_index_2 = 0
    cdef int i

    # same as doing triangle_table_index_1 + 2**i
    for i in range(8):
        if voxel_values[i] > isovalue:
            triangle_table_index_1 |= 1 << i
        if voxel_values[i] < -isovalue:
            triangle_table_index_2 |= 1 << i
    edges_result[0, :] = triangle_table[triangle_table_index_1]
    edges_result[1, :] = triangle_table[triangle_table_index_2]


# Source: https://gist.github.com/dwilliamson/c041e3454a713e58baf6e4f8e5fffecd
#
# Lookup Tables for Marching Cubes
#
# These tables differ from the original paper (Marching Cubes: A High Resolution 3D Surface Construction Algorithm)
#
# The coordinate system has the more convenient properties:
#
#    i = cube index [0, 7]
#    x = (i & 1) >> 0
#    y = (i & 2) >> 1
#    z = (i & 4) >> 2
#
# Axes are:
#
#             y
#             |
#             |
#             |
#      z------+
#            /
#          /
#        x
# Vertex and edge layout:
#
#            4             5
#            +-------------+               +-----4-------+
#          / |           / |             / |            /|
#        /   |         /   |          7    8         5   9
#    7 +-----+-------+  6  |         +------6------+     |
#      |   0 +-------+-----+ 1       |     +-----0-+-----+
#      |   /         |   /          11   3         10  1
#      | /           | /             | /           | /
#    3 +-------------+ 2             +------2------+
#
# Triangulation cases are generated prioritising rotations over inversions, which can introduce non-manifold geometry.


# Pair of vertex indices for each edge on the cube
cdef int64_t[:, :]  edge_vertex_indices = np.array(
    [
        [1, 0],
        [1, 2],
        [2, 3],
        [0, 3],
        [5, 4],
        [5, 6],
        [6, 7],
        [4, 7],
        [0, 4],
        [1, 5],
        [2, 6],
        [3, 7],
    ], dtype=np.int64
)

# For each MC case, a list of triangles, specified as triples of edge indices, terminated by -1
cdef int64_t[:, :] triangle_table = np.array([
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 8, 3, 9, 8, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 2, 10, 0, 2, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 8, 3, 2, 10, 8, 10, 9, 8, -1, -1, -1, -1, -1, -1, -1],
    [3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 11, 2, 8, 11, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 9, 0, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 11, 2, 1, 9, 11, 9, 8, 11, -1, -1, -1, -1, -1, -1, -1],
    [3, 10, 1, 11, 10, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 10, 1, 0, 8, 10, 8, 11, 10, -1, -1, -1, -1, -1, -1, -1],
    [3, 9, 0, 3, 11, 9, 11, 10, 9, -1, -1, -1, -1, -1, -1, -1],
    [9, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 3, 0, 7, 3, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 9, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 1, 9, 4, 7, 1, 7, 3, 1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 4, 7, 3, 0, 4, 1, 2, 10, -1, -1, -1, -1, -1, -1, -1],
    [9, 2, 10, 9, 0, 2, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
    [2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4, -1, -1, -1, -1],
    [8, 4, 7, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [11, 4, 7, 11, 2, 4, 2, 0, 4, -1, -1, -1, -1, -1, -1, -1],
    [9, 0, 1, 8, 4, 7, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
    [4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1, -1, -1, -1, -1],
    [3, 10, 1, 3, 11, 10, 7, 8, 4, -1, -1, -1, -1, -1, -1, -1],
    [1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4, -1, -1, -1, -1],
    [4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3, -1, -1, -1, -1],
    [4, 7, 11, 4, 11, 9, 9, 11, 10, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 4, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 5, 4, 1, 5, 0, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [8, 5, 4, 8, 3, 5, 3, 1, 5, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 8, 1, 2, 10, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
    [5, 2, 10, 5, 4, 2, 4, 0, 2, -1, -1, -1, -1, -1, -1, -1],
    [2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8, -1, -1, -1, -1],
    [9, 5, 4, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 11, 2, 0, 8, 11, 4, 9, 5, -1, -1, -1, -1, -1, -1, -1],
    [0, 5, 4, 0, 1, 5, 2, 3, 11, -1, -1, -1, -1, -1, -1, -1],
    [2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5, -1, -1, -1, -1],
    [10, 3, 11, 10, 1, 3, 9, 5, 4, -1, -1, -1, -1, -1, -1, -1],
    [4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10, -1, -1, -1, -1],
    [5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3, -1, -1, -1, -1],
    [5, 4, 8, 5, 8, 10, 10, 8, 11, -1, -1, -1, -1, -1, -1, -1],
    [9, 7, 8, 5, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 3, 0, 9, 5, 3, 5, 7, 3, -1, -1, -1, -1, -1, -1, -1],
    [0, 7, 8, 0, 1, 7, 1, 5, 7, -1, -1, -1, -1, -1, -1, -1],
    [1, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 7, 8, 9, 5, 7, 10, 1, 2, -1, -1, -1, -1, -1, -1, -1],
    [10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3, -1, -1, -1, -1],
    [8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2, -1, -1, -1, -1],
    [2, 10, 5, 2, 5, 3, 3, 5, 7, -1, -1, -1, -1, -1, -1, -1],
    [7, 9, 5, 7, 8, 9, 3, 11, 2, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11, -1, -1, -1, -1],
    [2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7, -1, -1, -1, -1],
    [11, 2, 1, 11, 1, 7, 7, 1, 5, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11, -1, -1, -1, -1],
    [5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0, -1],
    [11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0, -1],
    [11, 10, 5, 7, 11, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 0, 1, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 8, 3, 1, 9, 8, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
    [1, 6, 5, 2, 6, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 6, 5, 1, 2, 6, 3, 0, 8, -1, -1, -1, -1, -1, -1, -1],
    [9, 6, 5, 9, 0, 6, 0, 2, 6, -1, -1, -1, -1, -1, -1, -1],
    [5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8, -1, -1, -1, -1],
    [2, 3, 11, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [11, 0, 8, 11, 2, 0, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 9, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1, -1, -1, -1],
    [5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11, -1, -1, -1, -1],
    [6, 3, 11, 6, 5, 3, 5, 1, 3, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6, -1, -1, -1, -1],
    [3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9, -1, -1, -1, -1],
    [6, 5, 9, 6, 9, 11, 11, 9, 8, -1, -1, -1, -1, -1, -1, -1],
    [5, 10, 6, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 3, 0, 4, 7, 3, 6, 5, 10, -1, -1, -1, -1, -1, -1, -1],
    [1, 9, 0, 5, 10, 6, 8, 4, 7, -1, -1, -1, -1, -1, -1, -1],
    [10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4, -1, -1, -1, -1],
    [6, 1, 2, 6, 5, 1, 4, 7, 8, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7, -1, -1, -1, -1],
    [8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6, -1, -1, -1, -1],
    [7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9, -1],
    [3, 11, 2, 7, 8, 4, 10, 6, 5, -1, -1, -1, -1, -1, -1, -1],
    [5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11, -1, -1, -1, -1],
    [0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6, -1, -1, -1, -1],
    [9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6, -1],
    [8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6, -1, -1, -1, -1],
    [5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, -1],
    [0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7, -1],
    [6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9, -1, -1, -1, -1],
    [10, 4, 9, 6, 4, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 10, 6, 4, 9, 10, 0, 8, 3, -1, -1, -1, -1, -1, -1, -1],
    [10, 0, 1, 10, 6, 0, 6, 4, 0, -1, -1, -1, -1, -1, -1, -1],
    [8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10, -1, -1, -1, -1],
    [1, 4, 9, 1, 2, 4, 2, 6, 4, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4, -1, -1, -1, -1],
    [0, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [8, 3, 2, 8, 2, 4, 4, 2, 6, -1, -1, -1, -1, -1, -1, -1],
    [10, 4, 9, 10, 6, 4, 11, 2, 3, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6, -1, -1, -1, -1],
    [3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10, -1, -1, -1, -1],
    [6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1, -1],
    [9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3, -1, -1, -1, -1],
    [8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1, -1],
    [3, 11, 6, 3, 6, 0, 0, 6, 4, -1, -1, -1, -1, -1, -1, -1],
    [6, 4, 8, 11, 6, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [7, 10, 6, 7, 8, 10, 8, 9, 10, -1, -1, -1, -1, -1, -1, -1],
    [0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10, -1, -1, -1, -1],
    [10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0, -1, -1, -1, -1],
    [10, 6, 7, 10, 7, 1, 1, 7, 3, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7, -1, -1, -1, -1],
    [2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9, -1],
    [7, 8, 0, 7, 0, 6, 6, 0, 2, -1, -1, -1, -1, -1, -1, -1],
    [7, 3, 2, 6, 7, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7, -1, -1, -1, -1],
    [2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7, -1],
    [1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11, -1],
    [11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1, -1, -1, -1, -1],
    [8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6, -1],
    [0, 9, 1, 11, 6, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0, -1, -1, -1, -1],
    [7, 11, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 8, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 9, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [8, 1, 9, 8, 3, 1, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
    [10, 1, 2, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 3, 0, 8, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
    [2, 9, 0, 2, 10, 9, 6, 11, 7, -1, -1, -1, -1, -1, -1, -1],
    [6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8, -1, -1, -1, -1],
    [7, 2, 3, 6, 2, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [7, 0, 8, 7, 6, 0, 6, 2, 0, -1, -1, -1, -1, -1, -1, -1],
    [2, 7, 6, 2, 3, 7, 0, 1, 9, -1, -1, -1, -1, -1, -1, -1],
    [1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6, -1, -1, -1, -1],
    [10, 7, 6, 10, 1, 7, 1, 3, 7, -1, -1, -1, -1, -1, -1, -1],
    [10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8, -1, -1, -1, -1],
    [0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7, -1, -1, -1, -1],
    [7, 6, 10, 7, 10, 8, 8, 10, 9, -1, -1, -1, -1, -1, -1, -1],
    [6, 8, 4, 11, 8, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 6, 11, 3, 0, 6, 0, 4, 6, -1, -1, -1, -1, -1, -1, -1],
    [8, 6, 11, 8, 4, 6, 9, 0, 1, -1, -1, -1, -1, -1, -1, -1],
    [9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6, -1, -1, -1, -1],
    [6, 8, 4, 6, 11, 8, 2, 10, 1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6, -1, -1, -1, -1],
    [4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9, -1, -1, -1, -1],
    [10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3, -1],
    [8, 2, 3, 8, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1],
    [0, 4, 2, 4, 6, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8, -1, -1, -1, -1],
    [1, 9, 4, 1, 4, 2, 2, 4, 6, -1, -1, -1, -1, -1, -1, -1],
    [8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1, -1, -1, -1, -1],
    [10, 1, 0, 10, 0, 6, 6, 0, 4, -1, -1, -1, -1, -1, -1, -1],
    [4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3, -1],
    [10, 9, 4, 6, 10, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 9, 5, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 4, 9, 5, 11, 7, 6, -1, -1, -1, -1, -1, -1, -1],
    [5, 0, 1, 5, 4, 0, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
    [11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5, -1, -1, -1, -1],
    [9, 5, 4, 10, 1, 2, 7, 6, 11, -1, -1, -1, -1, -1, -1, -1],
    [6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5, -1, -1, -1, -1],
    [7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2, -1, -1, -1, -1],
    [3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6, -1],
    [7, 2, 3, 7, 6, 2, 5, 4, 9, -1, -1, -1, -1, -1, -1, -1],
    [9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7, -1, -1, -1, -1],
    [3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0, -1, -1, -1, -1],
    [6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8, -1],
    [9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7, -1, -1, -1, -1],
    [1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4, -1],
    [4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, -1],
    [7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10, -1, -1, -1, -1],
    [6, 9, 5, 6, 11, 9, 11, 8, 9, -1, -1, -1, -1, -1, -1, -1],
    [3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5, -1, -1, -1, -1],
    [0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11, -1, -1, -1, -1],
    [6, 11, 3, 6, 3, 5, 5, 3, 1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6, -1, -1, -1, -1],
    [0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10, -1],
    [11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5, -1],
    [6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3, -1, -1, -1, -1],
    [5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2, -1, -1, -1, -1],
    [9, 5, 6, 9, 6, 0, 0, 6, 2, -1, -1, -1, -1, -1, -1, -1],
    [1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8, -1],
    [1, 5, 6, 2, 1, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6, -1],
    [10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0, -1, -1, -1, -1],
    [0, 3, 8, 5, 6, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [10, 5, 6, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [11, 5, 10, 7, 5, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [11, 5, 10, 11, 7, 5, 8, 3, 0, -1, -1, -1, -1, -1, -1, -1],
    [5, 11, 7, 5, 10, 11, 1, 9, 0, -1, -1, -1, -1, -1, -1, -1],
    [10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1, -1, -1, -1, -1],
    [11, 1, 2, 11, 7, 1, 7, 5, 1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11, -1, -1, -1, -1],
    [9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7, -1, -1, -1, -1],
    [7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2, -1],
    [2, 5, 10, 2, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1],
    [8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5, -1, -1, -1, -1],
    [9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2, -1, -1, -1, -1],
    [9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2, -1],
    [1, 3, 5, 3, 7, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 7, 0, 7, 1, 1, 7, 5, -1, -1, -1, -1, -1, -1, -1],
    [9, 0, 3, 9, 3, 5, 5, 3, 7, -1, -1, -1, -1, -1, -1, -1],
    [9, 8, 7, 5, 9, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [5, 8, 4, 5, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1],
    [5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0, -1, -1, -1, -1],
    [0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5, -1, -1, -1, -1],
    [10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4, -1],
    [2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8, -1, -1, -1, -1],
    [0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, -1],
    [0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5, -1],
    [9, 4, 5, 2, 11, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4, -1, -1, -1, -1],
    [5, 10, 2, 5, 2, 4, 4, 2, 0, -1, -1, -1, -1, -1, -1, -1],
    [3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9, -1],
    [5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2, -1, -1, -1, -1],
    [8, 4, 5, 8, 5, 3, 3, 5, 1, -1, -1, -1, -1, -1, -1, -1],
    [0, 4, 5, 1, 0, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5, -1, -1, -1, -1],
    [9, 4, 5, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 11, 7, 4, 9, 11, 9, 10, 11, -1, -1, -1, -1, -1, -1, -1],
    [0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11, -1, -1, -1, -1],
    [1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11, -1, -1, -1, -1],
    [3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4, -1],
    [4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2, -1, -1, -1, -1],
    [9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3, -1],
    [11, 7, 4, 11, 4, 2, 2, 4, 0, -1, -1, -1, -1, -1, -1, -1],
    [11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4, -1, -1, -1, -1],
    [2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9, -1, -1, -1, -1],
    [9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7, -1],
    [3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, -1],
    [1, 10, 2, 8, 7, 4, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 9, 1, 4, 1, 7, 7, 1, 3, -1, -1, -1, -1, -1, -1, -1],
    [4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1, -1, -1, -1, -1],
    [4, 0, 3, 7, 4, 3, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [4, 8, 7, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [9, 10, 8, 10, 11, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 9, 3, 9, 11, 11, 9, 10, -1, -1, -1, -1, -1, -1, -1],
    [0, 1, 10, 0, 10, 8, 8, 10, 11, -1, -1, -1, -1, -1, -1, -1],
    [3, 1, 10, 11, 3, 10, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 2, 11, 1, 11, 9, 9, 11, 8, -1, -1, -1, -1, -1, -1, -1],
    [3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9, -1, -1, -1, -1],
    [0, 2, 11, 8, 0, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [3, 2, 11, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 3, 8, 2, 8, 10, 10, 8, 9, -1, -1, -1, -1, -1, -1, -1],
    [9, 10, 2, 0, 9, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8, -1, -1, -1, -1],
    [1, 10, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [1, 3, 8, 9, 1, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 9, 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [0, 3, 8, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
], dtype=np.int64)
