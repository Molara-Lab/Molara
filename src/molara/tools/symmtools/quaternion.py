"""Quaternion class."""

__all__ = ["Quaternion"]

from math import sin, cos, atan2

from numpy import eye

from .const import INF
from .vecop import norm, normalize, cross
from .transform import VectorTransformable, Rotation
from .primitive import Point
from .typehints import TypeVar, Any, Float, Vector, Matrix, RealVector

_Quaternion = TypeVar("_Quaternion", bound="Quaternion")
_VectorTransformable = TypeVar(
    "_VectorTransformable", bound=VectorTransformable
)


class Quaternion(VectorTransformable):
    """Quaternion."""

    def __init__(self, scalar: Float, vec: RealVector) -> None:
        """
        Initialize the instance with a scalar `scalar` and a 3D vector `vec`.
        """
        self._scalar = float(scalar)
        super().__init__(vec)

    @property
    def scalar(self) -> float:
        """Return the scalar part."""
        return self._scalar

    @property
    def args(self) -> str:
        return f"{self._scalar},{super().args}"

    def diff(self, obj: Any) -> float:
        res = super().diff(obj)
        if res < INF:
            res = max(res, abs(self._scalar - obj.scalar))
        return res

    @property
    def axis(self) -> Vector:
        """Return the axis of rotation."""
        return normalize(self._vec)

    @property
    def angle(self) -> float:
        """Return the angle of rotation."""
        return 2.0 * atan2(norm(self._vec), self._scalar)

    def conjugate(self: _Quaternion) -> _Quaternion:
        """Return the conjugate of the instance."""
        return self.invert()

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        return Quaternion(
            self._scalar * other.scalar - self.vec.dot(other.vec),
            cross(self._vec, other.vec)
            + self._scalar * other.vec
            + other.scalar * self._vec,
        )

    def __call__(self, obj: _VectorTransformable) -> _VectorTransformable:
        """
        Transform the transformable object `obj` by multiplying its vector by
        the instance from the left and by the conjugate of the instance from
        the right.  This transformation is a rotation, if the instance is
        normalized.
        """
        res = obj.copy()
        res._vec = (self * Quaternion(0.0, obj.vec) * self.conjugate()).vec
        return res

    @property
    def mat(self) -> Matrix:
        """Return the transformation matrix."""
        res = eye(3)
        for i in range(3):
            res[i, :] = self(Point(res[i, :])).vec
        return res.T

    @classmethod
    def from_point(cls, point: Point) -> "Quaternion":
        """Construct an instance from a point `point`."""
        return cls(0.0, point.vec)

    @classmethod
    def from_rotation(cls, rot: Rotation) -> "Quaternion":
        """Construct an instance from a rotation `rot`."""
        angle = 0.5 * rot.angle
        return cls(cos(angle), sin(angle) * rot.vec)
