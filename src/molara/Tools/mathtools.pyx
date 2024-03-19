
cpdef double norm(double[:] x):
    cdef double res = 0
    cdef int i
    for i in range(x.shape[0]):
        res += x[i]*x[i]
    res = res**0.5
    return res

cpdef float norm_float(float[:] x):
    cdef float res = 0
    cdef int i
    for i in range(x.shape[0]):
        res += x[i]*x[i]
    res = res**0.5
    return res
