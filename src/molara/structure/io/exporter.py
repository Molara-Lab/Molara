"""An exporter module to write chemical structures to files."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
    from os import PathLike
    from typing import Any

    from molara.molecule.structure import Structure


__copyright__ = "Copyright 2024, Molara"


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
            atom.symbol + "  " + rf"{atom.position[0]}  {atom.position[1]}  {atom.position[2]}"
            for atom in structure.atoms
        ]
        try:
            with self.path.open("w") as file:
                file.write(rf"{len(structure.atoms)}" + "\n")
                file.write("This xyz file was generated automatically by Molara!\n")
                file.write("\n".join(lines))
        except FileNotFoundError as err:
            msg = "File path for the export is invalid."
            raise FileNotFoundError(msg) from err


class GeneralExporter(StructureExporter):
    """Tries to determine the file format and calls the correct exporter."""

    _EXPORTER_BY_SUFFIX: Mapping[str, Any] = {
        ".xyz": XyzExporter,
    }

    def __init__(self, path: PathLike | str) -> None:
        """Try to determine the file format and calls the correct exporter.

        :param path: output file path
        """
        super().__init__(path)

        suffix = self.path.suffix

        try:
            self._exporter = self._EXPORTER_BY_SUFFIX[suffix](path)
        except KeyError:
            self._exporter = XyzExporter(path)

    def write_structure(self, structure: Structure) -> None:
        """Write given structure into file with given format.

        :param Structure: structure object to be exported to file
        """
        return self._exporter.write_structure(structure)

    @property
    def exporter(self) -> StructureExporter:
        """Return the exporter object."""
        return self._exporter
