"""Contains physical constants."""

# Constants
from __future__ import annotations

from scipy import constants as const

__copyright__ = "Copyright 2024, Molara"
ANGSTROM_TO_BOHR = const.angstrom / const.physical_constants["Bohr radius"][0]
