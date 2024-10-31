from .init import (
    TestCase,
    main,
    randint,
    normalvariate,
    zeros,
    cross,
    norm,
    ndarray,
    float64,
    randvec,
    randunitvec,
    randne0vec,
    perturb,
    orthperturb,
    randangle,
)

from symmtools import (
    TOL,
    vector,
    canonicalize,
    normalize,
    orthogonalize,
    diff,
    same,
    indep,
    unitindep,
    parallel,
    perpendicular,
    translate,
    invert,
    move2,
    rotate,
    reflect,
    rotmat,
    reflmat,
)


class TestVecOp(TestCase):
    def test_vector(self) -> None:
        arr = [randint(-8, 8) for _ in range(3)]
        vec = vector(arr)
        self.assertIsInstance(vec, ndarray)
        self.assertEqual(vec.dtype, float64)
        self.assertListEqual(vec.tolist(), arr)
        arr = randvec().tolist()
        vec = vector(arr)
        self.assertIsInstance(vec, ndarray)
        self.assertEqual(vec.dtype, float64)
        self.assertListEqual(vec.tolist(), arr)

    def test_canonicalize(self) -> None:
        vec = randvec()
        for i in range(3):
            while vec[i] == 0.0:
                vec[i] = normalvariate(0.0, 1.0)
            vec[i] = abs(vec[i])
            self.assertListEqual(canonicalize(vec).tolist(), vec.tolist())
            vec[i] = -vec[i]
            self.assertListEqual(canonicalize(vec).tolist(), (-vec).tolist())
            vec[i] = 0.0
        self.assertListEqual(canonicalize(vec).tolist(), vec.tolist())

    def test_normalize(self) -> None:
        vec = randne0vec()
        self.assertListEqual(
            normalize(vec).tolist(), (vec / norm(vec)).tolist()
        )

    def test_orthogonalize(self) -> None:
        vec1 = randvec()
        vec2 = randunitvec()
        self.assertLessEqual(orthogonalize(vec1, vec2).dot(vec2), TOL)

    def test_diff(self) -> None:
        vec1 = randvec()
        vec2 = vec1
        while (vec1 == vec2).all():
            vec2 = randvec()
        self.assertEqual(diff(vec1, vec1), 0.0)
        self.assertEqual(diff(vec2, vec2), 0.0)
        self.assertGreaterEqual(diff(vec1, vec2), abs(vec1 - vec2).max())

    def test_same(self) -> None:
        vec1 = randvec()
        vec2 = vec1
        while diff(vec1, vec2) <= TOL:
            vec2 = randvec()
        self.assertTrue(same(vec1, vec1, 0.0))
        self.assertTrue(same(vec2, vec2, 0.0))
        self.assertFalse(same(vec1, vec2, TOL))
        self.assertTrue(same(vec1, vec1 + perturb(), TOL))
        self.assertTrue(same(vec2, vec2 + perturb(), TOL))
        self.assertFalse(same(vec1, vec1 + 2.0 * perturb(), TOL))
        self.assertFalse(same(vec2, vec2 + 2.0 * perturb(), TOL))

    def test_indep(self) -> None:
        vec = randvec()
        self.assertEqual(indep(vec, vec), 0.0)
        self.assertEqual(indep(vec, -vec), 0.0)
        self.assertEqual(indep(vec, 2.0 * vec), 0.0)
        self.assertEqual(indep(vec, 0.0 * vec), 0.0)
        self.assertGreater(indep(vec, vec + perturb()), 0.0)

    def test_unitindep(self) -> None:
        vec = randunitvec()
        self.assertEqual(unitindep(vec, vec), 0.0)
        self.assertEqual(unitindep(vec, -vec), 0.0)
        self.assertGreater(indep(vec, vec + perturb()), 0.0)

    def test_parallel(self) -> None:
        vec = randvec()
        self.assertTrue(parallel(vec, vec, 0.0))
        self.assertTrue(parallel(vec, -vec, 0.0))
        self.assertTrue(parallel(vec, 2.0 * vec, 0.0))
        self.assertTrue(parallel(vec, 0.0 * vec, 0.0))
        self.assertTrue(parallel(vec, vec + perturb(), 4.0 * TOL))
        self.assertFalse(
            parallel(vec, vec + 4.0 * orthperturb(normalize(vec)), TOL)
        )

    def test_perpendicular(self) -> None:
        vec1 = randvec()
        vec2 = zeros(3)
        while (vec2 == 0.0).all():
            vec2 = randvec()
            vec2 -= vec2.dot(vec1) / vec1.dot(vec1) * vec1
        self.assertFalse(perpendicular(vec1, vec1, TOL))
        self.assertFalse(perpendicular(vec1, -vec1, TOL))
        self.assertFalse(perpendicular(vec1, 2.0 * vec1, TOL))
        self.assertTrue(perpendicular(vec1, 0.0 * vec1, TOL))
        self.assertTrue(perpendicular(vec1, vec2, TOL))
        self.assertTrue(perpendicular(vec1, vec2 + perturb(), 4.0 * TOL))

    def test_translate(self) -> None:
        vec = randvec()
        transl = randvec()
        self.assertListEqual(
            translate(vec, transl).tolist(), (vec + transl).tolist()
        )

    def test_invert(self) -> None:
        vec = randvec()
        self.assertListEqual(invert(vec).tolist(), (-vec).tolist())

    def test_move2(self) -> None:
        vec = randvec()
        normal = randunitvec()
        coef1, coef2 = [normalvariate(0.0, 1.0) for _ in range(2)]
        base = vec.dot(normal) * normal
        projection = vec - base
        perpendicular = cross(normal, projection)
        res = base + projection * coef1 + perpendicular * coef2
        self.assertListEqual(
            move2(vec, normal, coef1, coef2).tolist(), res.tolist()
        )

    def test_rotate(self) -> None:
        vec = randvec()
        axis = randunitvec()
        angle = randangle()
        mat = rotmat(axis, angle)
        self.assertLessEqual(diff(rotate(vec, axis, angle), mat @ vec), TOL)

    def test_reflect(self) -> None:
        vec = randvec()
        normal = randunitvec()
        mat = reflmat(normal)
        self.assertLessEqual(diff(reflect(vec, normal), mat @ vec), TOL)


if __name__ == "__main__":
    main()
