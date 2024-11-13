from libc.stdint cimport int64_t

cpdef double calculate_mo_cartesian(
        double[:],
        double[:,:],
        double[:,:],
        double[:,:],
        double[:,:],
        int64_t[:],
        double[:],
        double[:],
        double[:],
) nogil
