"""An importer class for all read in functions."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from molara.Molecule.crystal import Crystal
from molara.Molecule.crystals import Crystals

if TYPE_CHECKING:
    from os import PathLike


class FileImporterError(Exception):
    """base class for errors occurring when loading molecules from file."""


class FileFormatError(FileImporterError):
    """raised when the file format is wrong or unsupported."""


class Importer(ABC):
    """Base class for all importers."""

    def __init__(self, path: PathLike | str) -> None:
        """Initializes the Importer object."""
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
        """Initializes the Importer object."""
        super().__init__(path)

    def load(self) -> Crystals:
        """Imports a file and returns the Crystal."""
        try:
            from pymatgen.core import Structure

            structure = Structure.from_file(self.path)
            crystal = Crystal.from_pymatgen(structure)
        except ImportError as err:
            msg = "pymatgen is not installed, cannot read files"
            raise ImportError(msg) from err
        crystals = Crystals()
        crystals.add_crystal(crystal)
        return crystals


class VasprunImporter(Importer):
    """import crystal files."""

    def __init__(self, path: PathLike | str) -> None:
        """Initializes the Importer object."""
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
