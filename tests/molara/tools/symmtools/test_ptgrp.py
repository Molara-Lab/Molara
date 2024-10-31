from .init import TestCase, main, Union, Sequence, Tuple, pi, roots

from symmtools import (
    chcoords,
    signvar,
    ax3permut,
    Translation,
    Inversion,
    Rotation,
    Points,
    SymmetryElement,
    InversionCenter,
    RotationAxis,
    InfRotationAxis,
    ReflectionPlane,
    RotoreflectionAxis,
    InfRotoreflectionAxis,
    AxisRotationAxes,
    CenterRotationAxes,
    PointGroup,
    SymmetryElements,
    PHI,
    TOL,
)

origin = (0, 0, 0)
primax = (0, 0, 1)
secax = (1, 0, 0)
diagax = (2.0**-0.5, 2.0**-0.5, 0)
pos_transl = Translation(primax)
neg_transl = pos_transl.invert()
orth_transl = Translation(secax)
rot2 = RotationAxis(primax, 2)
rot3 = RotationAxis(primax, 3)
rot4 = RotationAxis(primax, 4)
rot5 = RotationAxis(primax, 5)
rot6 = RotationAxis(primax, 6)
rotorefl4 = RotoreflectionAxis(primax, 4)
rotorefl6 = RotoreflectionAxis(primax, 6)
rotorefl8 = RotoreflectionAxis(primax, 8)
rotorefl10 = RotoreflectionAxis(primax, 10)
rotorefl12 = RotoreflectionAxis(primax, 12)

point = Points.from_arr((origin,))
two_points = point + pos_transl(point)
three_collinear_points = two_points + neg_transl(neg_transl(point))
asymmetric_triangle = Points.from_arr(chcoords([[0, 0], [0, 2], [3, 0]]))

shifted_point = orth_transl(point)
rectangle = Points.from_arr(chcoords(signvar([3, 2])))
triangle = Points.from_symm(shifted_point, rot3)
square = Points.from_symm(shifted_point, rot4)
pentagon = Points.from_symm(shifted_point, rot5)
hexagon = Points.from_symm(shifted_point, rot6)

_base = pos_transl(asymmetric_triangle)
asymmetric_pyramid = point + _base
asymmetric_prism = _base + neg_transl(asymmetric_triangle)
asymmetric_antiprism = _base + Inversion()(_base)

_base = orth_transl(Rotation(secax, pi / 4)(two_points))
rot2_obj = Points.from_symm(_base, rot2)
rot3_obj = Points.from_symm(_base, rot3)
rot4_obj = Points.from_symm(_base, rot4)
rot5_obj = Points.from_symm(_base, rot5)
rot6_obj = Points.from_symm(_base, rot6)

angle = point + orth_transl(two_points.center())
triangular_pyramid = point + pos_transl(triangle)
quadrangular_pyramid = point + pos_transl(square)
pentangular_pyramid = point + pos_transl(pentagon)
hexangular_pyramid = point + pos_transl(hexagon)

_base = orth_transl(Rotation(diagax, pi / 2)(two_points))
double_propeller = Points.from_symm(_base, rot2)
triple_propeller = Points.from_symm(_base, rot3)
quadruple_propeller = Points.from_symm(_base, rot4)
pentuple_propeller = Points.from_symm(_base, rot5)
hextuple_propeller = Points.from_symm(_base, rot6)

_base = pos_transl(pos_transl(_base))
rotorefl4_obj = Points.from_symm(_base, rotorefl4)
rotorefl6_obj = Points.from_symm(_base, rotorefl6)
rotorefl8_obj = Points.from_symm(_base, rotorefl8)
rotorefl10_obj = Points.from_symm(_base, rotorefl10)
rotorefl12_obj = Points.from_symm(_base, rotorefl12)

_base = orth_transl(Rotation(secax, pi / 3)(two_points.center()))
double_helix = Points.from_symm(_base, rot2)
triple_helix = Points.from_symm(_base, rot3)
quadruple_helix = Points.from_symm(_base, rot4)
pentuple_helix = Points.from_symm(_base, rot5)
hextuple_helix = Points.from_symm(_base, rot6)

_base = pos_transl(pos_transl(orth_transl(point)))
quarter_twist = Points.from_symm(_base, rotorefl4)
triangular_antiprism = Points.from_symm(_base, rotorefl6)
quadrangular_antiprism = Points.from_symm(_base, rotorefl8)
pentangular_antiprism = Points.from_symm(_base, rotorefl10)
hexangular_antiprism = Points.from_symm(_base, rotorefl12)

rectangular_prism = pos_transl(rectangle) + neg_transl(rectangle)
triangular_prism = pos_transl(triangle) + neg_transl(triangle)
quadrangular_prism = pos_transl(square) + neg_transl(square)
pentangular_prism = pos_transl(pentagon) + neg_transl(pentagon)
hexangular_prism = pos_transl(hexagon) + neg_transl(hexagon)

tetrahedral = Points.from_arr(ax3permut(signvar([3, 2, 1], 1)))
pyritohedron = Points.from_arr(ax3permut(signvar([2, 1])))
octahedral = Points.from_arr(
    ax3permut(signvar([3, 2, 1], 1)) + ax3permut(signvar([2, 3, 1], -1))
)
XI = abs(roots([1, -2, 0, PHI**2])[2])
icosahedral = Points.from_transform(
    [[PHI**2 * (1 - XI), PHI * (XI * (1 + XI) - PHI**2), XI]],
    [Rotation([0, 1, PHI], 2 * pi / 5), Rotation([1, 1, 1], 2 * pi / 3)],
    TOL,
)

tetrahedron = Points.from_arr(signvar([1, 1, 1], 1))
cube = Points.from_arr(signvar([1, 1, 1]))
octahedron = Points.from_arr(ax3permut(signvar([1])))
icosahedron = Points.from_arr(ax3permut(signvar([PHI, 1])))
dodecahedron = Points.from_arr(
    signvar([PHI, PHI, PHI]) + ax3permut(signvar([PHI + 1, 1]))
)


class TestPointGroup(TestCase):
    def test_init(self) -> None:
        def stringify(symb: str) -> Tuple[str, str]:
            group = PointGroup(symb)
            info = SymmetryElements()
            info.include(tuple(group.symm_elems), TOL)
            return ",".join(info.symbs), group.symb

        symm_elem_symbs, group_symb = stringify("Cs")
        self.assertEqual(group_symb, "Cs")
        self.assertEqual(symm_elem_symbs, "s")

        symm_elem_symbs, group_symb = stringify("Ci")
        self.assertEqual(group_symb, "Ci")
        self.assertEqual(symm_elem_symbs, "i")

        symm_elem_symbs, group_symb = stringify("C1")
        self.assertEqual(group_symb, "C1")
        self.assertEqual(symm_elem_symbs, "")

        symm_elem_symbs, group_symb = stringify("C2")
        self.assertEqual(group_symb, "C2")
        self.assertEqual(symm_elem_symbs, "C2")

        symm_elem_symbs, group_symb = stringify("C3")
        self.assertEqual(group_symb, "C3")
        self.assertEqual(symm_elem_symbs, "C3")

        symm_elem_symbs, group_symb = stringify("C4")
        self.assertEqual(group_symb, "C4")
        self.assertEqual(symm_elem_symbs, "C4")

        symm_elem_symbs, group_symb = stringify("C5")
        self.assertEqual(group_symb, "C5")
        self.assertEqual(symm_elem_symbs, "C5")

        symm_elem_symbs, group_symb = stringify("C6")
        self.assertEqual(group_symb, "C6")
        self.assertEqual(symm_elem_symbs, "C6")

        symm_elem_symbs, group_symb = stringify("Coo")
        self.assertEqual(group_symb, "Coo")
        self.assertEqual(symm_elem_symbs, "Coo")

        symm_elem_symbs, group_symb = stringify("C1i")
        self.assertEqual(group_symb, "Ci")
        self.assertEqual(symm_elem_symbs, "i")

        symm_elem_symbs, group_symb = stringify("C2i")
        self.assertEqual(group_symb, "Cs")
        self.assertEqual(symm_elem_symbs, "s")

        symm_elem_symbs, group_symb = stringify("C3i")
        self.assertEqual(group_symb, "S6")
        self.assertEqual(symm_elem_symbs, "C3,i,S6")

        symm_elem_symbs, group_symb = stringify("C4i")
        self.assertEqual(group_symb, "S4")
        self.assertEqual(symm_elem_symbs, "C2,S4")

        symm_elem_symbs, group_symb = stringify("C5i")
        self.assertEqual(group_symb, "S10")
        self.assertEqual(symm_elem_symbs, "C5,i,S10")

        symm_elem_symbs, group_symb = stringify("C6i")
        self.assertEqual(group_symb, "C3h")
        self.assertEqual(symm_elem_symbs, "C3,s,S3")

        symm_elem_symbs, group_symb = stringify("Cooi")
        self.assertEqual(group_symb, "Cooh")
        self.assertEqual(symm_elem_symbs, "Coo,s,i,Soo")

        symm_elem_symbs, group_symb = stringify("C1v")
        self.assertEqual(group_symb, "Cs")
        self.assertEqual(symm_elem_symbs, "s")

        symm_elem_symbs, group_symb = stringify("C2v")
        self.assertEqual(group_symb, "C2v")
        self.assertEqual(symm_elem_symbs, "C2,2s")

        symm_elem_symbs, group_symb = stringify("C3v")
        self.assertEqual(group_symb, "C3v")
        self.assertEqual(symm_elem_symbs, "C3,3s")

        symm_elem_symbs, group_symb = stringify("C4v")
        self.assertEqual(group_symb, "C4v")
        self.assertEqual(symm_elem_symbs, "C4,4s")

        symm_elem_symbs, group_symb = stringify("C5v")
        self.assertEqual(group_symb, "C5v")
        self.assertEqual(symm_elem_symbs, "C5,5s")

        symm_elem_symbs, group_symb = stringify("C6v")
        self.assertEqual(group_symb, "C6v")
        self.assertEqual(symm_elem_symbs, "C6,6s")

        symm_elem_symbs, group_symb = stringify("Coov")
        self.assertEqual(group_symb, "Coov")
        self.assertEqual(symm_elem_symbs, "Coo,oosv")

        symm_elem_symbs, group_symb = stringify("C1h")
        self.assertEqual(group_symb, "Cs")
        self.assertEqual(symm_elem_symbs, "s")

        symm_elem_symbs, group_symb = stringify("C2h")
        self.assertEqual(group_symb, "C2h")
        self.assertEqual(symm_elem_symbs, "C2,s,i")

        symm_elem_symbs, group_symb = stringify("C3h")
        self.assertEqual(group_symb, "C3h")
        self.assertEqual(symm_elem_symbs, "C3,s,S3")

        symm_elem_symbs, group_symb = stringify("C4h")
        self.assertEqual(group_symb, "C4h")
        self.assertEqual(symm_elem_symbs, "C4,s,i,S4")

        symm_elem_symbs, group_symb = stringify("C5h")
        self.assertEqual(group_symb, "C5h")
        self.assertEqual(symm_elem_symbs, "C5,s,S5")

        symm_elem_symbs, group_symb = stringify("C6h")
        self.assertEqual(group_symb, "C6h")
        self.assertEqual(symm_elem_symbs, "C6,s,i,S6")

        symm_elem_symbs, group_symb = stringify("Cooh")
        self.assertEqual(group_symb, "Cooh")
        self.assertEqual(symm_elem_symbs, "Coo,s,i,Soo")

        symm_elem_symbs, group_symb = stringify("S1")
        self.assertEqual(group_symb, "Cs")
        self.assertEqual(symm_elem_symbs, "s")

        symm_elem_symbs, group_symb = stringify("S2")
        self.assertEqual(group_symb, "Ci")
        self.assertEqual(symm_elem_symbs, "i")

        symm_elem_symbs, group_symb = stringify("S3")
        self.assertEqual(group_symb, "C3h")
        self.assertEqual(symm_elem_symbs, "C3,s,S3")

        symm_elem_symbs, group_symb = stringify("S4")
        self.assertEqual(group_symb, "S4")
        self.assertEqual(symm_elem_symbs, "C2,S4")

        symm_elem_symbs, group_symb = stringify("S5")
        self.assertEqual(group_symb, "C5h")
        self.assertEqual(symm_elem_symbs, "C5,s,S5")

        symm_elem_symbs, group_symb = stringify("S6")
        self.assertEqual(group_symb, "S6")
        self.assertEqual(symm_elem_symbs, "C3,i,S6")

        symm_elem_symbs, group_symb = stringify("Soo")
        self.assertEqual(group_symb, "Cooh")
        self.assertEqual(symm_elem_symbs, "Coo,s,i,Soo")

        symm_elem_symbs, group_symb = stringify("D1")
        self.assertEqual(group_symb, "C2")
        self.assertEqual(symm_elem_symbs, "C2")

        symm_elem_symbs, group_symb = stringify("D2")
        self.assertEqual(group_symb, "D2")
        self.assertEqual(symm_elem_symbs, "3C2")

        symm_elem_symbs, group_symb = stringify("D3")
        self.assertEqual(group_symb, "D3")
        self.assertEqual(symm_elem_symbs, "C3,3C2")

        symm_elem_symbs, group_symb = stringify("D4")
        self.assertEqual(group_symb, "D4")
        self.assertEqual(symm_elem_symbs, "C4,4C2")

        symm_elem_symbs, group_symb = stringify("D5")
        self.assertEqual(group_symb, "D5")
        self.assertEqual(symm_elem_symbs, "C5,5C2")

        symm_elem_symbs, group_symb = stringify("D6")
        self.assertEqual(group_symb, "D6")
        self.assertEqual(symm_elem_symbs, "C6,6C2")

        symm_elem_symbs, group_symb = stringify("Doo")
        self.assertEqual(group_symb, "Doo")
        self.assertEqual(symm_elem_symbs, "Coo,ooC2")

        symm_elem_symbs, group_symb = stringify("D1d")
        self.assertEqual(group_symb, "C2h")
        self.assertEqual(symm_elem_symbs, "C2,s,i")

        symm_elem_symbs, group_symb = stringify("D2d")
        self.assertEqual(group_symb, "D2d")
        self.assertEqual(symm_elem_symbs, "3C2,2s,S4")

        symm_elem_symbs, group_symb = stringify("D3d")
        self.assertEqual(group_symb, "D3d")
        self.assertEqual(symm_elem_symbs, "C3,3C2,3s,i,S6")

        symm_elem_symbs, group_symb = stringify("D4d")
        self.assertEqual(group_symb, "D4d")
        self.assertEqual(symm_elem_symbs, "C4,4C2,4s,S8")

        symm_elem_symbs, group_symb = stringify("D5d")
        self.assertEqual(group_symb, "D5d")
        self.assertEqual(symm_elem_symbs, "C5,5C2,5s,i,S10")

        symm_elem_symbs, group_symb = stringify("D6d")
        self.assertEqual(group_symb, "D6d")
        self.assertEqual(symm_elem_symbs, "C6,6C2,6s,S12")

        symm_elem_symbs, group_symb = stringify("Dood")
        self.assertEqual(group_symb, "Dooh")
        self.assertEqual(symm_elem_symbs, "Coo,ooC2,oosv,s,i,Soo")

        symm_elem_symbs, group_symb = stringify("D1h")
        self.assertEqual(group_symb, "C2v")
        self.assertEqual(symm_elem_symbs, "C2,2s")

        symm_elem_symbs, group_symb = stringify("D2h")
        self.assertEqual(group_symb, "D2h")
        self.assertEqual(symm_elem_symbs, "3C2,3s,i")

        symm_elem_symbs, group_symb = stringify("D3h")
        self.assertEqual(group_symb, "D3h")
        self.assertEqual(symm_elem_symbs, "C3,3C2,4s,S3")

        symm_elem_symbs, group_symb = stringify("D4h")
        self.assertEqual(group_symb, "D4h")
        self.assertEqual(symm_elem_symbs, "C4,4C2,5s,i,S4")

        symm_elem_symbs, group_symb = stringify("D5h")
        self.assertEqual(group_symb, "D5h")
        self.assertEqual(symm_elem_symbs, "C5,5C2,6s,S5")

        symm_elem_symbs, group_symb = stringify("D6h")
        self.assertEqual(group_symb, "D6h")
        self.assertEqual(symm_elem_symbs, "C6,6C2,7s,i,S6")

        symm_elem_symbs, group_symb = stringify("Dooh")
        self.assertEqual(group_symb, "Dooh")
        self.assertEqual(symm_elem_symbs, "Coo,ooC2,oosv,s,i,Soo")

        symm_elem_symbs, group_symb = stringify("T")
        self.assertEqual(group_symb, "T")
        self.assertEqual(symm_elem_symbs, "4C3,3C2")

        symm_elem_symbs, group_symb = stringify("Td")
        self.assertEqual(group_symb, "Td")
        self.assertEqual(symm_elem_symbs, "4C3,3C2,6s,3S4")

        symm_elem_symbs, group_symb = stringify("Th")
        self.assertEqual(group_symb, "Th")
        self.assertEqual(symm_elem_symbs, "4C3,3C2,3s,i,4S6")

        symm_elem_symbs, group_symb = stringify("O")
        self.assertEqual(group_symb, "O")
        self.assertEqual(symm_elem_symbs, "3C4,4C3,6C2")

        symm_elem_symbs, group_symb = stringify("Oh")
        self.assertEqual(group_symb, "Oh")
        self.assertEqual(symm_elem_symbs, "3C4,4C3,6C2,9s,i,4S6,3S4")

        symm_elem_symbs, group_symb = stringify("I")
        self.assertEqual(group_symb, "I")
        self.assertEqual(symm_elem_symbs, "6C5,10C3,15C2")

        symm_elem_symbs, group_symb = stringify("Ih")
        self.assertEqual(group_symb, "Ih")
        self.assertEqual(symm_elem_symbs, "6C5,10C3,15C2,15s,i,6S10,10S6")

        symm_elem_symbs, group_symb = stringify("K")
        self.assertEqual(group_symb, "K")
        self.assertEqual(symm_elem_symbs, "ooCoo")

        symm_elem_symbs, group_symb = stringify("Kh")
        self.assertEqual(group_symb, "Kh")
        self.assertEqual(symm_elem_symbs, "ooCoo,oos,i,ooSoo")

    def test_from_all_symm_elems(self) -> None:
        def stringify(
            symm_elems: Union[Sequence[SymmetryElement], Points]
        ) -> Tuple[str, str]:
            if isinstance(symm_elems, Points):
                symm_elems = tuple(symm_elems.symm_elems(TOL))
            info = SymmetryElements()
            info.include(symm_elems, TOL)
            group = PointGroup.from_all_symm_elems(symm_elems)
            return ",".join(info.symbs), group.symb

        symm_elem_symbs, group_symb = stringify(asymmetric_pyramid)
        self.assertEqual(symm_elem_symbs, "")
        self.assertEqual(group_symb, "C1")

        symm_elem_symbs, group_symb = stringify(asymmetric_triangle)
        self.assertEqual(symm_elem_symbs, "s")
        self.assertEqual(group_symb, "Cs")

        symm_elem_symbs, group_symb = stringify(asymmetric_prism)
        self.assertEqual(symm_elem_symbs, "s")
        self.assertEqual(group_symb, "Cs")

        symm_elem_symbs, group_symb = stringify(asymmetric_antiprism)
        self.assertEqual(symm_elem_symbs, "i")
        self.assertEqual(group_symb, "Ci")

        symm_elem_symbs, group_symb = stringify(rot2_obj)
        self.assertEqual(symm_elem_symbs, "C2")
        self.assertEqual(group_symb, "C2")

        symm_elem_symbs, group_symb = stringify(rot3_obj)
        self.assertEqual(symm_elem_symbs, "C3")
        self.assertEqual(group_symb, "C3")

        symm_elem_symbs, group_symb = stringify(rot4_obj)
        self.assertEqual(symm_elem_symbs, "C4")
        self.assertEqual(group_symb, "C4")

        symm_elem_symbs, group_symb = stringify(rot5_obj)
        self.assertEqual(symm_elem_symbs, "C5")
        self.assertEqual(group_symb, "C5")

        symm_elem_symbs, group_symb = stringify(rot6_obj)
        self.assertEqual(symm_elem_symbs, "C6")
        self.assertEqual(group_symb, "C6")

        symm_elem_symbs, group_symb = stringify(angle)
        self.assertEqual(symm_elem_symbs, "C2,2s")
        self.assertEqual(group_symb, "C2v")

        symm_elem_symbs, group_symb = stringify(triangular_pyramid)
        self.assertEqual(symm_elem_symbs, "C3,3s")
        self.assertEqual(group_symb, "C3v")

        symm_elem_symbs, group_symb = stringify(quadrangular_pyramid)
        self.assertEqual(symm_elem_symbs, "C4,4s")
        self.assertEqual(group_symb, "C4v")

        symm_elem_symbs, group_symb = stringify(pentangular_pyramid)
        self.assertEqual(symm_elem_symbs, "C5,5s")
        self.assertEqual(group_symb, "C5v")

        symm_elem_symbs, group_symb = stringify(hexangular_pyramid)
        self.assertEqual(symm_elem_symbs, "C6,6s")
        self.assertEqual(group_symb, "C6v")

        symm_elem_symbs, group_symb = stringify(double_propeller)
        self.assertEqual(symm_elem_symbs, "C2,s,i")
        self.assertEqual(group_symb, "C2h")

        symm_elem_symbs, group_symb = stringify(triple_propeller)
        self.assertEqual(symm_elem_symbs, "C3,s,S3")
        self.assertEqual(group_symb, "C3h")

        symm_elem_symbs, group_symb = stringify(quadruple_propeller)
        self.assertEqual(symm_elem_symbs, "C4,s,i,S4")
        self.assertEqual(group_symb, "C4h")

        symm_elem_symbs, group_symb = stringify(pentuple_propeller)
        self.assertEqual(symm_elem_symbs, "C5,s,S5")
        self.assertEqual(group_symb, "C5h")

        symm_elem_symbs, group_symb = stringify(hextuple_propeller)
        self.assertEqual(symm_elem_symbs, "C6,s,i,S6")
        self.assertEqual(group_symb, "C6h")

        symm_elem_symbs, group_symb = stringify(rotorefl4_obj)
        self.assertEqual(symm_elem_symbs, "C2,S4")
        self.assertEqual(group_symb, "S4")

        symm_elem_symbs, group_symb = stringify(rotorefl6_obj)
        self.assertEqual(symm_elem_symbs, "C3,i,S6")
        self.assertEqual(group_symb, "S6")

        symm_elem_symbs, group_symb = stringify(rotorefl8_obj)
        self.assertEqual(symm_elem_symbs, "C4,S8")
        self.assertEqual(group_symb, "S8")

        symm_elem_symbs, group_symb = stringify(rotorefl10_obj)
        self.assertEqual(symm_elem_symbs, "C5,i,S10")
        self.assertEqual(group_symb, "S10")

        symm_elem_symbs, group_symb = stringify(rotorefl12_obj)
        self.assertEqual(symm_elem_symbs, "C6,S12")
        self.assertEqual(group_symb, "S12")

        symm_elem_symbs, group_symb = stringify(double_helix)
        self.assertEqual(symm_elem_symbs, "3C2")
        self.assertEqual(group_symb, "D2")

        symm_elem_symbs, group_symb = stringify(triple_helix)
        self.assertEqual(symm_elem_symbs, "C3,3C2")
        self.assertEqual(group_symb, "D3")

        symm_elem_symbs, group_symb = stringify(quadruple_helix)
        self.assertEqual(symm_elem_symbs, "C4,4C2")
        self.assertEqual(group_symb, "D4")

        symm_elem_symbs, group_symb = stringify(pentuple_helix)
        self.assertEqual(symm_elem_symbs, "C5,5C2")
        self.assertEqual(group_symb, "D5")

        symm_elem_symbs, group_symb = stringify(hextuple_helix)
        self.assertEqual(symm_elem_symbs, "C6,6C2")
        self.assertEqual(group_symb, "D6")

        symm_elem_symbs, group_symb = stringify(quarter_twist)
        self.assertEqual(symm_elem_symbs, "3C2,2s,S4")
        self.assertEqual(group_symb, "D2d")

        symm_elem_symbs, group_symb = stringify(triangular_antiprism)
        self.assertEqual(symm_elem_symbs, "C3,3C2,3s,i,S6")
        self.assertEqual(group_symb, "D3d")

        symm_elem_symbs, group_symb = stringify(quadrangular_antiprism)
        self.assertEqual(symm_elem_symbs, "C4,4C2,4s,S8")
        self.assertEqual(group_symb, "D4d")

        symm_elem_symbs, group_symb = stringify(pentangular_antiprism)
        self.assertEqual(symm_elem_symbs, "C5,5C2,5s,i,S10")
        self.assertEqual(group_symb, "D5d")

        symm_elem_symbs, group_symb = stringify(hexangular_antiprism)
        self.assertEqual(symm_elem_symbs, "C6,6C2,6s,S12")
        self.assertEqual(group_symb, "D6d")

        symm_elem_symbs, group_symb = stringify(rectangle)
        self.assertEqual(symm_elem_symbs, "3C2,3s,i")
        self.assertEqual(group_symb, "D2h")

        symm_elem_symbs, group_symb = stringify(rectangular_prism)
        self.assertEqual(symm_elem_symbs, "3C2,3s,i")
        self.assertEqual(group_symb, "D2h")

        symm_elem_symbs, group_symb = stringify(triangle)
        self.assertEqual(symm_elem_symbs, "C3,3C2,4s,S3")
        self.assertEqual(group_symb, "D3h")

        symm_elem_symbs, group_symb = stringify(triangular_prism)
        self.assertEqual(symm_elem_symbs, "C3,3C2,4s,S3")
        self.assertEqual(group_symb, "D3h")

        symm_elem_symbs, group_symb = stringify(square)
        self.assertEqual(symm_elem_symbs, "C4,4C2,5s,i,S4")
        self.assertEqual(group_symb, "D4h")

        symm_elem_symbs, group_symb = stringify(quadrangular_prism)
        self.assertEqual(symm_elem_symbs, "C4,4C2,5s,i,S4")
        self.assertEqual(group_symb, "D4h")

        symm_elem_symbs, group_symb = stringify(pentagon)
        self.assertEqual(symm_elem_symbs, "C5,5C2,6s,S5")
        self.assertEqual(group_symb, "D5h")

        symm_elem_symbs, group_symb = stringify(pentangular_prism)
        self.assertEqual(symm_elem_symbs, "C5,5C2,6s,S5")
        self.assertEqual(group_symb, "D5h")

        symm_elem_symbs, group_symb = stringify(hexagon)
        self.assertEqual(symm_elem_symbs, "C6,6C2,7s,i,S6")
        self.assertEqual(group_symb, "D6h")

        symm_elem_symbs, group_symb = stringify(hexangular_prism)
        self.assertEqual(symm_elem_symbs, "C6,6C2,7s,i,S6")
        self.assertEqual(group_symb, "D6h")

        symm_elem_symbs, group_symb = stringify(tetrahedral)
        self.assertEqual(symm_elem_symbs, "4C3,3C2")
        self.assertEqual(group_symb, "T")

        symm_elem_symbs, group_symb = stringify(tetrahedron)
        self.assertEqual(symm_elem_symbs, "4C3,3C2,6s,3S4")
        self.assertEqual(group_symb, "Td")

        symm_elem_symbs, group_symb = stringify(pyritohedron)
        self.assertEqual(symm_elem_symbs, "4C3,3C2,3s,i,4S6")
        self.assertEqual(group_symb, "Th")

        symm_elem_symbs, group_symb = stringify(octahedral)
        self.assertEqual(symm_elem_symbs, "3C4,4C3,6C2")
        self.assertEqual(group_symb, "O")

        symm_elem_symbs, group_symb = stringify(cube)
        self.assertEqual(symm_elem_symbs, "3C4,4C3,6C2,9s,i,4S6,3S4")
        self.assertEqual(group_symb, "Oh")

        symm_elem_symbs, group_symb = stringify(octahedron)
        self.assertEqual(symm_elem_symbs, "3C4,4C3,6C2,9s,i,4S6,3S4")
        self.assertEqual(group_symb, "Oh")

        symm_elem_symbs, group_symb = stringify(icosahedral)
        self.assertEqual(symm_elem_symbs, "6C5,10C3,15C2")
        self.assertEqual(group_symb, "I")

        symm_elem_symbs, group_symb = stringify(icosahedron)
        self.assertEqual(symm_elem_symbs, "6C5,10C3,15C2,15s,i,6S10,10S6")
        self.assertEqual(group_symb, "Ih")

        symm_elem_symbs, group_symb = stringify(dodecahedron)
        self.assertEqual(symm_elem_symbs, "6C5,10C3,15C2,15s,i,6S10,10S6")
        self.assertEqual(group_symb, "Ih")

        symm_elems: Sequence[SymmetryElement]
        primax = (0.0, 0.0, 1.0)

        symm_elems = [InfRotationAxis(primax)]
        symm_elem_symbs, group_symb = stringify(symm_elems)
        self.assertEqual(symm_elem_symbs, "Coo")
        self.assertEqual(group_symb, "Coo")

        symm_elems = [
            InfRotationAxis(primax),
            ReflectionPlane(primax),
            InversionCenter(),
            InfRotoreflectionAxis(primax),
        ]
        symm_elem_symbs, group_symb = stringify(symm_elems)
        self.assertEqual(symm_elem_symbs, "Coo,s,i,Soo")
        self.assertEqual(group_symb, "Cooh")

        symm_elem_symbs, group_symb = stringify(three_collinear_points)
        self.assertEqual(symm_elem_symbs, "Coo,oosv")
        self.assertEqual(group_symb, "Coov")

        symm_elems = [
            InfRotationAxis(primax),
            AxisRotationAxes(primax),
        ]
        symm_elem_symbs, group_symb = stringify(symm_elems)
        self.assertEqual(symm_elem_symbs, "Coo,ooC2")
        self.assertEqual(group_symb, "Doo")

        symm_elem_symbs, group_symb = stringify(two_points)
        self.assertEqual(symm_elem_symbs, "Coo,ooC2,oosv,s,i,Soo")
        self.assertEqual(group_symb, "Dooh")

        symm_elems = [CenterRotationAxes()]
        symm_elem_symbs, group_symb = stringify(symm_elems)
        self.assertEqual(symm_elem_symbs, "ooCoo")
        self.assertEqual(group_symb, "K")

        symm_elem_symbs, group_symb = stringify(point)
        self.assertEqual(symm_elem_symbs, "ooCoo,oos,i,ooSoo")
        self.assertEqual(group_symb, "Kh")


if __name__ == "__main__":
    main()
