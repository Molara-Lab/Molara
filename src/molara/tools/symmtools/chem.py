__all__ = [
    "s_orb",
    "px_orb",
    "py_orb",
    "dx2y2_orb",
    "dz2_orb",
    "dxy_orb",
    "dyz_orb",
    "dxz_orb",
]

from .primitive import Arrow, StructPoint


def s_orb(pos, coef=1):
    return StructPoint(pos, coef)


def px_orb(pos, coef=1):
    return StructPoint(pos, coef, [Arrow([1, 0, 0], True, False)])


def py_orb(pos, coef=1):
    return StructPoint(pos, coef, [Arrow([0, 1, 0], True, False)])


def pz_orb(pos, coef=1):
    return StructPoint(pos, coef, [Arrow([0, 0, 1], True, False)])


def dx2y2_orb(pos, coef=1):
    return StructPoint(
        pos,
        coef,
        [Arrow([1, 0, 0], True, True), Arrow([0, 1, 0], False, False)],
    )


def dz2_orb(pos, coef=1):
    return StructPoint(pos, coef, [Arrow([0, 0, 1], True, True)])


def dxy_orb(pos, coef=1):
    return StructPoint(
        pos,
        coef,
        [Arrow([1, 1, 0], True, True), Arrow([1, -1, 0], False, False)],
    )


def dyz_orb(pos, coef=1):
    return StructPoint(
        pos,
        coef,
        [Arrow([0, 1, 1], True, True), Arrow([0, 1, -1], False, False)],
    )


def dxz_orb(pos, coef=1):
    return StructPoint(
        pos,
        coef,
        [Arrow([1, 0, 1], True, True), Arrow([-1, 0, 1], False, False)],
    )
