"""An importer class for all read in functions."""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from molara.Structure.atom import element_symbol_to_atomic_number
from molara.Structure.crystal import Crystal
from molara.Structure.crystals import Crystals

if TYPE_CHECKING:
    from os import PathLike


class FileImporterError(Exception):
    """base class for errors occurring when loading molecules from file."""


class FileFormatError(FileImporterError):
    """raised when the file format is wrong or unsupported."""


def robust_split(text: str) -> list[str]:
    """Split a text into its components (separated by any kinds of space characters) with regular expressions.

    :param text: text to be split up
    """
    return re.split(r"\s+", text)


class Importer(ABC):
    """Base class for all importers."""

    def __init__(self, path: PathLike | str) -> None:
        """Initialize the Importer object.

        :param path: input file path
        """
        super().__init__()

        self.path = Path(path)

    @abstractmethod
    def load(self) -> Crystals:
        """Read the file in self.path."""


class PymatgenImporter(Importer):
    """import crystal files.

    This class is a wrapper around the pymatgen Structure class. Supported file formats include cif, poscar, cssr,
    pymatgen's json format, and pymatgen's yaml format.
    """

    def __init__(self, path: PathLike | str) -> None:
        """Initialize the Importer object.

        :param path: input file path
        """
        super().__init__(path)

    def load(self) -> Crystals:
        """Import a file and returns the Crystal."""
        try:
            from pymatgen.core import Structure

            structure = Structure.from_file(self.path)
            crystal = Crystal.from_pymatgen(structure, supercell_dims=[1, 1, 1])
        except ImportError as err:
            msg = "pymatgen is not installed and internal importer not successful, cannot read files"
            raise ImportError(msg) from err
        crystals = Crystals()
        crystals.add_crystal(crystal)
        return crystals


class PoscarImporter(Importer):
    """import crystal files.

    This class can be used to import poscar files. It tries the pymatgen import first.
    """

    def __init__(
        self,
        path: PathLike | str,
    ) -> None:
        """Initialize the Importer object.

        :param path: input file path
        :param supercell_dims: side lengths of the supercell in terms of the cell constants
        """
        super().__init__(path)

    def load(self) -> Crystals:
        """Import a file and returns the Crystal."""
        try:
            from monty.io import zopen
            from pymatgen.core import Structure as PymatgenStructure
        except ImportError:
            PymatgenStructure = None  # noqa: N806

        if PymatgenStructure is not None:
            with zopen(self.path, "rt", errors="replace") as f:
                contents = f.read()
            structure = PymatgenStructure.from_str(contents, fmt="poscar")
            crystal = Crystal.from_pymatgen(structure, supercell_dims=[1, 1, 1])
        else:
            with open(self.path) as file:
                lines = [line.strip() for line in file]
            header_length = 8
            if not len(lines) > header_length:
                msg = "Error: faulty formatting of the POSCAR file."
                raise FileFormatError(msg)
            scale_, latvecs_ = lines[1], lines[2:5]
            species_, numbers_, mode = lines[5:8]
            positions_ = lines[8:]
            try:
                scale = float(scale_)
                basis_vectors = [[float(component) for component in robust_split(latvec_)[:3]] for latvec_ in latvecs_]
                species = robust_split(species_)
                numbers = [int(num) for num in robust_split(numbers_)]
                if len(positions_) == sum(numbers) * 2 + 1:
                    positions_ = positions_[0 : sum(numbers)]
                positions = [[float(component) for component in robust_split(pos)[:3]] for pos in positions_]
            except ValueError as err:
                msg = "Error: faulty formatting of the POSCAR file."
                raise FileFormatError(msg) from err
            if (
                len(numbers) != len(species)
                or len(positions) != sum(numbers)
                or not mode.lower().startswith(("d", "c", "k"))  # Either cartesian or direct coords
            ):
                msg = "Error: faulty formatting of the POSCAR file."
                raise FileFormatError(msg)

            # For cartesian coordinates, convert to fractional coordinates
            if mode.lower().startswith(("c", "k")):
                positions = [np.dot(np.linalg.inv(basis_vectors).T, position).tolist() for position in positions]
            atomic_numbers = [element_symbol_to_atomic_number(symb) for symb in species]

            atomic_numbers_extended = []
            for num, an in zip(numbers, atomic_numbers):
                atomic_numbers_extended.extend(num * [an])

            scale_unitcell_to_volume = scale < 0
            if scale_unitcell_to_volume:
                _old_volume = Crystal.calc_volume_unitcell(basis_vectors)
                scale = np.cbrt((-scale) / _old_volume)

            crystal = Crystal(
                atomic_numbers_extended,
                positions,
                (scale * np.array(basis_vectors)).tolist(),
                supercell_dims=[1, 1, 1],
            )

        crystals = Crystals()
        crystals.add_crystal(crystal)
        return crystals


class VasprunImporter(Importer):
    """import crystal files."""

    def __init__(self, path: PathLike | str) -> None:
        """Initialize the Importer object.

        :param path: input file path
        """
        super().__init__(path)

    def load(self) -> Crystals:
        """Import a file and returns the Crystal."""
        try:
            from pymatgen.io.vasp import Vasprun

            vasprun = Vasprun(self.path)
            structure = vasprun.final_structure
            crystal = Crystal.from_pymatgen(structure, supercell_dims=[1, 1, 1])
        except ImportError as err:
            msg = "pymatgen is not installed, cannot read vasprun.xml files"
            raise FileFormatError(
                msg,
            ) from err
        crystals = Crystals()
        crystals.add_crystal(crystal)
        return crystals
