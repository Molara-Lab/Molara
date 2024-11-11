"""Contains physical constants."""

# Constants
from __future__ import annotations

from scipy import constants as const

ANGSTROM_TO_BOHR = const.angstrom / const.physical_constants["Bohr radius"][0]
