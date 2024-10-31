"""Miscellaneous functions."""

__all__ = [
    "rational",
    "chcoords",
    "signvar",
    "ax3permut",
]

from .typehints import (
    Optional,
    Tuple,
    List,
    Bool,
    Int,
    Real,
    Ints,
    RealVector,
    RealVectors,
)


def rational(num: float, tol: float) -> Tuple[int, int]:
    """
    Determine the rational representation (nominator and denominator) of a
    decimal number `num` within a tolerance `tol`.
    """
    negative = num < 0.0
    num = abs(num)
    nom = 0
    denom = 1
    diff = num - nom / denom
    while abs(diff) > tol:
        if diff > 0.0:
            nom += 1
        else:
            denom += 1
        diff = num - nom / denom
    if negative:
        nom = -nom
    return nom, denom


def chcoords(
    vecs: RealVectors,
    origin: RealVector = (0.0, 0.0, 0.0),
    axes: Optional[Ints] = None,
) -> List[List[Real]]:
    """
    Change the coordinate system of vectors `vecs` to a coordinate system with
    an origin `origin` and an axes order `axes`.  If `axes` is `None`, the
    original axes order is used.
    """
    if axes is None:
        axes = tuple(range(len(origin)))
    origin = tuple(-coord for coord in origin)
    res = []
    for vec in vecs:
        new = [*origin]
        for ax, coord in zip(axes, vec):
            new[ax] += coord
        res.append(new)
    return res


def signvar(
    vec: RealVector, parity: Int = 0, indep: Bool = False
) -> List[List[Real]]:
    """
    Generate vectors with all possible sign changes of the coordinates of a
    vector `vec` that satisfy a parity `parity`.  If `parity` is
    positive/negative, only the vectors resulting from even/odd number of sign
    changes are returned.  If `parity` is zero, all vectors are returned.  If
    `indep` is `True`, only linearly independent vectors are returned.
    """
    res = []
    for n in range(2 ** len(vec)):
        new = [*vec]
        sign = 1
        i = 0
        while n > 0:
            if n % 2 == 1:
                new[i] *= -1
                sign *= -1
            n //= 2
            i += 1
        if (sign * parity >= 0 and new not in res) and not (
            indep and [-coord for coord in new] in res
        ):
            res.append(new)
    return res


def ax3permut(vecs: RealVectors) -> List[List[Real]]:
    """
    Generate all possible vectors by applying a circular permutation on the
    coordinates of 3D vectors `vecs`.
    """
    vecs = chcoords(vecs)
    res = []
    for i in range(3):
        for vec in vecs:
            res.append([vec[i % 3], vec[(i + 1) % 3], vec[(i + 2) % 3]])
    return res
