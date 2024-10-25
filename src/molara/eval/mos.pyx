"""Calculates the value of a molecular orbital at a given point in space."""

from cython.cimports.molara.eval.aos import calculate_aos
from cython import boundscheck, exceptval

cdef int number_of_basis_functions[5]

number_of_basis_functions[0] = 1
number_of_basis_functions[1] = 3
number_of_basis_functions[2] = 6
number_of_basis_functions[3] = 10
number_of_basis_functions[4] = 15

@exceptval(check=False)
@boundscheck(False)
cpdef double calculate_mo_cartesian(
        double[:] electron_position,
        double[:,:] orbital_position,
        double[:,:] orbital_coefficients,
        double[:,:] orbital_exponents,
        double[:,:] orbital_norms,
        long[:] shells,
        double[:] mo_coefficients,
        double[:] aos_values,
) nogil:

    cdef double mo_value = 0.0
    cdef int number_of_orbitals, i, shell_index, shell_start, shell_end, shell

    number_of_orbitals = orbital_coefficients.shape[0]
    number_of_shells = shells.shape[0]
    shell_start = 0
    shell_end = 0
    for shell_index in range(number_of_shells):
        shell = shells[shell_index]
        shell_end = shell_start + number_of_basis_functions[shell]
        _ = calculate_aos(
            electron_position,
            orbital_position[shell_start, :],
            orbital_exponents[shell_start, :],
            orbital_coefficients[shell_start, :],
            orbital_norms[shell_start, :],
            shell,
            aos_values[shell_start:shell_end],
        )
        shell_start = shell_end

    for i in range(number_of_orbitals):
        mo_value += mo_coefficients[i] * aos_values[i]

    return mo_value
