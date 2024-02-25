"""Test the Atom class."""

from __future__ import annotations

from unittest import TestCase

import numpy as np
from molara.Structure.atom import Atom
from numpy.testing import assert_array_equal

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
        z_h, z_c, z_sr, z_n, z_nd, z_li, z_o, z_ar = 1, 6, 38, 7, 60, 3, 8, 18
        assert self.hydrogen.atomic_number == z_h
        assert self.hydrogen.symbol == "H"
        assert_array_equal(self.hydrogen.position, self.position_hydrogen)
        assert self.carbon.atomic_number == z_c
        assert self.carbon.symbol == "C"
        assert_array_equal(self.carbon.position, self.position_carbon)
        assert self.strontium.atomic_number == z_sr
        assert self.strontium.symbol == "Sr"
        assert_array_equal(self.strontium.position, self.position_strontium)
        assert self.nitrogen.atomic_number == z_n
        assert self.nitrogen.symbol == "N"
        assert_array_equal(self.nitrogen.position, self.position_nitrogen)
        assert self.neodymium.atomic_number == z_nd
        assert self.neodymium.symbol == "Nd"
        assert_array_equal(self.neodymium.position, self.position_neodymium)
        assert self.lithium.atomic_number == z_li
        assert self.lithium.symbol == "Li"
        assert_array_equal(self.lithium.position, self.position_lithium)
        assert self.oxygen.atomic_number == z_o
        assert self.oxygen.symbol == "O"
        assert_array_equal(self.oxygen.position, self.position_oxygen)
        assert self.argon.atomic_number == z_ar
        assert self.argon.symbol == "Ar"
        assert_array_equal(self.argon.position, self.position_argon)

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
