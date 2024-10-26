"""Calculates the isosurface for a given voxel grid."""

from __future__ import annotations

import numpy as np

from molara.eval.trianglelookuptable import edge_vertex_indices, triangle_table


def marching_cubes(
    grid: np.ndarray,
    isovalue: float,
    origin: np.ndarray,
    voxel_size: np.ndarray,
    voxel_number: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate the isosurface for a given voxel grid.

    :param grid: 3D numpy array containing the values of the voxels
    :param isovalue: value of the isosurface
    :param origin: origin of the voxel grids (position of the 0, 0, 0 entry)
    :param voxel_size: size of the voxels in each direction
    :param voxel_number: number of voxels in each direction
    :return: vertices and indices of the isosurface
    """
    x_voxels = voxel_number[0]
    y_voxels = voxel_number[1]
    z_voxels = voxel_number[2]

    verts: list = [[], []]
    for i in range(x_voxels - 1):
        for j in range(y_voxels - 1):
            for k in range(z_voxels - 1):
                # Calculate the 8 indices of the current voxel
                voxel_indices = np.array(
                    [
                        [i, j, k + 1],
                        [i, j, k],
                        [i + 1, j, k],
                        [i + 1, j, k + 1],
                        [i, j + 1, k + 1],
                        [i, j + 1, k],
                        [i + 1, j + 1, k],
                        [i + 1, j + 1, k + 1],
                    ],
                    dtype=np.int32,
                )
                voxel_values = np.zeros(8)
                for corner_index in range(8):
                    voxel_values[corner_index] = grid[
                        voxel_indices[corner_index, 0],
                        voxel_indices[corner_index, 1],
                        voxel_indices[corner_index, 2],
                    ]
                edges_1, edges_2 = get_edges(isovalue, voxel_values)
                edges_1_2 = np.array([edges_1, edges_2])
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
                        vs = np.array(
                            [voxel_size[0, 0], voxel_size[1, 1], voxel_size[2, 2]],
                        )
                        p11 = origin + vs * voxel_indices[c11, :]
                        p12 = origin + vs * voxel_indices[c12, :]
                        p21 = origin + vs * voxel_indices[c21, :]
                        p22 = origin + vs * voxel_indices[c22, :]
                        p31 = origin + vs * voxel_indices[c31, :]
                        p32 = origin + vs * voxel_indices[c32, :]

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

                        vertex1 = list(p11 + t1 * (p12 - p11))
                        vertex2 = list(p21 + t2 * (p22 - p21))
                        vertex3 = list(p31 + t3 * (p32 - p31))

                        n1 = list(
                            -prefactor
                            * calculate_normal_vertex(
                                grid,
                                voxel_indices[c11, :],
                                voxel_indices[c12, :],
                                t1,
                            ),
                        )
                        n2 = list(
                            -prefactor
                            * calculate_normal_vertex(
                                grid,
                                voxel_indices[c21, :],
                                voxel_indices[c22, :],
                                t2,
                            ),
                        )
                        n3 = list(
                            -prefactor
                            * calculate_normal_vertex(
                                grid,
                                voxel_indices[c31, :],
                                voxel_indices[c32, :],
                                t3,
                            ),
                        )
                        verts[phase] += vertex1 + n1 + vertex2 + n2 + vertex3 + n3

    return np.array(verts[0], dtype=np.float32), np.array(verts[1], dtype=np.float32)


def calculate_interpolation_value(
    iso: float,
    v1: float,
    v2: float,
) -> float:
    """Calculate the interpolation factor between two corner points.

    :param iso: isovalue
    :param v1: value of the first vertex
    :param v2: value of the second vertex
    """
    return (iso - v1) / (v2 - v1)


def calculate_normal_corner(
    grid: np.ndarray,
    corner_index: np.ndarray,
) -> np.ndarray:
    """Calculate the normal of a corner of a voxel.

    :param grid: 3D numpy array containing the values of the voxels
    :param corner_index: index of the corner
    :return: normal of the corner
    """
    x = corner_index[0]
    y = corner_index[1]
    z = corner_index[2]
    max_x, max_y, max_z = grid.shape
    x_minus = max(x - 1, 0)
    x_plus = min(x + 1, max_x - 1)
    y_minus = max(y - 1, 0)
    y_plus = min(y + 1, max_y - 1)
    z_minus = max(z - 1, 0)
    z_plus = min(z + 1, max_z - 1)
    dx = grid[x_plus, y, z] - grid[x_minus, y, z]
    dy = grid[x, y_plus, z] - grid[x, y_minus, z]
    dz = grid[x, y, z_plus] - grid[x, y, z_minus]
    return np.array([dx, dy, dz]) / np.linalg.norm(np.array([dx, dy, dz]))


def calculate_normal_vertex(
    grid: np.ndarray,
    corner_index_a: np.ndarray,
    corner_index_b: np.ndarray,
    t1: float,
) -> np.ndarray:
    """Calculate the normal of a vertex. And means it to smooth shade.

    :param grid: 3D numpy array containing the values of the voxels
    :param corner_index_a: index of the first corner
    :param corner_index_b: index of the second corner
    :param t1: interpolation factor
    :return: normal of the vertex
    """
    n1 = calculate_normal_corner(grid, corner_index_a)
    n2 = calculate_normal_corner(grid, corner_index_b)
    n = n1 + t1 * (n2 - n1)
    return n / np.linalg.norm(n)


def get_edges(
    isovalue: float,
    voxel_values: np.ndarray,
) -> tuple[list, list]:
    """Calculate the isosurface for a given voxel grid.

    :param isovalue: value of the isosurface
    :param voxel_values: values of the voxels
    :param phase: phase of the orbital
    :return: vertices and indices of the isosurface
    """
    triangle_table_index_1 = 0
    triangle_table_index_2 = 0
    for i in range(8):
        if voxel_values[i] > isovalue:
            # same as doing triangle_table_index_1 + 2**i
            triangle_table_index_1 |= 1 << i
        if voxel_values[i] < -isovalue:
            triangle_table_index_2 |= 1 << i
    return (
        triangle_table[triangle_table_index_1],
        triangle_table[triangle_table_index_2],
    )
