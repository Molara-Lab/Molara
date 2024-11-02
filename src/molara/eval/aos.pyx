"""This module serves the calculation of atomic orbitals."""

from cython.parallel import prange
from cython import boundscheck, exceptval, cdivision
from libc.math cimport exp

__copyright__ = "Copyright 2024, Molara"
@exceptval(check=False)
@boundscheck(False)
@cdivision(True)
cpdef int calculate_aos(
    double[:] electron_coords,
    double[:] atom_coords,
    double[:] exponents,
    double[:] coefficients,
    double[:] norms,
    int orbital,
    double[:] uao) nogil:

    cdef double sqr3 = 1.73205080756887729
    cdef double sqr5 = 2.236067977499789696
    cdef double sqr7 = 2.645751311064591

    cdef int s = 0
    cdef int p = 1
    cdef int d = 2
    cdef int f = 3
    cdef int g = 4

    cdef int fxxx = 0
    cdef int fyyy = 1
    cdef int fzzz = 2
    cdef int fxyy = 3
    cdef int fxxy = 4
    cdef int fxxz = 5
    cdef int fxzz = 6
    cdef int fyzz = 7
    cdef int fyyz = 8
    cdef int fxyz = 9

    cdef int gxxxx = 0
    cdef int gyyyy = 1
    cdef int gzzzz = 2
    cdef int gxxxy = 3
    cdef int gxxxz = 4
    cdef int gyyyx = 5
    cdef int gyyyz = 6
    cdef int gzzzx = 7
    cdef int gzzzy = 8
    cdef int gxxyy = 9
    cdef int gxxzz = 10
    cdef int gyyzz = 11
    cdef int gxxyz = 12
    cdef int gyyxz = 13
    cdef int gzzxy = 14

    cdef double[3] relative_coords
    cdef double r2, u, dx, dy, dz, dx2, dy2, dz2, dxyz
    cdef int ngto = exponents.shape[0]
    cdef int i, ic
    for i in range(3):
        relative_coords[i] = electron_coords[i] - atom_coords[i]
    r2 = (relative_coords[0]**2 +
          relative_coords[1]**2 +
          relative_coords[2]**2)
    u = 0
    for ic in prange(ngto):
        u += norms[ic] * coefficients[ic] * exp(-exponents[ic] * r2)
    if orbital == s:
        uao[0] = u
    elif orbital == p:
        dx = relative_coords[0]
        dy = relative_coords[1]
        dz = relative_coords[2]
        uao[0] = dx * u
        uao[1] = dy * u
        uao[2] = dz * u
    elif orbital == d:
        dx = relative_coords[0]
        dx2 = dx * dx
        dy = relative_coords[1]
        dy2 = dy * dy
        dz = relative_coords[2]
        dz2 = dz * dz
        uao[0] = dx2 * u
        uao[1] = dy2 * u
        uao[2] = dz2 * u
        u = sqr3 * u
        uao[3] = dx * dy * u
        uao[4] = dx * dz * u
        uao[5] = dy * dz * u
    elif orbital == f:
        dx = relative_coords[0]
        dx2 = dx * dx
        dy = relative_coords[1]
        dy2 = dy * dy
        dz = relative_coords[2]
        dz2 = dz * dz
        dxyz = dx * dy * dz
        uao[fxxx] = dx2 * dx * u
        uao[fyyy] = dy2 * dy * u
        uao[fzzz] = dz2 * dz * u
        u = sqr5 * u
        uao[fxxy] = dx2 * dy * u
        uao[fxxz] = dx2 * dz * u
        uao[fxyy] = dy2 * dx * u
        uao[fyyz] = dy2 * dz * u
        uao[fxzz] = dz2 * dx * u
        uao[fyzz] = dz2 * dy * u
        u = sqr3 * u
        uao[fxyz] = dxyz * u
    elif orbital == g:
        dx = relative_coords[0]
        dx2 = dx * dx
        dy = relative_coords[1]
        dy2 = dy * dy
        dz = relative_coords[2]
        dz2 = dz * dz
        dxyz = dx * dy * dz
        uao[gxxxx] = dx2 * dx2 * u
        uao[gyyyy] = dy2 * dy2 * u
        uao[gzzzz] = dz2 * dz2 * u
        u = sqr7 * u
        uao[gxxxy] = dx2 * dx * dy * u
        uao[gxxxz] = dx2 * dx * dz * u
        uao[gyyyx] = dy2 * dy * dx * u
        uao[gyyyz] = dy2 * dy * dz * u
        uao[gzzzx] = dz2 * dz * dx * u
        uao[gzzzy] = dz2 * dz * dy * u
        u = sqr5 / sqr3 * u
        uao[gxxyy] = dx2 * dy2 * u
        uao[gxxzz] = dx2 * dz2 * u
        uao[gyyzz] = dy2 * dz2 * u
        u = sqr3 * u
        uao[gxxyz] = dx * dxyz * u
        uao[gyyxz] = dy * dxyz * u
        uao[gzzxy] = dz * dxyz * u
    return 0
