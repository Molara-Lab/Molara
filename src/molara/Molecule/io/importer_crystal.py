"""An importer class for all read in functions."""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
from molara.Molecule.atom import element_symbol_to_atomic_number

if TYPE_CHECKING:
    from os import PathLike

    from molara.Molecule.crystal import Crystal


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
    def load(self) -> Crystal:
        """Reads the file in self.path."""


class CifImporter(Importer):
    """import crystal files."""

    def __init__(self, path: PathLike | str) -> None:
        """Initializes the Importer object."""
        super().__init__(path)

    def load(self) -> Crystal:
        """Imports a file and returns the Crystal."""
        try:
            from pymatgen import Structure
            structure = Structure.from_file(self.path)
            crystal = Crystal(
                atomic_numbers=structure.atomic_numbers,
                coordinates=structure.cart_coords,
                basis_vectors=structure.lattice.matrix,
            )
        except ImportError as err:
            msg = "pymatgen is not installed, cannot read .cif files"
            raise ImportError(msg) from err
        return crystal

class VasprunImporter(Importer):
    """import crystal files."""

    def __init__(self, path: PathLike | str) -> None:
        """Initializes the Importer object."""
        super().__init__(path)

    def load(self) -> Crystal:
        """Imports a file and returns the Crystal."""
        if self.path.suffix == ".xml":
            try:
                from pymatgen.io.vasp import Vasprun
                vasprun = Vasprun(self.path)
                structure = vasprun.final_structure
                crystal = Crystal(
                    atomic_numbers=structure.atomic_numbers,
                    coordinates=structure.cart_coords,
                    basis_vectors=structure.lattice.matrix,
                )
            except ImportError as err:
                msg = "pymatgen is not installed, cannot read .xml files"
                raise FileFormatError(
                    msg
                ) from err
        return crystal
