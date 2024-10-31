from .init import (
    TestCase,
    main,
    randvec,
    randunitvec,
    List,
)

from symmtools import (
    TAU,
    TOL,
    SYMB,
    IdentityElement,
    InversionCenter,
    RotationAxis,
    ReflectionPlane,
    RotoreflectionAxis,
    Inversion,
    Rotation,
    Reflection,
    Rotoreflection,
    Point,
    Points,
    normalize,
)


class TestIdentityElement(TestCase):
    def test_transformations(self) -> None:
        symm_elem = IdentityElement()
        self.assertSequenceEqual(tuple(symm_elem.transforms), [])

    def test_symb(self) -> None:
        symm_elem = IdentityElement()
        self.assertEqual(symm_elem.symb, "E")

    def test_symmetric(self) -> None:
        symm_elem = IdentityElement()
        points = [Point(randvec()) for _ in range(3)]
        self.assertTrue(symm_elem.symmetric(Points(points), TOL))


class TestInversionCenter(TestCase):
    def test_transformations(self) -> None:
        symm_elem = InversionCenter()
        self.assertSequenceEqual(tuple(symm_elem.transforms), [Inversion()])

    def test_symb(self) -> None:
        symm_elem = InversionCenter()
        self.assertEqual(symm_elem.symb, "i")

    def test_symmetric(self) -> None:
        symm_elem = InversionCenter()
        points: List[Point] = []
        for _ in range(3):
            points.append(Point(randvec()))
        for i in range(len(points)):
            for transform in tuple(symm_elem.transforms):
                points.append(transform(points[i]))
        self.assertTrue(symm_elem.symmetric(Points(points), TOL))


class TestRotationAxis(TestCase):
    def test_init(self) -> None:
        self.assertRaises(ValueError, RotationAxis, randunitvec(), -1)
        self.assertRaises(ValueError, RotationAxis, randunitvec(), 0)
        self.assertRaises(ValueError, RotationAxis, randunitvec(), 1)

    def test_transformations(self) -> None:
        vec = randunitvec()
        symm_elem = RotationAxis(vec, 3)
        vec = normalize(vec)
        self.assertSequenceEqual(
            tuple(symm_elem.transforms),
            [Rotation(vec, 1 / 3 * TAU), Rotation(vec, 2 / 3 * TAU)],
        )
        vec = randunitvec()
        symm_elem = RotationAxis(vec, 4)
        vec = normalize(vec)
        self.assertSequenceEqual(
            tuple(symm_elem.transforms),
            [
                Rotation(vec, 1 / 4 * TAU),
                Rotation(vec, 2 / 4 * TAU),
                Rotation(vec, 3 / 4 * TAU),
            ],
        )

    def test_symb(self) -> None:
        order = 3
        symm_elem = RotationAxis(randunitvec(), order)
        self.assertEqual(symm_elem.symb, f"C{order}")

    def test_symmetric(self) -> None:
        symm_elem = RotationAxis(randunitvec(), 3)
        points: List[Point] = []
        for _ in range(3):
            points.append(Point(randvec()))
        for i in range(len(points)):
            for transform in tuple(symm_elem.transforms):
                points.append(transform(points[i]))
        self.assertTrue(symm_elem.symmetric(Points(points), TOL))


class TestReflectionPlane(TestCase):
    def test_transformations(self) -> None:
        vec = randunitvec()
        symm_elem = ReflectionPlane(vec)
        vec = normalize(vec)
        self.assertSequenceEqual(
            tuple(symm_elem.transforms), [Reflection(vec)]
        )

    def test_symb(self) -> None:
        symm_elem = ReflectionPlane(randunitvec())
        self.assertEqual(symm_elem.symb, SYMB.refl)

    def test_symmetric(self) -> None:
        symm_elem = ReflectionPlane(randunitvec())
        points: List[Point] = []
        for _ in range(3):
            points.append(Point(randvec()))
        for i in range(len(points)):
            for transform in tuple(symm_elem.transforms):
                points.append(transform(points[i]))
        self.assertTrue(symm_elem.symmetric(Points(points), TOL))


class TestRotoreflectionAxis(TestCase):
    def test_init(self) -> None:
        self.assertRaises(ValueError, RotoreflectionAxis, randunitvec(), -1)
        self.assertRaises(ValueError, RotoreflectionAxis, randunitvec(), 0)
        self.assertRaises(ValueError, RotoreflectionAxis, randunitvec(), 1)
        self.assertRaises(ValueError, RotoreflectionAxis, randunitvec(), 2)

    def test_transformations(self) -> None:
        vec = randunitvec()
        symm_elem = RotoreflectionAxis(vec, 3)
        vec = normalize(vec)
        self.assertSequenceEqual(
            tuple(symm_elem.transforms),
            [
                Rotoreflection(vec, 1 / 3 * TAU),
                Rotation(vec, 2 / 3 * TAU),
                Reflection(vec),
                Rotation(vec, (4 % 3) / 3 * TAU),
                Rotoreflection(vec, (5 % 3) / 3 * TAU),
            ],
        )
        vec = randunitvec()
        symm_elem = RotoreflectionAxis(vec, 4)
        vec = normalize(vec)
        self.assertSequenceEqual(
            tuple(symm_elem.transforms),
            [
                Rotoreflection(vec, 1 / 4 * TAU),
                Rotation(vec, 2 / 4 * TAU),
                Rotoreflection(vec, 3 / 4 * TAU),
            ],
        )
        vec = randunitvec()
        symm_elem = RotoreflectionAxis(vec, 5)
        vec = normalize(vec)
        self.assertSequenceEqual(
            tuple(symm_elem.transforms),
            [
                Rotoreflection(vec, 1 / 5 * TAU),
                Rotation(vec, 2 / 5 * TAU),
                Rotoreflection(vec, 3 / 5 * TAU),
                Rotation(vec, 4 / 5 * TAU),
                Reflection(vec),
                Rotation(vec, (6 % 5) / 5 * TAU),
                Rotoreflection(vec, (7 % 5) / 5 * TAU),
                Rotation(vec, (8 % 5) / 5 * TAU),
                Rotoreflection(vec, (9 % 5) / 5 * TAU),
            ],
        )
        vec = randunitvec()
        symm_elem = RotoreflectionAxis(vec, 6)
        vec = normalize(vec)
        self.assertSequenceEqual(
            tuple(symm_elem.transforms),
            [
                Rotoreflection(vec, 1 / 6 * TAU),
                Rotation(vec, 2 / 6 * TAU),
                Inversion(),
                Rotation(vec, 4 / 6 * TAU),
                Rotoreflection(vec, 5 / 6 * TAU),
            ],
        )

    def test_symb(self) -> None:
        order = 3
        symm_elem = RotoreflectionAxis(randunitvec(), order)
        self.assertEqual(symm_elem.symb, f"S{order}")

    def test_symmetric(self) -> None:
        symm_elem = RotoreflectionAxis(randunitvec(), 3)
        points: List[Point] = []
        for _ in range(3):
            points.append(Point(randvec()))
        for i in range(len(points)):
            for transform in tuple(symm_elem.transforms):
                points.append(transform(points[i]))
        self.assertTrue(symm_elem.symmetric(Points(points), TOL))


if __name__ == "__main__":
    main()
