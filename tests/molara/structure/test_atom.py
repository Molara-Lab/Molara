"""Test the Atom class."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest import TestCase

import numpy as np
from numpy.testing import assert_array_equal
from numpy.typing import NDArray

from molara.structure.atom import Atom, element_symbol_to_atomic_number, elements
from molara.structure.basisset import BasisSet

if TYPE_CHECKING:
    from numpy.typing import ArrayLike

__copyright__ = "Copyright 2024, Molara"


class TestAtom(TestCase):
    """Test the Atom class."""

    def setUp(self) -> None:
        """Set up an Atom object."""
        self.position_hydrogen = [0.1324354657, 0.0897867564, 0.1029384756]
        self.position_carbon = [-0.1324354657, -0.0897867564, 0.1029384756]
        self.position_strontium = [0.1324354657, 0.0897867564, -0.1029384756]
        self.position_nitrogen = np.array([0.7564534231, 0.4657687980, 0.6574839201])
        self.position_neodymium = np.array([-0.7564534231, 0.4657687980, -0.6574839201])
        self.position_lithium = np.array([-0.7564534231, -0.4657687980, -0.6574839201])
        self.position_oxygen = [0.0, 0.0, 0.0]
        self.position_argon = [123, 45, 67]
        self.hydrogen = Atom(1, self.position_hydrogen)
        self.carbon = Atom(6, self.position_carbon)
        self.strontium = Atom(38, self.position_strontium)
        self.nitrogen = Atom(7, self.position_nitrogen)
        self.neodymium = Atom(60, self.position_neodymium)
        self.lithium = Atom(3, self.position_lithium)
        self.oxygen = Atom(8, self.position_oxygen)
        self.argon = Atom(18, self.position_argon)

    def test_setup(self) -> None:
        """Test the setup of the atom objects."""
        # values for comparison
        #     atomic numbers
        z_h, z_c, z_sr, z_n, z_nd, z_li, z_o, z_ar = 1, 6, 38, 7, 60, 3, 8, 18
        #     atomic masses
        (molmass_h, molmass_c, molmass_sr, molmass_n, molmass_nd, molmass_li, molmass_o, molmass_ar) = (
            1.00794,  # h
            12.0107,  # c
            87.62,  # sr
            14.0067,  # n
            144.242,  # nd
            6.941,  # li
            15.9994,  # o
            39.948,  # ar
        )
        #     electronegativities
        (elneg_h, elneg_c, elneg_sr, elneg_n, elneg_nd, elneg_li, elneg_o, elneg_ar) = (
            2.2,  # h
            2.55,  # c
            0.95,  # sr
            3.04,  # n
            1.14,  # nd
            0.98,  # li
            3.44,  # o
            None,  # ar
        )
        (vdwrad_h, vdwrad_c, vdwrad_sr, vdwrad_n, vdwrad_nd, vdwrad_li, vdwrad_o, vdwrad_ar) = (
            1.1,  # h
            1.70,  # c
            2.49,  # sr
            1.55,  # n
            2.39,  # nd
            1.82,  # li
            1.52,  # o
            1.88,  # ar
        )

        def general_attribute_tests(
            my_atom: Atom,
            symbol: str,
            atomic_number: int,
        ) -> None:
            assert my_atom.symbol == symbol
            assert my_atom.atomic_number == atomic_number
            assert isinstance(my_atom.basis_set, BasisSet)

        def special_attribute_tests(
            my_atom: Atom,
            position: ArrayLike,
            atomic_mass: float,
            electronegativity: float | None,
            vdw_radius: float,
        ) -> None:
            assert my_atom.atomic_mass == atomic_mass
            assert my_atom.electronegativity == electronegativity
            assert my_atom.vdw_radius == vdw_radius
            assert isinstance(my_atom.position, NDArray)
            assert_array_equal(my_atom.position, position)

        general_attribute_tests(self.hydrogen, "H", z_h)
        special_attribute_tests(self.hydrogen, self.position_hydrogen, molmass_h, elneg_h, vdwrad_h)
        general_attribute_tests(self.carbon, "C", z_c)
        special_attribute_tests(self.carbon, self.position_carbon, molmass_c, elneg_c, vdwrad_c)
        general_attribute_tests(self.strontium, "Sr", z_sr)
        special_attribute_tests(self.strontium, self.position_strontium, molmass_sr, elneg_sr, vdwrad_sr)
        general_attribute_tests(self.nitrogen, "N", z_n)
        special_attribute_tests(self.nitrogen, self.position_nitrogen, molmass_n, elneg_n, vdwrad_n)
        general_attribute_tests(self.neodymium, "Nd", z_nd)
        special_attribute_tests(self.neodymium, self.position_neodymium, molmass_nd, elneg_nd, vdwrad_nd)
        general_attribute_tests(self.lithium, "Li", z_li)
        special_attribute_tests(self.lithium, self.position_lithium, molmass_li, elneg_li, vdwrad_li)
        general_attribute_tests(self.oxygen, "O", z_o)
        special_attribute_tests(self.oxygen, self.position_oxygen, molmass_o, elneg_o, vdwrad_o)
        general_attribute_tests(self.argon, "Ar", z_ar)
        special_attribute_tests(self.argon, self.position_argon, molmass_ar, elneg_ar, vdwrad_ar)

    def test_set_position(self) -> None:
        """Test the routine for changing an atom's coordinates."""
        self.hydrogen.set_position(self.position_carbon)
        assert_array_equal(self.hydrogen.position, self.position_carbon)
        self.carbon.set_position(self.position_strontium)
        assert_array_equal(self.carbon.position, self.position_strontium)
        self.strontium.set_position(self.position_nitrogen)
        assert_array_equal(self.strontium.position, self.position_nitrogen)
        self.nitrogen.set_position(self.position_neodymium)
        assert_array_equal(self.nitrogen.position, self.position_neodymium)
        self.neodymium.set_position(self.position_lithium)
        assert_array_equal(self.neodymium.position, self.position_lithium)
        self.lithium.set_position(self.position_oxygen)
        assert_array_equal(self.lithium.position, self.position_oxygen)
        self.oxygen.set_position(self.position_argon)
        assert_array_equal(self.oxygen.position, self.position_argon)
        self.argon.set_position(self.position_hydrogen)
        assert_array_equal(self.argon.position, self.position_hydrogen)

    def test_element_symbol_to_atomic_number(self) -> None:
        """Test the routine that converts element symbols to atomic numbers (i.e., nuclear charge numbers)."""
        # test some elements directly
        z_h, z_d, z_c, z_n, z_o, z_f, z_s, z_tc, z_rn, z_sb = 1, 1, 6, 7, 8, 9, 16, 43, 86, 51
        assert element_symbol_to_atomic_number("H") == z_h
        assert element_symbol_to_atomic_number("D", h_isotopes=True) == z_d
        assert element_symbol_to_atomic_number("C") == z_c
        assert element_symbol_to_atomic_number("N") == z_n
        assert element_symbol_to_atomic_number("O") == z_o
        assert element_symbol_to_atomic_number("F") == z_f
        assert element_symbol_to_atomic_number("S") == z_s
        assert element_symbol_to_atomic_number("Tc") == z_tc
        assert element_symbol_to_atomic_number("Rn") == z_rn
        assert element_symbol_to_atomic_number("Sb") == z_sb
        # test all elements for consistency
        for i in elements:
            element_i = elements[i]
            atomic_number = element_i["Atomic no"]
            symbol = i
            assert element_symbol_to_atomic_number(symbol, h_isotopes=True) == atomic_number
