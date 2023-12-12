import numpy as np
cimport numpy as npc
from cython.parallel import prange
from cython import boundscheck, exceptval
from cython import nogil

@boundscheck(False)
def calculate_model_matrices(float[:,:,:] translation, float[:,:,:] scale,
                             float[:,:,:] rotation=np.array([[[-1.0]]], dtype=np.float32),
                             bint cylinder=False):

    cdef int n = translation.shape[0], i, j, k, l
    cdef float[:,:,:] model_matrices = np.zeros((n, 4, 4), dtype=np.float32)
    cdef float[:,:] temp = np.zeros((3,3), dtype=np.float32)
    cdef float temp1

    model_matrices[:, 3, 3] = 1.0
    with nogil:
        if rotation[0, 0, 0] == -1:
            for i in prange(n):
                model_matrices[i, 0, 0] = scale[i, 0, 0]
                model_matrices[i, 1, 1] = scale[i, 1, 1]
                model_matrices[i, 2, 2] = scale[i, 2, 2]
                model_matrices[i, 3, 0] = translation[i, 3, 0]
                model_matrices[i, 3, 1] = translation[i, 3, 1]
                model_matrices[i, 3, 2] = translation[i, 3, 2]
        else:
            for i in prange(n):
                if cylinder:
                    if (i % 2) == 0:
                        dot_product_m(rotation[i//2, :, :], scale[i//2, :, :], temp)
                else:
                    dot_product_m(rotation[i, :, :], scale[i, :, :], temp)
                model_matrices[i, :3, :3] = temp[:,:]
                model_matrices[i, 3, 0] = translation[i, 3, 0]
                model_matrices[i, 3, 1] = translation[i, 3, 1]
                model_matrices[i, 3, 2] = translation[i, 3, 2]
    return np.array(
        model_matrices,
        dtype=np.float32,
    )
@exceptval(check=False)
@boundscheck(False)
cdef int dot_product_m(float[:,:] a, float[:,:] b, float[:,:] res) nogil:
    """Calculates the dot product of two matrices.

    :param res: Resulting matrix.
    :param a: First matrix.
    :param b: Second matrix.
    """
    cdef int j, k, l

    for j in prange(3):
        for k in prange(3):
            res[k, j] = 0.0
            for l in range(3):
                res[k, j] = res[k, j] + a[j, l] * b[l, k]

    return 0
@boundscheck(False)
def calculate_translation_matrices(npc.ndarray[float, ndim=2] positions) -> npc.ndarray:
    """Calculates the translation matrix for a sphere.

    :param position: Position of the sphere.
    :return: Translation matrix of the sphere.
    """

    cdef npc.ndarray[float, ndim=3] translation_matrices = np.zeros((positions.shape[0], 4, 4), dtype=np.float32)
    cdef int n = positions.shape[0], i

    with nogil:
        for i in prange(n):
            translation_matrices[i, 0, 0] = 1.0
            translation_matrices[i, 1, 1] = 1.0
            translation_matrices[i, 2, 2] = 1.0
            translation_matrices[i, 3, 3] = 1.0
            translation_matrices[i, 3, 0] = positions[i, 0]
            translation_matrices[i, 3, 1] = positions[i, 1]
            translation_matrices[i, 3, 2] = positions[i, 2]


    return np.array(translation_matrices, dtype=np.float32)

@boundscheck(False)
def calculate_scale_matrices(npc.ndarray[float, ndim=2] scales) -> np.ndarray:
    """Calculates the scale matrix for a sphere.

    :param scales: Scales of the spheres.
    :return: Scale matrix of the sphere.
    """

    cdef npc.ndarray[float, ndim=3] scale_matrices = np.zeros((scales.shape[0], 4, 4), dtype=np.float32)
    cdef int n = scales.shape[0], i

    with nogil:
        for i in prange(n):
            scale_matrices[i, 0, 0] = scales[i, 0]
            scale_matrices[i, 1, 1] = scales[i, 1]
            scale_matrices[i, 2, 2] = scales[i, 2]
            scale_matrices[i, 3, 3] = 1.0

    return np.array(scale_matrices, dtype=np.float32)

@boundscheck(False)
def calculate_rotation_matrices(
    double[:,:] directions,
):
    """Calculates the rotation matrix.

    :param directions: Direction the y-axis of the rotated object should be rotated to.
    :return: Rotation matrices.
    """
    cdef npc.ndarray[float, ndim=3] rotation_matrices = np.zeros((directions.shape[0], 4, 4), dtype=np.float32)
    cdef int n = directions.shape[0], i, j, k
    cdef double[3] rotation_axis
    cdef float rotation_angle, x, y, z, c, s, t, dot_product
    cdef float normalized_direction[3]
    cdef double direction_norm
    cdef float[3] y_axis = [0., 1., 0.]

    with (nogil):
        for i in prange(n):
            direction_norm = (directions[i, 0]**2 + directions[i, 1]**2 + directions[i, 2]**2)**0.5
            normalized_direction[0] = directions[i, 0] / direction_norm
            normalized_direction[1] = directions[i, 1] / direction_norm
            normalized_direction[2] = directions[i, 2] / direction_norm
            dot_product = -(y_axis[0]*normalized_direction[0] + y_axis[1]*normalized_direction[1] + y_axis[2]*normalized_direction[2])
            if dot_product != 1 and dot_product != -1:
                rotation_axis[0] = y_axis[1] * normalized_direction[2] - y_axis[2] * normalized_direction[1]
                rotation_axis[1] = y_axis[2] * normalized_direction[0] - y_axis[0] * normalized_direction[2]
                rotation_axis[2] = y_axis[0] * normalized_direction[1] - y_axis[1] * normalized_direction[0]
                c = dot_product
                s = (rotation_axis[0]**2 + rotation_axis[1]**2 + rotation_axis[2]**2)**0.5
                x = rotation_axis[0] / s
                y = rotation_axis[1] / s
                z = rotation_axis[2] / s
                t = 1 - c

                rotation_matrices[i, 0, 0] = t*x*x + c
                rotation_matrices[i, 0, 1] = t*x*y + s*z
                rotation_matrices[i, 0, 2] = t*x*z - s*y
                rotation_matrices[i, 1, 0] = t*x*y - s*z
                rotation_matrices[i, 1, 1] = t*y*y + c
                rotation_matrices[i, 1, 2] = t*y*z + s*x
                rotation_matrices[i, 2, 0] = t*x*z + s*y
                rotation_matrices[i, 2, 1] = t*y*z - s*x
                rotation_matrices[i, 2, 2] = t*z*z + c
                rotation_matrices[i, 3, 3] = 1.0
            else:
                for j in prange(3):
                    for k in prange(3):
                        if j == k:
                            rotation_matrices[i, j, k] = 1.0
                        else:
                            rotation_matrices[i, j, k] = 0.0

    return np.array(rotation_matrices, dtype=np.float32)
