"""Classes for primitive objects in a real 3D space."""

__all__ = ["Point", "Points", "LabeledPoint", "Arrow", "StructPoint"]

from abc import ABC, abstractmethod
from math import sin, cos
from re import findall

from numpy import zeros
from numpy.linalg import eigh

from .const import (
    INF,
    PI,
    TOL,
    SPECIAL_ANGLES,
    SPECIAL_COMPONENTS,
    LABEL_RE,
    FLOAT_RE,
)
from .vecop import (
    norm,
    cross,
    normalize,
    orthogonalize,
    diff,
    zero,
    unitindep,
    parallel,
    unitparallel,
    perpendicular,
    angle,
    inertia,
)
from .transform import (
    Transformable,
    Transformables,
    Transformation,
    VectorTransformable,
    DirectionTransformable,
    Translation,
    Rotation,
    Reflection,
    Rotoreflection,
)
from .symmelem import (
    SymmetryElement,
    InversionCenter,
    RotationAxis,
    InfRotationAxis,
    ReflectionPlane,
    RotoreflectionAxis,
    InfRotoreflectionAxis,
    AxisRotationAxes,
    CenterRotationAxes,
    AxisReflectionPlanes,
    CenterReflectionPlanes,
    CenterRotoreflectionAxes,
)
from .typehints import (
    TypeVar,
    Union,
    Any,
    Sequence,
    Tuple,
    List,
    Dict,
    Iterator,
    Bool,
    Vector,
    Matrix,
    RealVector,
    RealVectors,
)

_Indices = Sequence[Tuple[int, int, int]]


class _Vecs(ABC):
    def __init__(
        self, idxs1: _Indices, idxs2: _Indices, idxs3: _Indices
    ) -> None:
        self.vecs = tuple(
            tuple(
                tuple(
                    (
                        SPECIAL_COMPONENTS[idx]
                        if idx >= 0
                        else -SPECIAL_COMPONENTS[-idx]
                    )
                    for idx in idxs
                )
                for idxs in arr_idxs
            )
            for arr_idxs in (idxs1, idxs2, idxs3)
        )

    @abstractmethod
    def symm_elems(
        self, ax1: Vector, ax2: Vector, ax3: Vector, suffix: str
    ) -> Iterator[SymmetryElement]:
        pass


class _VecsT(_Vecs):
    def symm_elems(
        self, ax1: Vector, ax2: Vector, ax3: Vector, suffix: str
    ) -> Iterator[SymmetryElement]:
        diag = suffix == "d"
        horiz = suffix == "h"
        for vec in self.vecs[0]:
            vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
            yield RotationAxis(vec, 3)
            if horiz:
                yield RotoreflectionAxis(vec, 6)
        for vec in self.vecs[1]:
            vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
            yield RotationAxis(vec, 2)
            if diag:
                yield RotoreflectionAxis(vec, 4)
            elif horiz:
                yield ReflectionPlane(vec)
        if diag:
            for vec in self.vecs[2]:
                vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
                yield ReflectionPlane(vec)


class _VecsO(_Vecs):
    def symm_elems(
        self, ax1: Vector, ax2: Vector, ax3: Vector, suffix: str
    ) -> Iterator[SymmetryElement]:
        horiz = suffix == "h"
        for vec in self.vecs[0]:
            vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
            yield RotationAxis(vec, 4)
            if horiz:
                yield RotoreflectionAxis(vec, 4)
                yield ReflectionPlane(vec)
        for vec in self.vecs[1]:
            vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
            yield RotationAxis(vec, 3)
            if horiz:
                yield RotoreflectionAxis(vec, 6)
        for vec in self.vecs[2]:
            vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
            yield RotationAxis(vec, 2)
            if horiz:
                yield ReflectionPlane(vec)


class _VecsI(_Vecs):
    def symm_elems(
        self, ax1: Vector, ax2: Vector, ax3: Vector, suffix: str
    ) -> Iterator[SymmetryElement]:
        horiz = suffix == "h"
        for vec in self.vecs[0]:
            vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
            yield RotationAxis(vec, 5)
            if horiz:
                yield RotoreflectionAxis(vec, 10)
        for vec in self.vecs[1]:
            vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
            yield RotationAxis(vec, 3)
            if horiz:
                yield RotoreflectionAxis(vec, 6)
        for vec in self.vecs[2]:
            vec = vec[0] * ax1 + vec[1] * ax2 + vec[2] * ax3
            yield RotationAxis(vec, 2)
            if horiz:
                yield ReflectionPlane(vec)


_T_ROT3_IDXS_0 = (
    (41, 41, 41),
    (41, 41, -41),
    (41, -41, 41),
    (-41, 41, 41),
)
_T_ROT2_IDXS_0 = (
    (79, 0, 0),
    (0, 79, 0),
    (0, 0, 79),
)
_TD_REFL_IDXS_0 = (
    (53, 53, 0),
    (53, 0, 53),
    (0, 53, 53),
    (53, -53, 0),
    (53, 0, -53),
    (0, 53, -53),
)
_T_ROT3_IDXS_1 = (
    (79, 0, 0),
    (24, 74, 0),
    (24, -33, 63),
    (-24, 33, 63),
)
_T_ROT2_IDXS_1 = (
    (41, -63, 0),
    (41, 29, 53),
    (41, 29, -53),
)
_TD_REFL_IDXS_1 = (
    (63, 41, 0),
    (63, -20, 36),
    (-63, 20, 36),
    (0, 66, 36),
    (0, 66, -36),
    (0, 0, 79),
)
_T_VECS = (
    _VecsT(_T_ROT3_IDXS_0, _T_ROT2_IDXS_0, _TD_REFL_IDXS_0),
    _VecsT(_T_ROT3_IDXS_1, _T_ROT2_IDXS_1, _TD_REFL_IDXS_1),
)
_O_VECS = (
    _VecsO(_T_ROT2_IDXS_0, _T_ROT3_IDXS_0, _TD_REFL_IDXS_0),
    _VecsO(_T_ROT2_IDXS_1, _T_ROT3_IDXS_1, _TD_REFL_IDXS_1),
    _VecsO(
        (
            (79, 0, 0),
            (0, 53, 53),
            (0, 53, -53),
        ),
        (
            (41, 63, 0),
            (41, 0, 63),
            (41, -63, 0),
            (41, 0, -63),
        ),
        (
            (0, 79, 0),
            (0, 0, 79),
            (53, 36, 36),
            (53, 36, -36),
            (53, -36, 36),
            (-53, 36, 36),
        ),
    ),
)
_I_VECS = (
    _VecsI(
        (
            (64, 37, 0),
            (37, 0, 64),
            (0, 64, 37),
            (64, -37, 0),
            (-37, 0, 64),
            (0, 64, -37),
        ),
        _T_ROT3_IDXS_0
        + (
            (26, 73, 0),
            (73, 0, 26),
            (0, 26, 73),
            (26, -73, 0),
            (-73, 0, 26),
            (0, 26, -73),
        ),
        _T_ROT2_IDXS_0
        + (
            (62, 22, 36),
            (62, 22, -36),
            (62, -22, 36),
            (-62, 22, 36),
            (36, 62, 22),
            (36, 62, -22),
            (36, -62, 22),
            (-36, 62, 22),
            (22, 36, 62),
            (22, 36, -62),
            (22, -36, 62),
            (-22, 36, 62),
        ),
    ),
    _VecsI(
        (
            (61, 39, -14),
            (61, -2, 44),
            (-61, 34, 27),
            (11, 58, 44),
            (11, 7, -76),
            (11, -70, 27),
        ),
        _T_ROT3_IDXS_1
        + (
            (56, 38, 29),
            (56, 3, -49),
            (56, -47, 16),
            (24, 15, 71),
            (24, 51, -49),
            (-24, 69, 16),
        ),
        _T_ROT2_IDXS_1
        + (
            (73, 19, 13),
            (73, 1, -25),
            (73, -23, 8),
            (41, 59, 13),
            (41, -42, 40),
            (-41, 12, 60),
            (26, 65, -25),
            (26, -5, 72),
            (-26, 55, 40),
            (0, 78, 8),
            (0, 28, 72),
            (0, 46, -60),
        ),
    ),
    _VecsI(
        (
            (79, 0, 0),
            (31, 68, 0),
            (31, 18, 64),
            (31, 18, -64),
            (31, -54, 37),
            (-31, 54, 37),
        ),
        (
            (61, -45, 0),
            (61, 35, 26),
            (61, 35, -26),
            (61, -11, 41),
            (-61, 11, 41),
            (11, -77, 0),
            (11, 61, 41),
            (11, 61, -41),
            (11, -21, 73),
            (-11, 21, 73),
        ),
        (
            (64, 37, 0),
            (64, 9, 36),
            (64, 9, -36),
            (64, -30, 22),
            (-64, 30, 22),
            (37, -64, 0),
            (37, 52, 36),
            (37, 52, -36),
            (37, -17, 62),
            (-37, 17, 62),
            (0, 43, 62),
            (0, 43, -62),
            (0, 75, 22),
            (0, -75, 22),
            (0, 0, 79),
        ),
    ),
    _VecsI(
        (
            (61, 21, 37),
            (61, 21, -37),
            (61, -45, 0),
            (11, 77, 0),
            (11, -35, 64),
            (-11, 35, 64),
        ),
        (
            (79, 0, 0),
            (56, 50, 0),
            (56, -24, 41),
            (-56, 24, 41),
            (24, 56, 41),
            (24, 56, -41),
            (24, -67, 26),
            (-24, 67, 26),
            (24, 6, -73),
            (24, 6, 73),
        ),
        (
            (73, 26, 0),
            (73, -10, 22),
            (-73, 10, 22),
            (41, 57, 22),
            (41, 57, -22),
            (41, -48, 36),
            (-41, 48, 36),
            (41, -4, 62),
            (-41, 4, 62),
            (26, -73, 0),
            (26, 32, 62),
            (26, 32, -62),
            (0, 66, 36),
            (0, 66, -36),
            (0, 0, 79),
        ),
    ),
)
_VARIANTS: Dict[
    Tuple[int, int],
    Dict[float, Tuple[Tuple[_Vecs, Tuple[int, int, int]], ...]],
] = {
    (5, 5): {SPECIAL_ANGLES[11]: ((_I_VECS[2], (0, 1, 2)),)},
    (5, 3): {
        SPECIAL_ANGLES[5]: ((_I_VECS[2], (0, -1, 2)),),
        SPECIAL_ANGLES[15]: ((_I_VECS[2], (0, -1, 2)),),
    },
    (5, 2): {
        SPECIAL_ANGLES[2]: ((_I_VECS[2], (0, 1, 2)),),
        SPECIAL_ANGLES[9]: ((_I_VECS[2], (0, -1, 2)),),
        SPECIAL_ANGLES[16]: ((_I_VECS[1], (0, 2, 1)),),
    },
    (4, 4): {SPECIAL_ANGLES[16]: ((_O_VECS[0], (0, 1, 2)),)},
    (4, 3): {SPECIAL_ANGLES[8]: ((_O_VECS[2], (0, 1, 2)),)},
    (4, 2): {
        SPECIAL_ANGLES[7]: ((_O_VECS[0], (0, 1, 2)),),
        SPECIAL_ANGLES[16]: ((_O_VECS[2], (0, 1, 2)),),
    },
    (3, 3): {
        SPECIAL_ANGLES[6]: ((_I_VECS[3], (0, 1, 2)),),
        SPECIAL_ANGLES[13]: (
            (_I_VECS[1], (0, 1, 2)),
            (_O_VECS[1], (0, 1, 2)),
            (_T_VECS[1], (0, 1, 2)),
        ),
    },
    (3, 2): {
        SPECIAL_ANGLES[1]: ((_I_VECS[3], (0, 1, 2)),),
        SPECIAL_ANGLES[3]: ((_O_VECS[1], (0, 1, 2)),),
        SPECIAL_ANGLES[8]: (
            (_I_VECS[1], (0, -1, 2)),
            (_T_VECS[1], (0, -1, 2)),
        ),
        SPECIAL_ANGLES[12]: ((_I_VECS[3], (0, -1, 2)),),
        SPECIAL_ANGLES[16]: (
            (_I_VECS[3], (0, 2, -1)),
            (_O_VECS[1], (0, 2, -1)),
        ),
    },
    (2, 2): {
        SPECIAL_ANGLES[4]: ((_I_VECS[2], (2, 1, 0)),),
        SPECIAL_ANGLES[10]: (
            (_I_VECS[3], (2, 1, 0)),
            (_O_VECS[0], (0, 1, 2)),
        ),
        SPECIAL_ANGLES[14]: ((_I_VECS[2], (2, -1, 0)),),
        SPECIAL_ANGLES[16]: (
            (_I_VECS[0], (0, 1, 2)),
            (_O_VECS[2], (2, 0, 1)),
            (_T_VECS[0], (0, 1, 2)),
        ),
    },
}


class Point(VectorTransformable):
    """Point in a real 3D space."""

    @property
    def pos(self) -> Vector:
        """Return the position."""
        return self._vec


class LabeledPoint(Point):
    """Labeled point in a real 3D space."""

    def __init__(self, vec: RealVector, label: str) -> None:
        """
        Initialize the instance with a 3D vector `vec` and a label `label`.
        """
        super().__init__(vec)
        self._label = label

    @property
    def label(self) -> str:
        """Return the label."""
        return self._label

    @property
    def args(self):
        label = self._label.replace("'", r"\'")
        return f"{super().args},'{label}'"

    @property
    def props(self) -> Tuple:
        return super().props + (self._label,)


_Points = TypeVar("_Points", bound="Points")


class Points(Transformables):
    """Set of points."""

    _elems: Tuple[Point, ...] = ()

    def __init__(self, points: Sequence[Point]) -> None:
        """Initialize the instance with a set of points `points`."""
        super().__init__(points)

    @property
    def elems(self) -> Tuple[Point, ...]:
        """Return the set of elements."""
        return self._elems

    @property
    def pos(self) -> Vector:
        """Return the centroid of the points."""
        centroid = zeros(3)
        n = 0
        for elem in self._elems:
            centroid += elem.pos
            n += 1
        if n > 0:
            centroid /= n
        return centroid

    def __getitem__(self, item: int) -> Point:
        return self._elems[item]

    def __add__(self, other: "Points") -> "Points":
        """Return the union of the instance with a set of points `other`."""
        return type(self)(self._elems + other.elems)

    def center(self: _Points) -> _Points:
        """Center the points at the origin."""
        return self.translate(Translation(-self.pos))

    @property
    def inertia(self) -> Matrix:
        """Return the inertia tensor of the points of unit mass."""
        centroid = self.pos
        return inertia(tuple(elem.pos - centroid for elem in self._elems))

    def symm_elems(
        self, tol: float = TOL, fast: bool = True
    ) -> Iterator[SymmetryElement]:
        """
        Determine all symmetry elements of a set of points `points` within a
        tolerance `tol`. Use the fast algorithm if `fast` is `True`.
        """
        if not self.nondegen(tol):
            raise ValueError(
                "at least two identical elements in the instance of for the"
                + " given tolerance"
            )
        points = self.center()
        poses = tuple(elem.pos for elem in points._elems)

        center = InversionCenter()
        invertible = center.symmetric(points, tol)
        if invertible:
            yield center
        n_points = len(poses)

        if n_points == 1:
            yield CenterRotationAxes()
            yield CenterReflectionPlanes()
            yield CenterRotoreflectionAxes()
            return

        for i in range(n_points):
            pos = poses[i]
            if not zero(pos, tol):
                axis = pos
                break
        for i in range(i + 1, n_points):
            if not parallel(axis, poses[i], tol):
                break
        else:
            yield InfRotationAxis(axis)
            yield AxisReflectionPlanes(axis)
            if invertible:
                yield AxisRotationAxes(axis)
                yield ReflectionPlane(axis)
                yield InfRotoreflectionAxis(axis)
            return

        axes: List[Vector] = []
        normals: List[Vector] = []
        eigvals, eigvecs = eigh(inertia(poses))
        oblate = eigvals[1] - eigvals[0] <= tol
        prolate = eigvals[2] - eigvals[1] <= tol
        coplanar = False
        cubic = False
        if oblate and prolate:
            cubic = True
        elif oblate or prolate:
            vec = eigvecs[:, 2] if oblate else eigvecs[:, 0]
            axes.append(vec)
            coplanar = True
            orders = set()
            for _, idxs in points._groups:
                dists: Dict[float, int] = {}
                n_points = len(idxs)
                for i in range(n_points):
                    pos = poses[idxs[i]]
                    dist = pos.dot(vec)
                    if coplanar and dist > tol:
                        coplanar = False
                    for ref_dist in dists:
                        if abs(dist - ref_dist) <= tol:
                            dists[ref_dist] += 1
                            break
                    else:
                        dists[dist] = 1
                for count in dists.values():
                    orders.add(count)
            ref_orders = sorted(orders, reverse=True)
            for order in range(ref_orders[0], 1, -1):
                for ref_order in ref_orders:
                    if ref_order % order != 0 and (ref_order - 1) % order != 0:
                        break
                else:
                    rot = RotationAxis(vec, order)
                    if rot.symmetric(points, tol):
                        yield rot
                        max_order = order
                        if not coplanar:
                            for factor in (2, 1):
                                new_order = order * factor
                                if new_order > 2:
                                    rotorefl = RotoreflectionAxis(
                                        vec, new_order
                                    )
                                    if rotorefl.symmetric(points, tol):
                                        yield rotorefl
                                        break
                        elif order > 2:
                            yield RotoreflectionAxis(vec, order)
                        break
            normals.append(vec)
            refl = ReflectionPlane(vec)
            if coplanar or refl.symmetric(points, tol):
                yield refl
        else:
            curr_rot = False
            curr_refl = False
            for i in range(3):
                prev_rot = curr_rot
                prev_refl = curr_refl
                curr_rot = False
                curr_refl = False
                vec = eigvecs[:, i]
                rot = RotationAxis(vec, 2)
                if rot.symmetric(points, tol):
                    yield rot
                    curr_rot = True
                refl = ReflectionPlane(vec)
                if (invertible and curr_rot) or refl.symmetric(points, tol):
                    yield refl
                    curr_refl = True
                if i == 1:
                    vec = eigvecs[:, 2]
                    if prev_rot and prev_refl:
                        if curr_rot and curr_refl:
                            yield RotationAxis(vec, 2)
                            yield ReflectionPlane(vec)
                    elif prev_rot:
                        if curr_rot:
                            yield RotationAxis(vec, 2)
                        elif curr_refl:
                            yield ReflectionPlane(vec)
                    elif prev_refl:
                        if curr_rot:
                            yield ReflectionPlane(vec)
                        elif curr_refl:
                            yield RotationAxis(vec, 2)
                    elif not (curr_rot or curr_refl):
                        continue
                    break
            return

        def new(arr: List[Vector], vec: Vector) -> bool:
            for elem in arr:
                if unitparallel(elem, vec, tol):
                    return False
            arr.append(vec)
            return True

        def high_symm_elems(
            idxs: Tuple[int, ...]
        ) -> Iterator[Union[RotationAxis, RotoreflectionAxis]]:
            n_points = len(idxs)
            collinear_part = False
            coplanar_part = False
            for i1 in range(n_points - 2):
                pos1 = poses[idxs[i1]]
                for i2 in range(i1 + 1, n_points - 1):
                    pos2 = poses[idxs[i2]]
                    segment = pos1 - pos2
                    if i2 == 1:
                        collinear_part = True
                    for i3 in range(i2 + 1, n_points):
                        pos3 = poses[idxs[i3]]
                        normal = cross(segment, pos1 - pos3)
                        normal_norm = norm(normal)
                        if normal_norm <= tol:
                            continue
                        axis = normal / normal_norm
                        collinear_part = False
                        if new(axes, axis):
                            dist = pos1.dot(axis)
                            max_order = 3
                            for i4 in range(n_points):
                                if i4 == i1 or i4 == i2 or i4 == i3:
                                    continue
                                pos4 = poses[idxs[i4]]
                                if abs(pos4.dot(axis) - dist) <= tol:
                                    max_order += 1
                            if i3 == 2 and max_order == n_points:
                                coplanar_part = True
                            for order in range(max_order, 1, -1):
                                if (
                                    max_order % order != 0
                                    and (max_order - 1) % order != 0
                                ):
                                    continue
                                rot = RotationAxis(axis, order)
                                if rot.symmetric(points, tol):
                                    yield rot
                                    if not fast:
                                        for factor in (2, 1):
                                            new_order = order * factor
                                            if new_order > 2:
                                                rotorefl = RotoreflectionAxis(
                                                    axis, new_order
                                                )
                                                if rotorefl.symmetric(
                                                    points, tol
                                                ):
                                                    yield rotorefl
                                                    break
                                    break
                    if collinear_part or coplanar_part:
                        break
                else:
                    continue
                break

        def low_symm_elems(
            idxs: Tuple[int, ...]
        ) -> Iterator[
            Union[RotationAxis, RotoreflectionAxis, ReflectionPlane]
        ]:
            n_points = len(idxs)
            for i1 in range(n_points - 1):
                pos1 = poses[idxs[i1]]
                for i2 in range(i1 + 1, n_points):
                    pos2 = poses[idxs[i2]]
                    segment = pos1 - pos2
                    midpoint = 0.5 * (pos1 + pos2)
                    if not perpendicular(segment, midpoint, tol):
                        continue
                    midpoint_norm = norm(midpoint)
                    nonzero = midpoint_norm > tol
                    if nonzero or coplanar:
                        axis = (
                            midpoint / midpoint_norm
                            if nonzero
                            else normalize(cross(segment, normals[0]))
                        )
                        if (
                            cubic or perpendicular(axis, axes[0], tol)
                        ) and new(axes, axis):
                            rot = RotationAxis(axis, 2)
                            if rot.symmetric(points, tol):
                                yield rot
                                if not fast:
                                    rotorefl = RotoreflectionAxis(axis, 4)
                                    if rotorefl.symmetric(points, tol):
                                        yield rotorefl
                    normal = normalize(segment)
                    if (cubic or perpendicular(normal, axes[0], tol)) and new(
                        normals, normal
                    ):
                        refl = ReflectionPlane(normal)
                        if refl.symmetric(points, tol):
                            yield refl

        generator: Iterator[SymmetryElement]
        for _, idxs in points._groups:
            if fast:
                if cubic:
                    generator = high_symm_elems(idxs)
                    rot1 = next(generator)
                    vec1 = rot1.vec
                    order1 = rot1.order
                    rot2 = next(generator)
                    vec2 = rot2.vec
                    order2 = rot2.order
                    if order1 < order2:
                        vec1, vec2 = vec2, vec1
                        order1, order2 = order2, order1
                    if vec1.dot(vec2) < 0.0:
                        vec2 = -vec2
                    original_axes = [
                        vec1,
                        normalize(orthogonalize(vec2, vec1)),
                    ]
                    original_axes.append(
                        normalize(cross(original_axes[0], original_axes[1]))
                    )
                    ang = angle(vec1, vec2)
                    min_diff = INF
                    for ref_ang, ref_variants in _VARIANTS[
                        (order1, order2)
                    ].items():
                        diff = abs(ang - ref_ang)
                        if min_diff > diff:
                            min_diff = diff
                            variants = ref_variants
                    suffix = "h" if invertible else ""
                    n_variants = len(variants)
                    for i_variant in range(n_variants):
                        vecs_obj, axes_order = variants[i_variant]
                        permut_axes = tuple(
                            (
                                original_axes[i_axis]
                                if i_axis >= 0
                                else -original_axes[-i_axis]
                            )
                            for i_axis in axes_order
                        )
                        if suffix == "" and isinstance(vecs_obj, _VecsT):
                            vec = vecs_obj.vecs[1][0]
                            rotorefl = RotoreflectionAxis(
                                vec[0] * permut_axes[0]
                                + vec[1] * permut_axes[1]
                                + vec[2] * permut_axes[2],
                                4,
                            )
                            if rotorefl.symmetric(points, tol):
                                suffix = "d"
                        generator = vecs_obj.symm_elems(
                            permut_axes[0],
                            permut_axes[1],
                            permut_axes[2],
                            suffix,
                        )
                        if i_variant < n_variants - 1:
                            symm_elem = next(generator)
                            if symm_elem.symmetric(points, tol):
                                yield symm_elem
                                break
                    yield from generator
                else:
                    try:
                        symm_elem = next(low_symm_elems(idxs))
                    except StopIteration:
                        continue
                    yield symm_elem
                    axis = axes[0]
                    vec1 = normalize(orthogonalize(symm_elem.vec, axis))
                    vec2 = normalize(cross(axis, vec1))
                    ang = 0.0
                    step = PI / max_order
                    if isinstance(symm_elem, RotationAxis):
                        refl = ReflectionPlane(vec1)
                        vert = refl.symmetric(points, tol)
                        if vert:
                            yield refl
                        else:
                            half_step = 0.5 * step
                            refl = ReflectionPlane(
                                vec1 * cos(half_step) + vec2 * sin(half_step)
                            )
                            diag = refl.symmetric(points, tol)
                            if diag:
                                yield refl
                        for factor in range(1, max_order):
                            ang += step
                            new_vec = vec1 * cos(ang) + vec2 * sin(ang)
                            yield RotationAxis(new_vec, 2)
                            if vert:
                                yield ReflectionPlane(new_vec)
                            elif diag:
                                new_ang = ang + half_step
                                yield ReflectionPlane(
                                    vec1 * cos(new_ang) + vec2 * sin(new_ang)
                                )
                    elif isinstance(symm_elem, ReflectionPlane):
                        rot = RotationAxis(vec1, 2)
                        vert = rot.symmetric(points, tol)
                        if vert:
                            yield rot
                        else:
                            half_step = 0.5 * step
                            rot = RotationAxis(
                                vec1 * cos(half_step) + vec2 * sin(half_step),
                                2,
                            )
                            diag = rot.symmetric(points, tol)
                            if diag:
                                yield rot
                        for factor in range(1, max_order):
                            ang += step
                            new_vec = vec1 * cos(ang) + vec2 * sin(ang)
                            yield ReflectionPlane(new_vec)
                            if vert:
                                yield RotationAxis(new_vec, 2)
                            elif diag:
                                new_ang = ang + half_step
                                yield RotationAxis(
                                    vec1 * cos(new_ang) + vec2 * sin(new_ang),
                                    2,
                                )
            else:
                if cubic:
                    yield from high_symm_elems(idxs)
                yield from low_symm_elems(idxs)

    @classmethod
    def from_arr(cls, vecs: RealVectors) -> "Points":
        """Construct an instance from an array of 3D vectors `vecs`."""
        return cls(tuple(Point(vec) for vec in vecs))

    @classmethod
    def from_str(cls, string: str) -> "Points":
        """
        Construct an instance from a string `string`.  Each three consecutive
        floating-point numbers are parsed as a `Point` instance.  If they are
        preceded by a label satisfying the rules of variable names, a
        `LabeledPoint` instance is created instead.
        """
        points = []
        for match in findall(
            r"(?:({0})\s+)?({1})\s+({1})\s+({1})".format(LABEL_RE, FLOAT_RE),
            string,
        ):
            label = match[0]
            vec = tuple(map(float, match[1:]))
            points.append(LabeledPoint(vec, label) if label else Point(vec))
        return cls(points)

    @classmethod
    def from_symm(
        cls,
        base: Union[RealVectors, "Points"],
        symm_elems: Union[SymmetryElement, Sequence[SymmetryElement]],
    ) -> "Points":
        """
        Construct an instance by applying one or multiple symmetry elements
        `symm_elems` to an array of 3D point position vectors or a set of
        points `base`.
        """
        if isinstance(base, Points):
            points = list(base.elems)
        else:
            points = [Point(vec) for vec in base]
        if not isinstance(symm_elems, Sequence):
            symm_elems = (symm_elems,)
        for symm_elem in symm_elems:
            for i in range(len(points)):
                point = points[i]
                for transform in symm_elem.transforms:
                    points.append(transform(point))
        return cls(points)

    @classmethod
    def from_transform(
        cls,
        base: Union[RealVectors, "Points"],
        transforms: Union[Transformation, Sequence[Transformation]],
        tol: float,
    ) -> "Points":
        """
        Construct an instance by applying repeatedly one or multiple
        trnasfomations `transforms` to an array of 3D point position vectors or
        a set of points `base` and generating only unique points within a
        tolerance `tol`.
        """
        if isinstance(base, Points):
            points = list(base.elems)
        else:
            points = [Point(vec) for vec in base]
        if not isinstance(transforms, Sequence):
            transforms = (transforms,)
        fi = 0
        li = len(points)
        while fi < li:
            for transform in transforms:
                for i in range(fi, li):
                    point = transform(points[i])
                    for ref_point in points:
                        if point.same(ref_point, tol):
                            break
                    else:
                        points.append(point)
            fi = li
            li = len(points)
        return cls(points)


_Arrow = TypeVar("_Arrow", bound="Arrow")


class Arrow(DirectionTransformable):
    """Arrow in a real 3D space."""

    def __init__(self, vec: RealVector, fore: Bool, back: Bool) -> None:
        """
        Initialize the instance with a 3D non-zero vector `vec` and two
        arguments, `fore` and `back`, describing the types of its ends: `True`
        for head and `False` for tail. The direction of the vector corresponds
        the direction from the end described by `back` to the end described by
        `fore`. Possible combinations of `fore` and `back` are:
        - '<->' (two heads) for `True` and `True`,
        - '>->' (one head and one tail) for `True` and `False`,
        - '<-<' (one tail and one head) for `False` and `True`,
        - '>-<' (two tails) for `False` and `False`.
        """
        super().__init__(vec)
        if fore and back:
            self._form = 1
        elif not fore and not back:
            self._form = -1
        else:
            self._form = 0
            if back:
                self._vec = -self._vec

    @property
    def form(self) -> int:
        """
        Return the form: `1` for two heads ('<->'), `-1` for two tails ('>-<'),
        and `0` otherwise ('>->' or '<-<').
        """
        return self._form

    @property
    def args(self) -> str:
        if self._form == 1:
            fore = True
            back = True
        elif self._form == -1:
            fore = False
            back = False
        else:
            fore = True
            back = False
        return f"{super().args},{fore},{back}"

    @property
    def props(self) -> Tuple:
        return super().props + (self._form,)

    def diff(self, obj: Any) -> float:
        res = Transformable.diff(self, obj)
        if res < INF:
            if self._form == 0:
                res = max(res, diff(self._vec, obj.vec))
            else:
                res = max(res, unitindep(self._vec, obj.vec))
        return res

    def negate(self: _Arrow) -> _Arrow:
        res = self.copy()
        if self._form == 0:
            res._vec = -self._vec
        else:
            res._form = -self._form
        return res


_StructPoint = TypeVar("_StructPoint", bound="StructPoint")


class StructPoint(Point):
    """Point with a coefficient and a set of arrows."""

    def __init__(
        self, vec: RealVector, coef: float = 1.0, arrows: Sequence[Arrow] = ()
    ) -> None:
        """
        Initialize the instance with a 3D position vector `vec`, a non-zero
        coefficient `coef`, and a set of arrows `arrows`.
        """
        super().__init__(vec)
        if coef == 0.0:
            raise ValueError("zero coefficient")
        self._arrows = Transformables(arrows)
        if coef < 0.0:
            self._arrows = self._arrows.negate()
        self._coef = abs(coef)

    @property
    def coef(self) -> float:
        """Return the coefficient."""
        return self._coef

    @property
    def arrows(self) -> Transformables:
        """Return the set of arrows."""
        return self._arrows

    @property
    def args(self) -> str:
        return f"{super().args},{self._coef},{self._arrows.args}"

    @property
    def props(self) -> Tuple:
        return super().props + self._arrows.props

    def diff(self, obj: Any) -> float:
        res = super().diff(obj)
        if res < INF:
            res = max(
                res, abs(self._coef - obj.coef), self._arrows.diff(obj.arrows)
            )
        return res

    def negate(self: _StructPoint) -> _StructPoint:
        res = super().negate()
        res._arrows = self._arrows.negate()
        return res

    def invert(self: _StructPoint) -> _StructPoint:
        res = super().invert()
        res._arrows = self._arrows.invert()
        return res

    def rotate(self: _StructPoint, rot: Rotation) -> _StructPoint:
        res = super().rotate(rot)
        res._arrows = self._arrows.rotate(rot)
        return res

    def reflect(self: _StructPoint, refl: Reflection) -> _StructPoint:
        res = super().reflect(refl)
        res._arrows = self._arrows.reflect(refl)
        return res

    def rotoreflect(
        self: _StructPoint, rotorefl: Rotoreflection
    ) -> _StructPoint:
        res = super().rotoreflect(rotorefl)
        res._arrows = self._arrows.rotoreflect(rotorefl)
        return res
