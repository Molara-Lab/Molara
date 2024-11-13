"""Contains the Atom class and a dictionary of elements."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from molara.structure.basisset import BasisSet

if TYPE_CHECKING:
    from numpy.typing import ArrayLike

__copyright__ = "Copyright 2024, Molara"

with Path(__file__).absolute().parent.joinpath("periodic_table.json").open(encoding="utf-8") as ptable_json:
    _pt_data = json.load(ptable_json)

with Path(__file__).absolute().parent.joinpath("atom_colors.json").open(encoding="utf-8") as atom_colors_json:
    _atom_colors = json.load(atom_colors_json)


class Atom:
    """Creates an Atom object."""

    def __init__(self, atomic_number: int, position: ArrayLike) -> None:
        """Create an Atom object.

        :param atomic_number: atomic number (nuclear charge number) of the atom
        :param position: cartesian coordinates of atom location
        """
        self.symbol = atomic_number_to_symbol(atomic_number)
        self.name = _pt_data[self.symbol]["Name"]
        self.atomic_number = atomic_number
        self.atomic_mass = _pt_data[self.symbol]["Atomic mass"]
        try:
            self.electronegativity = _pt_data[self.symbol]["X"]
        except KeyError:
            self.electronegativity = None
        jmol_color = (
            np.array(
                tuple(int(_atom_colors["Jmol"][self.symbol].strip("#")[i : i + 2], 16) for i in (0, 2, 4)),
                dtype=np.float64,
            )
            / 255
        )
        cpk_color = np.array(_atom_colors["CPK_ase"][self.symbol], dtype=np.float64)
        self.color = {
            "CPK": cpk_color,
            "Jmol": jmol_color,
        }
        self.vdw_radius = _pt_data[self.symbol]["Van der waals radius"]
        self.basis_set = BasisSet()
        self.position = np.array([])
        self.set_position(position)

    def set_position(self, position: ArrayLike) -> None:
        """Set the position of the atom and update the basis set positions.

        :param position: new position of the atom
        :return: None
        """
        position_array = np.array(position, dtype=np.float64)
        if position_array.shape != (3,):
            msg = "Position must be a 3D coordinate"
            raise ValueError(msg)
        self.position = position_array
        for basis_function in self.basis_set.basis_functions.values():
            basis_function.position = self.position


def element_symbol_to_atomic_number(symbol: str, h_isotopes: bool = False) -> int:
    """Define a dictionary mapping element symbols to atomic numbers.

    :param symbol: atomic symbol (element) of the atom
    :param h_isotopes: include hydrogen isotopes (deuterium and tritium) in the dictionary.
    :return: atomic number (nuclear charge number) of the atom
    """
    symbol_to_atomic_number = {element: _pt_data[element]["Atomic no"] for element in _pt_data}
    if not h_isotopes:
        symbol_to_atomic_number.pop("D")
        symbol_to_atomic_number.pop("T")
    return symbol_to_atomic_number.get(symbol, 0)


def atomic_number_to_symbol(atomic_number: int) -> str:
    """Define a dictionary mapping element symbols to atomic numbers.

    :param atomic_number: atomic number (nuclear charge number) of the atom
    """
    symbol_to_atomic_number = {
        _pt_data[element]["Atomic no"]: element for element in _pt_data if element not in ["D", "T"]
    }
    return symbol_to_atomic_number[atomic_number]


elements = _pt_data
