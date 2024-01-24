"""Calculates the isosurface for a given voxel grid."""

import numpy as np
from molara.Eval.trianglelookuptable import triangle_table, edge_vertex_indices


def marching_cubes(
    grid: np.ndarray,
    isovalue: float,
    origin: np.ndarray,
    voxel_size: np.ndarray,
    voxel_number: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculates the isosurface for a given voxel grid.

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
    verts1 = []
    verts2 = []
    temp = []
    for i in range(x_voxels - 1):
        for j in range(y_voxels - 1):
            for k in range(z_voxels - 1):
                # Calculate the 8 indices of the current voxel
                voxel_indices = np.array(
                    [
                        [i, j + 1, k + 1],
                        [i, j, k + 1],
                        [i + 1, j, k + 1],
                        [i + 1, j + 1, k + 1],
                        [i, j + 1, k],
                        [i, j, k],
                        [i + 1, j, k],
                        [i + 1, j + 1, k],
                    ],
                    dtype=np.uint32,
                )
                voxel_values = np.zeros(8)
                for corner_index in range(8):
                    voxel_values[corner_index] = grid[
                        voxel_indices[corner_index, 0], voxel_indices[corner_index, 1], voxel_indices[corner_index, 2]
                    ]
                edges = get_edges(isovalue, voxel_values, phase=1)
                for ei in range(5):
                    if edges[ei * 3] == -1:
                        break
                    else:
                        c11 = edge_vertex_indices[edges[ei * 3], 0]
                        c12 = edge_vertex_indices[edges[ei * 3], 1]
                        c21 = edge_vertex_indices[edges[ei * 3 + 1], 0]
                        c22 = edge_vertex_indices[edges[ei * 3 + 1], 1]
                        c31 = edge_vertex_indices[edges[ei * 3 + 2], 0]
                        c32 = edge_vertex_indices[edges[ei * 3 + 2], 1]
                        vs = np.array(
                            [voxel_size[0, 0], voxel_size[1, 1], voxel_size[2, 2]]
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

                        vertex1 = list(
                            get_interpolated_edge_position(
                                p11, p12, isovalue, float(v11), float(v12)
                            )
                        )
                        vertex2 = list(
                            get_interpolated_edge_position(
                                p21, p22, isovalue, float(v21), float(v22)
                            )
                        )
                        vertex3 = list(
                            get_interpolated_edge_position(
                                p31, p32, isovalue, float(v31), float(v32)
                            )
                        )
                        n = np.cross(
                            np.array(vertex2) - np.array(vertex1),
                            np.array(vertex3) - np.array(vertex1),
                        )
                        n = list(n / np.linalg.norm(n))
                        verts1 += vertex1 + n + vertex2 + n + vertex3 + n
                edges = get_edges(isovalue, voxel_values, phase=-1)
                for ei in range(5):
                    if edges[ei * 3] == -1:
                        break
                    else:
                        c11 = edge_vertex_indices[edges[ei * 3], 0]
                        c12 = edge_vertex_indices[edges[ei * 3], 1]
                        c21 = edge_vertex_indices[edges[ei * 3 + 1], 0]
                        c22 = edge_vertex_indices[edges[ei * 3 + 1], 1]
                        c31 = edge_vertex_indices[edges[ei * 3 + 2], 0]
                        c32 = edge_vertex_indices[edges[ei * 3 + 2], 1]
                        vs = np.array(
                            [voxel_size[0, 0], voxel_size[1, 1], voxel_size[2, 2]]
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

                        vertex1 = list(
                            get_interpolated_edge_position(
                                p11, p12, -isovalue, float(v11), float(v12)
                            )
                        )
                        vertex2 = list(
                            get_interpolated_edge_position(
                                p21, p22, -isovalue, float(v21), float(v22)
                            )
                        )
                        vertex3 = list(
                            get_interpolated_edge_position(
                                p31, p32, -isovalue, float(v31), float(v32)
                            )
                        )
                        n = np.cross(
                            np.array(vertex2) - np.array(vertex1),
                            np.array(vertex3) - np.array(vertex1),
                        )
                        n = list(n / np.linalg.norm(n))
                        verts2 += vertex1 + n + vertex2 + n + vertex3 + n

    return np.array(verts1, dtype=np.float32), np.array(verts2, dtype=np.float32)


def get_edges(
    isovalue: float,
    voxel_values: np.ndarray,
    phase: int=1,
) -> np.ndarray:
    """Calculates the isosurface for a given voxel grid.

    :param isovalue: value of the isosurface
    :param voxel_values: values of the voxels
    :param phase: phase of the orbital
    :return: vertices and indices of the isosurface
    """

    triangle_table_index = np.int8(0)
    if phase == 1:
        if voxel_values[0] > isovalue:
            triangle_table_index += 1
        if voxel_values[1] > isovalue:
            triangle_table_index += 2
        if voxel_values[2] > isovalue:
            triangle_table_index += 4
        if voxel_values[3] > isovalue:
            triangle_table_index += 8
        if voxel_values[4] > isovalue:
            triangle_table_index += 16
        if voxel_values[5] > isovalue:
            triangle_table_index += 32
        if voxel_values[6] > isovalue:
            triangle_table_index += 64
        if voxel_values[7] > isovalue:
            triangle_table_index += 128
    elif phase == -1:
        if voxel_values[0] < -isovalue:
            triangle_table_index += 1
        if voxel_values[1] < -isovalue:
            triangle_table_index += 2
        if voxel_values[2] < -isovalue:
            triangle_table_index += 4
        if voxel_values[3] < -isovalue:
            triangle_table_index += 8
        if voxel_values[4] < -isovalue:
            triangle_table_index += 16
        if voxel_values[5] < -isovalue:
            triangle_table_index += 32
        if voxel_values[6] < -isovalue:
            triangle_table_index += 64
        if voxel_values[7] < -isovalue:
            triangle_table_index += 128
    return triangle_table[triangle_table_index]


def get_interpolated_edge_position(
    p1: np.ndarray,
    p2: np.ndarray,
    iso: float,
    v1: float,
    v2: float,
) -> np.ndarray:
    """Calculates the isosurface for a given voxel grid.

    :param p1: position of the first vertex
    :param p2: position of the second vertex
    :param iso: isovalue
    :param v1: value of the first vertex
    :param v2: value of the second vertex
    """

    return p1 + (iso - v1) * (p2 - p1) / (v2 - v1)
