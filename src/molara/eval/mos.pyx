"""Calculates the value of a molecular orbital at a given point in space."""

from molara.eval.aos cimport calculate_aos
from cython.parallel import prange
from cython.cimports.molara.eval.aos import calculate_aos
from cython import boundscheck, exceptval


@exceptval(check=False)
@boundscheck(False)
cpdef double calculate_mo_cartesian(
        double[:] electron_position,
        double[:,:] orbital_position,
        double[:,:] orbital_coefficients,
        double[:,:] orbital_exponents,
        double[:,:] orbital_norms,
        long[:,:] orbital_ijk,
        double[:] mo_coefficients,
        double[:] aos_values,
) nogil:

    cdef double mo_value = 0.0
    cdef int mo_index, number_of_orbitals, i
    cdef int s = 0, p = 1, d = 2, f = 3, g = 4
    cdef int aos_pre_calculated = 0, shell

    number_of_orbitals = orbital_coefficients.shape[0]
    mo_index = 0
    for mo_index in range(number_of_orbitals):
        shell = orbital_ijk[mo_index, 0] + orbital_ijk[mo_index, 1] + orbital_ijk[mo_index, 2]
        if aos_pre_calculated == 0:
            _ = calculate_aos(
                electron_position,
                orbital_position[mo_index, :],
                orbital_exponents[mo_index, :],
                orbital_coefficients[mo_index, :],
                orbital_norms[mo_index, :],
                shell,
                aos_values,
            )
            if shell == s:
                mo_value += mo_coefficients[mo_index] * aos_values[0]
            if shell == p:
                for i in prange(3):
                    mo_value += mo_coefficients[mo_index + i] * aos_values[i]
                aos_pre_calculated = 2
            if shell == d:
                for i in prange(6):
                    mo_value += mo_coefficients[mo_index + i] * aos_values[i]
                aos_pre_calculated = 5
            if shell == f:
                for i in prange(10):
                    mo_value += mo_coefficients[mo_index + i] * aos_values[i]
                aos_pre_calculated = 9
            if shell == g:
                for i in prange(15):
                    mo_value += mo_coefficients[mo_index + i] * aos_values[i]
                aos_pre_calculated = 14
        else:
            aos_pre_calculated -= 1
    return mo_value
