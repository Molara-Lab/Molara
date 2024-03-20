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

    fxxx = 0
    fyyy = 1
    fzzz = 2
    fxyy = 3
    fxxy = 4
    fxxz = 5
    fxzz = 6
    fyzz = 7
    fyyz = 8
    fxyz = 9

    gxxxx = 0
    gyyyy = 1
    gzzzz = 2
    gxxxy = 3
    gxxxz = 4
    gyyyx = 5
    gyyyz = 6
    gzzzx = 7
    gzzzy = 8
    gxxyy = 9
    gxxzz = 10
    gyyzz = 11
    gxxyz = 12
    gyyxz = 13
    gzzxy = 14

    ngto = len(exponents)
    relative_coords = electron_coords - atom_coords
    rr = np.linalg.norm(relative_coords)
    r2 = rr * rr
    if orbital == s:
        uao = np.zeros(1)
        for ic in range(ngto):
            u = coefficients[ic] * np.exp(-exponents[ic] * r2)
            uao[0] = uao[0] + u
    elif orbital == p:
        uao = np.zeros(3)
        for ic in range(ngto):
            u = coefficients[ic] * np.exp(-exponents[ic] * r2)
            dx = relative_coords[0]
            dy = relative_coords[1]
            dz = relative_coords[2]
            uao[0] = uao[0] + dx * u
            uao[1] = uao[1] + dy * u
            uao[2] = uao[2] + dz * u
    elif orbital == d:
        uao = np.zeros(6)
        for ic in range(ngto):
            u = coefficients[ic] * np.exp(-exponents[ic] * r2)
            dx = relative_coords[0]
            dx2 = dx * dx
            dy = relative_coords[1]
            dy2 = dy * dy
            dz = relative_coords[2]
            dz2 = dz * dz
            uao[0] = uao[0] + dx2 * u
            uao[1] = uao[1] + dy2 * u
            uao[2] = uao[2] + dz2 * u
            u = sqr3 * u
            uao[3] = uao[3] + dx * dy * u
            uao[4] = uao[4] + dx * dz * u
            uao[5] = uao[5] + dy * dz * u
    elif orbital == f:
        uao = np.zeros(10)
        for ic in range(ngto):
            u = coefficients[ic] * np.exp(-exponents[ic] * r2)
            dx = relative_coords[0]
            dx2 = dx * dx
            dy = relative_coords[1]
            dy2 = dy * dy
            dz = relative_coords[2]
            dz2 = dz * dz
            dxyz = dx * dy * dz
            uao[fxxx] = uao[fxxx] + dx2 * dx * u
            uao[fyyy] = uao[fyyy] + dy2 * dy * u
            uao[fzzz] = uao[fzzz] + dz2 * dz * u
            u = sqr5 * u
            uao[fxxy] = uao[fxxy] + dx2 * dy * u
            uao[fxxz] = uao[fxxz] + dx2 * dz * u
            uao[fxyy] = uao[fxyy] + dy2 * dx * u
            uao[fyyz] = uao[fyyz] + dy2 * dz * u
            uao[fxzz] = uao[fxzz] + dz2 * dx * u
            uao[fyzz] = uao[fyzz] + dz2 * dy * u
            u = sqr3 * u
            uao[fxyz] = uao[fxyz] + dxyz * u
    elif orbital == g:
        uao = np.zeros(15)
        for ic in range(ngto):
            u = coefficients[ic] * np.exp(-exponents[ic] * r2)
            dx = relative_coords[0]
            dx2 = dx * dx
            dy = relative_coords[1]
            dy2 = dy * dy
            dz = relative_coords[2]
            dz2 = dz * dz
            dxyz = dx * dy * dz
            uao[gxxxx] = uao[gxxxx] + dx2 * dx2 * u
            uao[gyyyy] = uao[gyyyy] + dy2 * dy2 * u
            uao[gzzzz] = uao[gzzzz] + dz2 * dz2 * u
            u = sqr7 * u
            uao[gxxxy] = uao[gxxxy] + dx2 * dx * dy * u
            uao[gxxxz] = uao[gxxxz] + dx2 * dx * dz * u
            uao[gyyyx] = uao[gyyyx] + dy2 * dy * dx * u
            uao[gyyyz] = uao[gyyyz] + dy2 * dy * dz * u
            uao[gzzzx] = uao[gzzzx] + dz2 * dz * dx * u
            uao[gzzzy] = uao[gzzzy] + dz2 * dz * dy * u
            u = sqr5 / sqr3 * u
            uao[gxxyy] = uao[gxxyy] + dx2 * dy2 * u
            uao[gxxzz] = uao[gxxzz] + dx2 * dz2 * u
            uao[gyyzz] = uao[gyyzz] + dy2 * dz2 * u
            u = sqr3 * u
            uao[gxxyz] = uao[gxxyz] + dx * dxyz * u
            uao[gyyxz] = uao[gyyxz] + dy * dxyz * u
            uao[gzzxy] = uao[gzzxy] + dz * dxyz * u
    else:
        msg = "(calculate_aos): wrong GTO"
        raise TypeError(msg)
    return uao
