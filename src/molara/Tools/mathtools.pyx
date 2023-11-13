from __future__ import annotations

cimport numpy as npc
cpdef double norm(npc.ndarray[double, ndim=1] x):
    cdef double res = 0
    cdef int i
    for i in range(len(x)):
        res += x[i]*x[i]
    res = res**0.5
    return res