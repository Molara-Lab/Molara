"""Type hints."""

__all__ = [
    "TypeVar",
    "Union",
    "Optional",
    "Type",
    "Any",
    "Sequence",
    "Set",
    "Tuple",
    "List",
    "Dict",
    "Iterable",
    "Iterator",
    "Bool",
    "Int",
    "Float",
    "Complex",
    "Real",
    "Scalar",
    "Bools",
    "Ints",
    "Floats",
    "Complexes",
    "Reals",
    "Scalars",
    "Vector",
    "Matrix",
    "RealVector",
    "RealVectors",
]

from typing import (
    TypeVar,
    Union,
    Optional,
    Type,
    Any,
    Sequence,
    Set,
    Tuple,
    List,
    Dict,
    Iterable,
    Iterator,
)

from numpy import bool_, signedinteger, floating, complexfloating
from numpy.typing import NDArray

Bool = Union[bool, bool_]
Int = Union[int, signedinteger]
Float = Union[float, floating]
Complex = Union[complex, complexfloating]
Real = Union[Int, Float]
Scalar = Union[Int, Float, Complex]
Bools = Sequence[Bool]
Ints = Sequence[Int]
Floats = Sequence[Float]
Complexes = Sequence[Complex]
Reals = Sequence[Real]
Scalars = Sequence[Scalar]
Vector = NDArray[floating]
Matrix = NDArray[floating]
RealVector = Union[Vector, Reals]
RealVectors = Sequence[RealVector]
