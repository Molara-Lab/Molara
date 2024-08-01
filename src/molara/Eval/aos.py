"""Serves the calculation of atomic orbitals."""

from __future__ import annotations

import numpy as np

__copyright__ = "Copyright 2024, Molara"


def calculate_aos(  # noqa: PLR0915 C901
    electron_coords: np.ndarray,
    atom_coords: np.ndarray,
    exponents: np.ndarray,
    coefficients: np.ndarray,
    orbital: int,
) -> np.ndarray:
    """Calculate the atomic orbitals for a given atom (cartesian).

    If the orbital is an s orbital, the function the return has size 1, if the orbital is a d orbital, the return
    ha size 6 (dxx, dyy, dzz, etc.).
    :param electron_coords: list of coordinates
    :param atom_coords: list of atom coordinates
    :param exponents: list of exponents
    :param coefficients: list of coefficients
    :param orbital: Name of the orbital (ie, s, p, d, etc.)
    :return: Value of the atomic orbital(s) for a given atom position and electron position
    """
    sqr3 = 1.73205080756887729
    sqr5 = 2.236067977499789696
    sqr7 = 2.645751311064591

    s = 0
    p = 1
    d = 2
    f = 3
    g = 4

    # # shortcuts for the array-entry indices of f atomic orbitals
    # fxxx, fyyy, fzzz = 0, 1, 2
    # fxyy, fxxy = 3, 4
    # fxxz, fxzz = 5, 6
    # fyzz, fyyz  = 7, 8
    # fxyz = 9

    # # shortcuts for the array-entry indices of f atomic orbitals
    # gxxxx, gyyyy, gzzzz = 0, 1, 2
    # gxxxy, gxxxz = 3, 4
    # gyyyx, gyyyz = 5, 6
    # gzzzx, gzzzy = 7, 8
    # gxxyy, gxxzz = 9, 10
    # gyyzz, gxxyz = 11, 12
    # gyyxz, gzzxy = 13, 14

    ngto = len(exponents)
    relative_coords = electron_coords - atom_coords
    dx, dy, dz = relative_coords
    dx2, dy2, dz2 = dx**2, dy**2, dz**2
    dxyz = dx * dy * dz
    rr = np.linalg.norm(relative_coords)
    r2 = rr**2
    if orbital == s:
        uao = np.zeros(1)
        directional_factors = np.array([1.])
    elif orbital == p:
        uao = np.zeros(3)
        directional_factors = np.array([dx, dy, dz])
    elif orbital == d:
        uao = np.zeros(6)
        directional_factors = np.array([
            dx2,
            dy2,
            dz2,
            sqr3*dx*dy,
            sqr3*dx*dz,
            sqr3*dy*dz,
        ])
    elif orbital == f:
        uao = np.zeros(10)
        directional_factors = np.array([
            dx2*dx,# fxxx
            dy2*dy,# fyyy
            dz2*dz,# fzzz
            sqr5*dx2*dy,# fxyy
            sqr5*dx2*dz,# fxxy
            sqr5*dy2*dx,# fxxz
            sqr5*dy2*dz,# fxzz
            sqr5*dz2*dx,# fyyz
            sqr5*dz2*dy,# fyzz
            sqr5*sqr3*dxyz,# fxyz
        ])
    elif orbital == g:
        uao = np.zeros(15)
        directional_factors = np.array([
            dx2 * dx2,
            dy2 * dy2,
            dz2 * dz2,
            sqr7*dx2 * dx * dy,
            sqr7*dx2 * dx * dz,
            sqr7*dy2 * dy * dx,
            sqr7*dy2 * dy * dz,
            sqr7*dz2 * dz * dx,
            sqr7*dz2 * dz * dy,
            sqr7*sqr5/sqr3*dx2 * dy2,
            sqr7*sqr5/sqr3*dx2 * dz2,
            sqr7*sqr5/sqr3*dy2 * dz2,
            sqr7*sqr5*dx * dxyz,
            sqr7*sqr5*dy * dxyz,
            sqr7*sqr5*dz * dxyz,
        ])
    else:
        msg = "(calculate_aos): wrong GTO"
        raise TypeError(msg)
    for ic in range(ngto):
        u = coefficients[ic] * np.exp(-exponents[ic] * r2)
        uao += directional_factors * u
    return uao
