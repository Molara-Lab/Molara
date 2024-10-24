"""Test the aos module."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import TestCase

import numpy as np
from numpy.testing import assert_almost_equal

from molara.eval.aos import calculate_aos
from molara.structure.io.importer import GeneralImporter

if TYPE_CHECKING:
    from molara.structure.basisset import BasisSet

__copyright__ = "Copyright 2024, Molara"


class TestAos(TestCase):
    """Test the Aos class."""

    def setUp(self) -> None:
        """Set up a basisset."""
        importer_h2 = GeneralImporter("tests/input_files/molden/h2_cas.molden")
        molecules_h2 = importer_h2.load()
        self.basisset_h2 = molecules_h2.mols[0].atoms[0].basis_set
        self.electron_pos_h2 = np.array([0.1, -0.234, 0.5])
        self.nuclear_pos_h2 = np.array([0.0, 0.0, 0.0])

        importer_f2 = GeneralImporter("tests/input_files/molden/f2.molden")
        molecules_f2 = importer_f2.load()
        self.basisset_f2 = molecules_f2.mols[0].atoms[0].basis_set
        self.electron_pos_f2 = np.array([0.15, -0.1, 0.3])
        self.nuclear_pos_f2 = np.array([0.03, 0.01, -0.02])

    def test_aos(self) -> None:
        """Test if the aos are correct.

        Tests still need to be implemented.
        """
        quantum_number_l = {
            "s": 0,
            "p": 1,
            "d": 2,
            "f": 3,
            "g": 4,
        }
        orbital_array_lengths = {
            "s": 1,
            "p": 3,
            "d": 6,
            "f": 10,
            "g": 15,
        }
        # orbital_lists = {
        #     "s": [],
        #     "p": [],
        #     "d": [],
        #     "f": [],
        #     "g": [],
        # }
        # pi = 0

        def _test_orbital(orb: str, basisset: BasisSet, electron_pos: np.ndarray, nuclear_pos: np.ndarray) -> None:
            """Test the orbital."""
            orbital_type = orb[0]
            res = np.zeros(orbital_array_lengths[orb[0]])
            calculate_aos(
                np.array(electron_pos),
                np.array(nuclear_pos),
                basisset.basis_functions[orb].exponents,
                basisset.basis_functions[orb].coefficients,
                basisset.basis_functions[orb].norms,
                quantum_number_l[orbital_type],
                res,
            )
            compare_orbital = reference_calculate_aos(
                electron_pos,
                nuclear_pos,
                basisset.basis_functions[orb].exponents,
                basisset.basis_functions[orb].coefficients,
                quantum_number_l[orbital_type],
                basisset.basis_functions[orb].norms,
            )
            compare_orbital_old_implementation = reference2_calculate_aos(
                electron_pos,
                nuclear_pos,
                basisset.basis_functions[orb].exponents,
                basisset.basis_functions[orb].coefficients,
                quantum_number_l[orbital_type],
                basisset.basis_functions[orb].norms,
            )
            assert res.size == orbital_array_lengths[orbital_type]
            assert_almost_equal(res, compare_orbital)
            assert_almost_equal(res, compare_orbital_old_implementation)

        for orb in self.basisset_h2.basis_functions:
            _test_orbital(orb, self.basisset_h2, self.electron_pos_h2, self.nuclear_pos_h2)
        for orb in self.basisset_f2.basis_functions:
            _test_orbital(orb, self.basisset_f2, self.electron_pos_f2, self.nuclear_pos_f2)


def reference_calculate_aos(  # noqa: PLR0913
    electron_coords: np.ndarray,
    atom_coords: np.ndarray,
    exponents: np.ndarray,
    coefficients: np.ndarray,
    orbital: int,
    norms: np.ndarray,
) -> np.ndarray:
    """Calculate the atomic orbitals for a given atom (cartesian).

    If the orbital is an s orbital, the function the return has size 1, if the orbital is a d orbital, the return
    ha size 6 (dxx, dyy, dzz, etc.).
    :param electron_coords: list of coordinates
    :param atom_coords: list of atom coordinates
    :param exponents: list of exponents
    :param coefficients: list of coefficients
    :param orbital: Name of the orbital (ie, s, p, d, etc.)
    :param norms: Norms of the orbitals
    :return: Value of the atomic orbital(s) for a given atom position and electron position
    """
    sqr3 = 1.73205080756887729
    sqr5 = 2.236067977499789696
    sqr7 = 2.645751311064591
    s, p, d, f, g = 0, 1, 2, 3, 4

    ngto = len(exponents)
    relative_coords = electron_coords - atom_coords
    dx, dy, dz = relative_coords
    dx2, dy2, dz2 = dx**2, dy**2, dz**2
    dxyz = dx * dy * dz
    rr = np.linalg.norm(relative_coords)
    r2 = rr**2
    if orbital == s:
        uao = np.zeros(1)
        directional_factors = np.array([1.0])
    elif orbital == p:
        uao = np.zeros(3)
        directional_factors = np.array([dx, dy, dz])
    elif orbital == d:
        uao = np.zeros(6)
        directional_factors = np.array(
            [
                dx2,
                dy2,
                dz2,
                sqr3 * dx * dy,
                sqr3 * dx * dz,
                sqr3 * dy * dz,
            ],
        )
    elif orbital == f:
        uao = np.zeros(10)
        directional_factors = np.array(
            [
                dx2 * dx,  # fxxx
                dy2 * dy,  # fyyy
                dz2 * dz,  # fzzz
                sqr5 * dx2 * dy,  # fxyy
                sqr5 * dx2 * dz,  # fxxy
                sqr5 * dy2 * dx,  # fxxz
                sqr5 * dy2 * dz,  # fxzz
                sqr5 * dz2 * dx,  # fyyz
                sqr5 * dz2 * dy,  # fyzz
                sqr5 * sqr3 * dxyz,  # fxyz
            ],
        )
    elif orbital == g:
        uao = np.zeros(15)
        directional_factors = np.array(
            [
                dx2 * dx2,
                dy2 * dy2,
                dz2 * dz2,
                sqr7 * dx2 * dx * dy,
                sqr7 * dx2 * dx * dz,
                sqr7 * dy2 * dy * dx,
                sqr7 * dy2 * dy * dz,
                sqr7 * dz2 * dz * dx,
                sqr7 * dz2 * dz * dy,
                sqr7 * sqr5 / sqr3 * dx2 * dy2,
                sqr7 * sqr5 / sqr3 * dx2 * dz2,
                sqr7 * sqr5 / sqr3 * dy2 * dz2,
                sqr7 * sqr5 * dx * dxyz,
                sqr7 * sqr5 * dy * dxyz,
                sqr7 * sqr5 * dz * dxyz,
            ],
        )
    else:
        msg = "(calculate_aos): wrong GTO"
        raise TypeError(msg)
    for ic in range(ngto):
        u = coefficients[ic] * np.exp(-exponents[ic] * r2)
        uao += directional_factors * u * norms[ic]
    return uao


# Long-term: delete this function
# The function is used to compare the results of the new implementation with the old one.
# Once we are confident that the new implementation is correct, we can delete this function.
def reference2_calculate_aos(  # noqa: C901 PLR0915 PLR0913
    electron_coords: np.ndarray,
    atom_coords: np.ndarray,
    exponents: np.ndarray,
    coefficients: np.ndarray,
    orbital: int,
    norms: np.ndarray,
) -> np.ndarray:
    """Calculate the atomic orbitals for a given atom (cartesian).

    If the orbital is an s orbital, the function the return has size 1, if the orbital is a d orbital, the return
    ha size 6 (dxx, dyy, dzz, etc.).
    :param electron_coords: list of coordinates
    :param atom_coords: list of atom coordinates
    :param exponents: list of exponents
    :param coefficients: list of coefficients
    :param orbital: Name of the orbital (ie, s, p, d, etc.)
    :param norms: Norms of the orbitals
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
            u = coefficients[ic] * np.exp(-exponents[ic] * r2) * norms[ic]
            uao[0] = uao[0] + u
    elif orbital == p:
        uao = np.zeros(3)
        for ic in range(ngto):
            u = coefficients[ic] * np.exp(-exponents[ic] * r2) * norms[ic]
            dx = relative_coords[0]
            dy = relative_coords[1]
            dz = relative_coords[2]
            uao[0] = uao[0] + dx * u
            uao[1] = uao[1] + dy * u
            uao[2] = uao[2] + dz * u
    elif orbital == d:
        uao = np.zeros(6)
        for ic in range(ngto):
            u = coefficients[ic] * np.exp(-exponents[ic] * r2) * norms[ic]
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
            u = coefficients[ic] * np.exp(-exponents[ic] * r2) * norms[ic]
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
            u = coefficients[ic] * np.exp(-exponents[ic] * r2) * norms[ic]
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
