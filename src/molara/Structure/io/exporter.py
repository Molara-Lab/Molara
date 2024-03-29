"""An exporter module to write chemical structures to files."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

from molara.Structure.atom import elements

if TYPE_CHECKING:
    from collections.abc import Mapping
    from os import PathLike
    from typing import Any

    from molara.Molecule.structure import Structure


__copyright__ = "Copyright 2024, Molara"


class FileExporterError(Exception):
    """Base class for errors occurring when loading molecules from file."""


class FileFormatError(FileExporterError):
    """Raised when the file format is wrong or unsupported."""


class StructureExporter(ABC):
    """Base class for structure exporters."""

    def __init__(self, path: PathLike | str) -> None:
        """Instantiate object.

        :param path: output file path
        """
        super().__init__()
        self.path = Path(path)

    @abstractmethod
    def write_structure(self, structure: Structure) -> None:
        """Write the structure in some given format into the output file.

        :param structure: Structure object to be exported to file
        """


class XyzExporter(StructureExporter):
    """Export xyz files."""

    def write_structure(self, structure: Structure) -> None:
        """Write given structure into file with xyz format.

        :param structure: Structure object to be exported to xyz-file
        """
        lines = [
            elements[atom.atomic_number]["symbol"]
            + "  "
            + rf"{atom.position[0]}  {atom.position[1]}  {atom.position[2]}"
            for atom in structure.atoms
        ]
        with open(self.path, "w") as file:
            file.write(rf"{len(structure.atoms)}" + "\n")
            file.write("This xyz file was generated automatically by Molara!\n")
            file.write("\n".join(lines))


class GeneralExporter(StructureExporter):
    """Tries to determine the file format and calls the correct exporter."""

    _IMPORTER_BY_SUFFIX: Mapping[str, Any] = {
        ".xyz": XyzExporter,
    }

    def __init__(self, path: PathLike | str) -> None:
        """Try to determine the file format and calls the correct exporter.

        :param path: output file path
        """
        super().__init__(path)

        suffix = self.path.suffix

        try:
            self._importer = self._IMPORTER_BY_SUFFIX[suffix](path)
        except KeyError:
            try:
                self._importer = XyzExporter(path)
            except FileFormatError as err:
                msg = "Could not open file."
                raise FileFormatError(msg) from err

    def write_structure(self, structure: Structure) -> None:
        """Write given structure into file with given format.

        :param structure: Structure object to be exported to file
        """
        return self._importer.write_structure(structure)
