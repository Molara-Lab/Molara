"""Classes for symmetry elements in a real 3D space."""

__all__ = [
    "SymmetryElement",
    "IdentityElement",
    "InversionCenter",
    "RotationAxis",
    "InfRotationAxis",
    "ReflectionPlane",
    "RotoreflectionAxis",
    "InfRotoreflectionAxis",
    "AxisRotationAxes",
    "CenterRotationAxes",
    "AxisReflectionPlanes",
    "CenterReflectionPlanes",
    "CenterRotoreflectionAxes",
    "SymmetryElements",
]

from abc import ABC, abstractmethod

from .const import PI, TAU, SYMB, SPECIAL_ANGLES
from .vecop import intersectangle
from .tools import rational
from .transform import (
    Transformable,
    Transformables,
    InvariantTransformable,
    DirectionTransformable,
    OrderedTransformable,
    InfFoldTransformable,
    Transformation,
    Inversion,
    Rotation,
    Reflection,
    Rotoreflection,
)
from .typehints import (
    Union,
    TypeVar,
    Sequence,
    Tuple,
    List,
    Dict,
    Iterator,
    Int,
    RealVector,
)

_Transformable = TypeVar("_Transformable", bound=Transformable)


class SymmetryElement(ABC):
    """Symmetry element."""

    _symb = ""
    _name = ""
    _id = 0
    label = ""

    @property
    @abstractmethod
    def props(self) -> Tuple:
        pass

    @property
    @abstractmethod
    def transforms(self) -> Iterator[Transformation]:
        """Return the transformations."""
        pass

    @property
    def symb(self) -> str:
        """Return the symbol."""
        return self._symb

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def id(self) -> int:
        """Return the ID."""
        return self._id

    def __iter__(self) -> Iterator[Transformation]:
        return self.transforms

    def symmetric(self, transformables: Transformables, tol: float) -> bool:
        """
        Check whether a set of transformables `transformables` is symmetric
        within a tolerance `tol`.
        """
        for transform in self.transforms:
            if not transformables.same(transform(transformables), tol):
                return False
        return True

    def __call__(
        self, transformable: _Transformable
    ) -> Sequence[_Transformable]:
        """Apply the transformations."""
        return (transformable,) + tuple(
            transform(transformable) for transform in self.transforms
        )


class InfSymmetryElement(SymmetryElement):
    """Symmetry element with an infinite number of transformations."""

    @property
    def transforms(self) -> Iterator[Transformation]:
        raise NotImplementedError("infinite number of transformations")


class IdentityElement(InvariantTransformable, SymmetryElement):
    """Identity element in a real 3D space."""

    _symb = "E"
    _name = "identity element"
    _id = 1

    @property
    def transforms(self) -> Iterator[Transformation]:
        return iter(())


class InversionCenter(InvariantTransformable, SymmetryElement):
    """Inversion center in the origin in a real 3D space."""

    _symb = "i"
    _name = "inversion center"
    _id = -2

    @property
    def transforms(self) -> Iterator[Transformation]:
        yield Inversion()


class RotationAxis(OrderedTransformable, SymmetryElement):
    """Rotation axis containing the origin in a real 3D space."""

    _symb = SYMB.rot
    _name = "rotation axis"

    def __init__(self, vec: RealVector, order: Int) -> None:
        """
        Initialize the instance with a 3D non-zero vector `vec` and a positive
        order `order` greater than 1.
        """
        super().__init__(vec, order)
        if order == 1:
            raise ValueError(
                "a 1-fold rotation axis is identical to an identity element"
            )
        order_str = str(order)
        self._symb += order_str
        self._name = order_str + "-fold " + self._name
        self._id = self._order

    @property
    def transforms(self) -> Iterator[Transformation]:
        for i in range(1, self._order):
            yield Rotation(self._vec, i / self._order * TAU)


class InfRotationAxis(InfFoldTransformable, InfSymmetryElement):
    """Infinite-fold rotation axis containing the origin in a real 3D space."""

    _symb = SYMB.rot + SYMB.inf
    _name = "infinite-fold rotation axis"


class ReflectionPlane(DirectionTransformable, SymmetryElement):
    """Reflection plane containing the origin in a real 3D space."""

    _symb = SYMB.refl
    _name = "reflection plane"
    _id = -1

    @property
    def transforms(self) -> Iterator[Transformation]:
        yield Reflection(self._vec)


class RotoreflectionAxis(OrderedTransformable, SymmetryElement):
    """Rotoreflection axis containing the origin in a real 3D space."""

    _symb = SYMB.rotorefl
    _name = "rotoreflection axis"

    def __init__(self, vec: RealVector, order: Int) -> None:
        """
        Initialize the instance with a 3D non-zero vector `vec` and a positive
        order `order` greater than 2.
        """
        super().__init__(vec, order)
        if order == 1:
            raise ValueError(
                "a 1-fold rotoreflection axis is identical to a reflection"
                + " plane"
            )
        elif order == 2:
            raise ValueError(
                "a 2-fold rotoreflection axis is identical to an inversion"
                + " center"
            )
        order_str = str(order)
        self._symb += order_str
        self._name = order_str + "-fold " + self._name
        self._id = -self._order

    @property
    def transforms(self) -> Iterator[Transformation]:
        for i in range(1, self._order * (1 if self._order % 2 == 0 else 2)):
            if i != self._order:
                angle = (i % self._order) / self._order * TAU
                if i % 2 == 0:
                    yield Rotation(self._vec, angle)
                else:
                    if 2 * i != self._order:
                        yield Rotoreflection(self._vec, angle)
                    else:
                        yield Inversion()
            else:
                yield Reflection(self._vec)


class InfRotoreflectionAxis(InfFoldTransformable, InfSymmetryElement):
    """
    Infinite-fold rotoreflaction axis containing the origin in a real 3D space.
    """

    _symb = SYMB.rotorefl + SYMB.inf
    _name = "infinite-fold rotoreflection axis"


class AxisRotationAxes(DirectionTransformable, InfSymmetryElement):
    """
    All two-fold rotation axes perpendicular to an infinite-fold rotation axis
    containing the origin in a real 3D space.
    """

    _symb = SYMB.inf + SYMB.rot + "2"
    _name = "set of all two-fold rotation axes perpendicular to an axis"
    _id = 2


class CenterRotationAxes(InvariantTransformable, InfSymmetryElement):
    """
    All infinite-fold rotation axes containing the origin as an invariant
    center in a real 3D space.
    """

    _symb = SYMB.inf + SYMB.rot + SYMB.inf
    _name = "set of all infinite-fold rotation axes containing a center"


class AxisReflectionPlanes(DirectionTransformable, InfSymmetryElement):
    """
    All reflection planes containing an infinite-fold rotation axis and the
    origin in a real 3D space.
    """

    _symb = SYMB.inf + SYMB.refl + "v"
    _name = "set of all reflection planes containing an axis"
    _id = -1


class CenterReflectionPlanes(InvariantTransformable, InfSymmetryElement):
    """
    All reflection planes containing the origin as an invariant center in a
    real 3D space.
    """

    _symb = SYMB.inf + SYMB.refl
    _name = "set of all reflection planes containing a center"
    _id = -1


class CenterRotoreflectionAxes(InvariantTransformable, InfSymmetryElement):
    """
    All infinite-fold rotoreflection axes containing the origin as an invariant
    center in a real 3D space.
    """

    _symb = SYMB.inf + SYMB.rotorefl + SYMB.inf
    _name = "set of all infinite-fold rotoreflection axes containing a center"


_DirectionSymmetryElement = Union[
    RotationAxis,
    InfRotationAxis,
    ReflectionPlane,
    RotoreflectionAxis,
    InfRotoreflectionAxis,
    AxisRotationAxes,
    AxisReflectionPlanes,
]
_DirectionSymmetryElements = (
    RotationAxis,
    InfRotationAxis,
    ReflectionPlane,
    RotoreflectionAxis,
    InfRotoreflectionAxis,
    AxisRotationAxes,
    AxisReflectionPlanes,
)
_SYMM_ELEM_ORDER = (
    RotoreflectionAxis,
    InfRotoreflectionAxis,
    CenterRotoreflectionAxes,
    InversionCenter,
    ReflectionPlane,
    AxisReflectionPlanes,
    CenterReflectionPlanes,
    AxisRotationAxes,
    RotationAxis,
    InfRotationAxis,
    CenterRotationAxes,
)


def _prop2rank(prop: Tuple) -> Tuple:
    """
    Calculate the ordering rank of a symmetry element by using its properties.
    """
    rank: Tuple = (_SYMM_ELEM_ORDER.index(prop[0]),)
    if len(prop) > 1:
        rank += (prop[1],)
    return rank


class SymmetryElements:
    """
    Set of symmetry elements containing numbers of their types and of the
    angles between their axes or normals.
    """

    def __init__(self) -> None:
        """Initialize the instance."""
        self._included: List[_DirectionSymmetryElement] = []
        self._excluded: List[_DirectionSymmetryElement] = []
        self._nums: Dict[Tuple, int] = {}
        self._angles: Dict[Tuple[Tuple, Tuple], Dict[float, int]] = {}

    @property
    def included(self) -> Sequence[_DirectionSymmetryElement]:
        """Return the included symmetry elements containing a direction."""
        return tuple(self._included)

    @property
    def excluded(self) -> Sequence[_DirectionSymmetryElement]:
        """Return the excluded symmetry elements containing a direction."""
        return tuple(self._excluded)

    @property
    def nums(self) -> Dict[Tuple, int]:
        """Return the types and numbers of symmetry elements."""
        return self._nums.copy()

    @property
    def angles(
        self,
    ) -> Dict[Tuple[Tuple, Tuple], Dict[float, int]]:
        """Return the angles between axes or normals of symmetry elements."""
        return {props: angles.copy() for props, angles in self._angles.items()}

    def include(
        self,
        symm_elems: Union[SymmetryElement, Sequence[SymmetryElement]],
        tol: float,
    ) -> None:
        """
        Include information of one or multiple symmetry elements `symm_elems`
        using a tolerance `tol` to calculate exact intersection angles.
        """
        if not isinstance(symm_elems, Sequence):
            symm_elems = (symm_elems,)
        for symm_elem1 in symm_elems:
            prop1 = symm_elem1.props
            rank1 = _prop2rank(prop1)
            if isinstance(symm_elem1, _DirectionSymmetryElements):
                if prop1 not in self._nums:
                    self._nums[prop1] = 0
                self._nums[prop1] += 1
                vec1 = symm_elem1.vec
                for symm_elem2 in self._included:
                    prop2 = symm_elem2.props
                    vec2 = symm_elem2.vec
                    angle = intersectangle(vec1, vec2)
                    for special_angle in SPECIAL_ANGLES:
                        diff = abs(angle - special_angle)
                        if diff <= tol:
                            angle = special_angle
                            break
                    else:
                        nom, denom = rational(angle / PI, tol)
                        angle = nom * PI / denom
                    if angle == 0.0 and symm_elem1.similar(symm_elem2):
                        raise ValueError(
                            f"a parallel {symm_elem1.name} already included"
                        )
                    props = (
                        (prop1, prop2)
                        if rank1 >= _prop2rank(prop2)
                        else (prop2, prop1)
                    )
                    if props not in self._angles:
                        self._angles[props] = {}
                    if angle not in self._angles[props]:
                        self._angles[props][angle] = 0
                    elif self._angles[props][angle] == 0:
                        raise ValueError(
                            f"the excluded angle of {angle} between"
                            + f" a {symm_elem1.name} and a {symm_elem2.name}"
                            + " cannot be included"
                        )
                    self._angles[props][angle] += 1
                for symm_elem2 in self._excluded:
                    prop2 = symm_elem2.props
                    vec2 = symm_elem2.vec
                    angle = intersectangle(vec1, vec2)
                    if angle > tol:
                        continue
                    angle = 0.0
                    if symm_elem1.similar(symm_elem2):
                        raise ValueError(
                            f"the excluded parallel {symm_elem1.name} cannot"
                            + " be included"
                        )
                    props = (
                        (prop1, prop2)
                        if rank1 >= _prop2rank(prop2)
                        else (prop2, prop1)
                    )
                    if props not in self._angles:
                        self._angles[props] = {}
                    if (
                        angle in self._angles[props]
                        and self._angles[props][angle] > 0
                    ):
                        raise ValueError(
                            f"the included angle of {angle} between"
                            + f" a {symm_elem1.name} and a {symm_elem2.name}"
                            + " cannot be excluded"
                        )
                    self._angles[props][angle] = 0
                self._included.append(symm_elem1)
            else:
                if prop1 in self._nums:
                    raise ValueError(
                        f"an {symm_elem1.name} already "
                        + (
                            "included"
                            if self._nums[prop1] == 1
                            else "excluded"
                        )
                    )
                self._nums[prop1] = 1

    def exclude(
        self,
        symm_elems: Union[SymmetryElement, Sequence[SymmetryElement]],
        tol: float,
    ) -> None:
        """
        Exclude information of one or multiple symmetry elements `symm_elems`
        using a tolerance `tol` to calculate exact intersection angles.
        """
        if not isinstance(symm_elems, Sequence):
            symm_elems = (symm_elems,)
        for symm_elem1 in symm_elems:
            prop1 = symm_elem1.props
            rank1 = _prop2rank(prop1)
            if isinstance(symm_elem1, _DirectionSymmetryElements):
                vec1 = symm_elem1.vec
                for symm_elem2 in self._included:
                    prop2 = symm_elem2.props
                    vec2 = symm_elem2.vec
                    angle = intersectangle(vec1, vec2)
                    if angle > tol:
                        continue
                    angle = 0.0
                    if symm_elem1.similar(symm_elem2):
                        raise ValueError(
                            f"the included parallel {symm_elem1.name} cannot"
                            + " be excluded"
                        )
                    props = (
                        (prop1, prop2)
                        if rank1 >= _prop2rank(prop2)
                        else (prop2, prop1)
                    )
                    if props not in self._angles:
                        self._angles[props] = {}
                    if (
                        angle in self._angles[props]
                        and self._angles[props][angle] > 0
                    ):
                        raise ValueError(
                            f"the included angle of {angle} between"
                            + f" a {symm_elem1.name} and a {symm_elem2.name}"
                            + " cannot be excluded"
                        )
                    self._angles[props][angle] = 0
                for symm_elem2 in self._excluded:
                    prop2 = symm_elem2.props
                    vec2 = symm_elem2.vec
                    angle = intersectangle(vec1, vec2)
                    if angle <= tol and symm_elem1.similar(symm_elem2):
                        raise ValueError(
                            f"a parallel {symm_elem1.name} already excluded"
                        )
                self._excluded.append(symm_elem1)
            else:
                if prop1 in self._nums:
                    raise ValueError(
                        f"an {symm_elem1.name} already "
                        + (
                            "included"
                            if self._nums[prop1] == 1
                            else "excluded"
                        )
                    )
                self._nums[prop1] = 0

    def contains(self, other: "SymmetryElements") -> bool:
        """
        Check whether another instance `other` is a subset of the instance.
        """
        for key1, num in other.nums.items():
            if key1 in self._nums:
                ref_num = self._nums[key1]
            else:
                ref_num = 0
            zero = num == 0
            ref_zero = ref_num == 0
            if ref_num < num or zero != ref_zero:
                return False
        for key2, angles in other.angles.items():
            for angle, num in angles.items():
                if angle in self._angles[key2]:
                    ref_num = self._angles[key2][angle]
                else:
                    ref_num = 0
                zero = num == 0
                ref_zero = ref_num == 0
                if ref_num < num or zero != ref_zero:
                    return False
        return True

    @property
    def symbs(self) -> Sequence[str]:
        """Return the sorted symbols of the symmetry elements."""
        res = {}
        for prop, num in self._nums.items():
            if num > 0:
                symb = prop[0]._symb
                if len(prop) > 1:
                    symb += str(prop[1])
                if num > 1:
                    symb = str(num) + symb
                res[_prop2rank(prop)] = symb
        return tuple(res[rank] for rank in sorted(res, reverse=True))
