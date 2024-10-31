"""Functions for basic vector operations."""

__all__ = [
    "clamp",
    "vector",
    "norm",
    "cross",
    "normalize",
    "orthogonalize",
    "canonicalize",
    "diff",
    "same",
    "zero",
    "indep",
    "unitindep",
    "parallel",
    "unitparallel",
    "perpendicular",
    "angle",
    "intersectangle",
    "translate",
    "invert",
    "move2",
    "rotate",
    "vecrotate",
    "reflect",
    "rotmat",
    "reflmat",
    "inertia",
]

from math import sqrt, sin, cos, acos
from numpy import array, empty

from .const import PI, PI_2
from .typehints import Sequence, Float, Vector, Matrix, RealVector

# `max` is faster than `numpy.ndarray.max`
# `float` is faster than `numpy.float64.item`
# `sqrt`, `sin`, `cos`, `acos` from `math` are faster than from `numpy`


def clamp(val: Float, low: Float, high: Float) -> Float:
    """Clamp a value `val` within the interval between `low` and `high`."""
    # `numpy.clip` is slower
    if val < low:
        return low
    elif val > high:
        return high
    else:
        return val


def vector(vec: RealVector) -> Vector:
    """Convert a vector `vec` to a NumPy array of floating-point numbers."""
    return array(vec, dtype=float)


def norm(vec: Vector) -> float:
    """Calculate the norm of a vector `vec`."""
    # `numpy.linalg.norm` is slower
    return sqrt(vec.dot(vec))


def cross(vec1: Vector, vec2: Vector) -> Vector:
    """Calculate the cross product of two 3D vectors `vec1` and `vec2`."""
    # `numpy.cross` is slower
    x1, y1, z1 = vec1
    x2, y2, z2 = vec2
    vec = empty(3)
    vec[0] = y1 * z2 - z1 * y2
    vec[1] = z1 * x2 - x1 * z2
    vec[2] = x1 * y2 - y1 * x2
    return vec


def normalize(vec: Vector) -> Vector:
    """Normalize a non-zero vector `vec` to a unit vector."""
    return vec / norm(vec)


def orthogonalize(vec: Vector, unitvec: Vector) -> Vector:
    """Orthogonalize a vector `vec` to a unit vector `unitvec`."""
    return vec - vec.dot(unitvec) * unitvec


def canonicalize(vec: Vector) -> Vector:
    """
    Canonicalize an unsigned direction vector `vec` by making the first
    non-zero coordinate positive.
    """
    for coord in vec:
        if coord < 0.0:
            vec = -vec
        if coord != 0.0:
            break
    return vec


def diff(vec1: Vector, vec2: Vector) -> float:
    """Calculate the difference between two vectors `vec1` and `vec2`."""
    # `norm(vec1 - vec2)` is slower
    return float(max(abs(vec1 - vec2)))


def same(vec1: Vector, vec2: Vector, tol: float) -> bool:
    """
    Check whether two vectors `vec1` and `vec2` are the same within a tolerance
    `tol`.
    """
    return diff(vec1, vec2) <= tol


def zero(vec: Vector, tol: float) -> bool:
    """
    Check whether a vector `vec` is a zero vector within a tolerance `tol`.
    """
    return float(max(abs(vec))) <= tol


def indep(vec1: Vector, vec2: Vector) -> float:
    """
    Calculate the linear independence of two 3D vectors `vec1` and `vec2`.
    """
    # `norm(cross(vec1, vec2))` is slower
    return float(max(abs(cross(vec1, vec2))))


def unitindep(unitvec1: Vector, unitvec2: Vector) -> float:
    """
    Calculate the linear independence of two 3D unit vectors `unitvec1` and
    `unitvec2`.
    """
    # `abs(abs(unitvec1.dot(unitvec2)) - 1)` is faster but less accurate
    # `min(diff(unitvec1, unitvec2), diff(unitvec1, -unitvec2))` is slower
    x1, y1, z1 = unitvec1
    x2, y2, z2 = unitvec2
    return min(
        max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2)),
        max(abs(x1 + x2), abs(y1 + y2), abs(z1 + z2)),
    )


def parallel(vec1: Vector, vec2: Vector, tol: float) -> bool:
    """
    Check whether two 3D vectors `vec1` and `vec2` are parallel within a
    tolerance `tol`.
    """
    return indep(vec1, vec2) <= tol


def unitparallel(unitvec1: Vector, unitvec2: Vector, tol: float) -> bool:
    """
    Check whether two 3D unit vectors `unitvec1` and `unitvec2` are parallel
    within a tolerance `tol`.
    """
    return unitindep(unitvec1, unitvec2) <= tol


def perpendicular(vec1: Vector, vec2: Vector, tol: float) -> bool:
    """
    Check whether two vectors `vec1` and `vec2` are perpendicular within a
    tolerance `tol`.
    """
    return abs(float(vec1.dot(vec2))) <= tol


def angle(vec1: Vector, vec2: Vector) -> float:
    """Calculate the angle between two vectors `vec1` and `vec2`."""
    # `acos(clamp(unitvec1.dot(unitvec2), -1.0, 1.0))` is less accurate
    return acos(
        clamp(
            vec1.dot(vec2) / sqrt(vec1.dot(vec1) * vec2.dot(vec2)), -1.0, 1.0
        )
    )


def intersectangle(vec1: Vector, vec2: Vector) -> float:
    """
    Calculate the intersection angle between two lines described by two vectors
    `vec1` and `vec2`.
    """
    ang = angle(vec1, vec2)
    if ang > PI_2:
        ang = PI - ang
    return ang


def translate(vec: Vector, transl: Vector) -> Vector:
    """Translate a vector `vec` by a translation vector `transl`."""
    return vec + transl


def invert(vec: Vector) -> Vector:
    """Invert a vector `vec` through the origin."""
    return -vec


def move2(point: Vector, normal: Vector, coef1: Float, coef2: Float) -> Vector:
    """
    Move a 3D point `point` in a plane containing the point with a normalized
    normal `normal` to the position represented by the linear combination of
    the projection of the point position on the plane scaled by `coef1` and its
    perpendicular in the plane scaled by `coef2`.
    """
    base = point.dot(normal) * normal
    projection = point - base
    perpendicular = cross(normal, projection)
    return base + projection * coef1 + perpendicular * coef2


def rotate(vec: Vector, axis: Vector, angle: Float) -> Vector:
    """
    Rotate a 3D vector `vec` by an angle `angle` around an axis that contains
    the origin and is described by a unit vector `axis`.
    """
    return move2(vec, axis, cos(angle), sin(angle))


def vecrotate(vec: Vector, rotvec: Vector) -> Vector:
    """Rotate a 3D vector `vec` by a rotation vector `rotvec`."""
    length = sqrt(rotvec.dot(rotvec))
    if length > 0.0:
        vec = rotate(vec, rotvec / length, length)
    return vec


def reflect(vec: Vector, normal: Vector) -> Vector:
    """
    Reflect a vector `vec` through a plane that contains the origin and whose
    normal is described by a unit vector `normal`.
    """
    return vec - 2.0 * vec.dot(normal) * normal


def rotmat(axis: Vector, angle: Float) -> Matrix:
    """
    Generate a 3D transformation matrix for a rotation by an angle `angle`
    around an axis that contains the origin and is described by a unit vector
    `axis`.
    """
    x, y, z = axis
    c = cos(angle)
    s = sin(angle)
    xc = x * (1.0 - c)
    yc = y * (1.0 - c)
    zc = z * (1.0 - c)
    xs = x * s
    ys = y * s
    zs = z * s
    xyc = x * yc
    yzc = y * zc
    zxc = z * xc
    mat = empty((3, 3))
    mat[0, 0] = c + x * xc
    mat[0, 1] = xyc - zs
    mat[0, 2] = zxc + ys
    mat[1, 0] = xyc + zs
    mat[1, 1] = c + y * yc
    mat[1, 2] = yzc - xs
    mat[2, 0] = zxc - ys
    mat[2, 1] = yzc + xs
    mat[2, 2] = c + z * zc
    return mat


def reflmat(normal: Vector) -> Matrix:
    """
    Generate a 3D transformation matrix for a reflection through a plane that
    contains the origin and whose normal is described by a unit vector
    `normal`.
    """
    x, y, z = normal
    dx = x + x
    dy = y + y
    dz = z + z
    xy = -x * dy
    yz = -y * dz
    zx = -z * dx
    mat = empty((3, 3))
    mat[0, 0] = 1.0 - x * dx
    mat[0, 1] = xy
    mat[0, 2] = zx
    mat[1, 0] = xy
    mat[1, 1] = 1.0 - y * dy
    mat[1, 2] = yz
    mat[2, 0] = zx
    mat[2, 1] = yz
    mat[2, 2] = 1.0 - z * dz
    return mat


def inertia(vecs: Sequence[Vector]) -> Matrix:
    """
    Calculate the inertia tensor of the points of unit mass with positions
    `vecs`.
    """
    xx = 0.0
    yy = 0.0
    zz = 0.0
    xy = 0.0
    zx = 0.0
    yz = 0.0
    for vec in vecs:
        x, y, z = vec
        xs = x * x
        ys = y * y
        zs = z * z
        xx += ys + zs
        yy += zs + xs
        zz += xs + ys
        xy -= x * y
        zx -= x * z
        yz -= y * z
    mat = empty((3, 3))
    mat[0, 0] = xx
    mat[0, 1] = xy
    mat[0, 2] = zx
    mat[1, 0] = xy
    mat[1, 1] = yy
    mat[1, 2] = yz
    mat[2, 0] = zx
    mat[2, 1] = yz
    mat[2, 2] = zz
    return mat
