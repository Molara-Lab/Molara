"""An importer class for all read in functions."""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import numpy as np
from molara.Structure.atom import element_symbol_to_atomic_number
from molara.Structure.crystal import Crystal
from molara.Structure.crystals import Crystals

if TYPE_CHECKING:
    from collections.abc import Sequence
    from os import PathLike


class FileImporterError(Exception):
    """base class for errors occurring when loading molecules from file."""


class FileFormatError(FileImporterError):
    """raised when the file format is wrong or unsupported."""


class Importer(ABC):
    """Base class for all importers."""

    def __init__(self, path: PathLike | str) -> None:
        """Initializes the Importer object.

        :param path: input file path
        """
        super().__init__()

        self.path = Path(path)

    @abstractmethod
    def load(self) -> Crystals:
        """Reads the file in self.path."""


class PymatgenImporter(Importer):
    """import crystal files.

    This class is a wrapper around the pymatgen Structure class. Supported file formats include cif, poscar, cssr,
    pymatgen's json format, and pymatgen's yaml format.
    """

    def __init__(self, path: PathLike | str) -> None:
        """Initializes the Importer object.

        :param path: input file path
        """
        super().__init__(path)

    def load(self) -> Crystals:
        """Imports a file and returns the Crystal."""
        try:
            from pymatgen.core import Structure

            structure = Structure.from_file(self.path)
            crystal = Crystal.from_pymatgen(structure)
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
        supercell_dims: Annotated[Sequence[int], 3] = [1, 1, 1],
    ) -> None:
        """Initializes the Importer object.

        :param path: input file path
        :param supercell_dims: side lengths of the supercell in terms of the cell constants
        """
        super().__init__(path)
        self.supercell_dims = supercell_dims

    def load(self) -> Crystals:
        """Imports a file and returns the Crystal."""
        try:
            from monty.io import zopen
            from pymatgen.core import Structure
        except ImportError:
            Structure = None  # noqa: N806

        if Structure is not None:
            with zopen(self.path, "rt", errors="replace") as f:
                contents = f.read()
            structure = Structure.from_str(contents, fmt="poscar")
            crystal = Crystal.from_pymatgen(structure)
        else:
            with open(self.path) as file:
                lines = file.readlines()
            header_length = 9
            if not len(lines) >= header_length:
                msg = "Error: faulty formatting of the POSCAR file."
                raise FileFormatError(msg)
            scale_, latvec_a_, latvec_b_, latvec_c_ = lines[1:5]
            species_ = lines[5].strip()
            numbers_ = lines[6]
            mode = lines[7].strip()
            positions_ = lines[8:]
            try:
                scale = float(scale_)
                latvec_a = [float(component) for component in latvec_a_.split()[:3]]
                latvec_b = [float(component) for component in latvec_b_.split()[:3]]
                latvec_c = [float(component) for component in latvec_c_.split()[:3]]
                species = re.split(r"\s+", species_)
                numbers = [int(num) for num in numbers_.split()]
                if len(positions_) == sum(numbers) * 2 + 1:
                    positions_ = positions_[0 : sum(numbers)]
                positions = [np.fromstring(pos, sep=" ").tolist()[:3] for pos in positions_]
                basis_vectors = [latvec_a, latvec_b, latvec_c]
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

            crystal = Crystal(
                atomic_numbers_extended,
                positions,
                [scale * np.array(bv, dtype=float) for bv in basis_vectors],
                self.supercell_dims,
            )

        crystals = Crystals()
        crystals.add_crystal(crystal)
        return crystals


class VasprunImporter(Importer):
    """import crystal files."""

    def __init__(self, path: PathLike | str) -> None:
        """Initializes the Importer object.

        :param path: input file path
        """
        super().__init__(path)

    def load(self) -> Crystals:
        """Imports a file and returns the Crystal."""
        try:
            from pymatgen.io.vasp import Vasprun

            vasprun = Vasprun(self.path)
            structure = vasprun.final_structure
            crystal = Crystal.from_pymatgen(structure)
        except ImportError as err:
            msg = "pymatgen is not installed, cannot read vasprun.xml files"
            raise FileFormatError(
                msg,
            ) from err
        crystals = Crystals()
        crystals.add_crystal(crystal)
        return crystals