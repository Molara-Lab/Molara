from __future__ import annotations
from cython import nogil


cimport numpy as npc
cpdef double norm(double[:] x):
    cdef double res = 0
    cdef int i
    for i in range(x.shape[0]):
        res += x[i]*x[i]
    res = res**0.5
    return res
