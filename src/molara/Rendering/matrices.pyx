import numpy as np
cimport numpy as npc
from cython.parallel import prange
from cython import nogil

def calculate_model_matrices(npc.ndarray[float, ndim=3] translation, npc.ndarray[float, ndim=3]  scale):

    cdef int n = translation.shape[0], i
    cdef npc.ndarray[float, ndim=3] model_matrix = np.zeros((n, 4, 4), dtype=np.float32)

    with nogil:
        for i in prange(n):
            model_matrix[i, 0, 0] = scale[i, 0, 0]
            model_matrix[i, 1, 1] = scale[i, 1, 1]
            model_matrix[i, 2, 2] = scale[i, 2, 2]
            model_matrix[i, 3, 3] = 1.0
            model_matrix[i, 3, 0] = translation[i, 3, 0]
            model_matrix[i, 3, 1] = translation[i, 3, 1]
            model_matrix[i, 3, 2] = translation[i, 3, 2]
    return np.array(
        model_matrix,
        dtype=np.float32,
    )

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

def calculate_scale_matrices(npc.ndarray[float, ndim=2] scales) -> np.ndarray:
    """Calculates the scale matrix for a sphere.

    :param radius: Radius of the sphere.
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
