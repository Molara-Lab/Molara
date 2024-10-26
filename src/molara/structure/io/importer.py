"""An importer class for all read in functions."""

from __future__ import annotations

import locale
from abc import ABC, abstractmethod
from fnmatch import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from molara.structure.atom import element_symbol_to_atomic_number
from molara.structure.io.importer_crystal import PoscarImporter, PymatgenImporter, VasprunImporter
from molara.structure.molecule import Molecule
from molara.structure.molecules import Molecules
from molara.structure.mos import Mos

if TYPE_CHECKING:
    from collections.abc import Mapping
    from os import PathLike
    from typing import Any

    from molara.molecule.crystals import Crystals

    try:
        from cclib.data import ccData
    except ImportError:
        ccData = Any  # noqa: N816

__copyright__ = "Copyright 2024, Molara"

bohr_to_angstrom = 5.29177210903e-1


class FileImporterError(Exception):
    """Base class for errors occurring when loading molecules from file."""


class FileFormatError(FileImporterError):
    """Raised when the file format is wrong or unsupported."""


class MoleculesImporter(ABC):
    """Base class for importers loading molecules from files."""

    def __init__(self, path: PathLike | str) -> None:
        """Instantiate MoleculesImporter object.

        :param path: input file path
        """
        super().__init__()

        self.path = Path(path)

    @abstractmethod
    def load(self) -> Molecules | Crystals:
        """Read the file in self.path and creates a Molecules object."""


class XyzImporter(MoleculesImporter):
    """Import xyz files."""

    def _molecule_from_xyz(self, lines: list[str]) -> Molecule:
        """Create a Molecule object from the lines of an xyz file.

        :param lines: The lines of the xyz file.
        :return: The Molecule object.
        """
        num_atoms = int(lines[0])
        atomic_numbers = []
        coordinates = []

        for line in lines[2 : 2 + num_atoms]:
            atom_info = line.split()
            if atom_info[0].isnumeric():
                atomic_numbers.append(int(atom_info[0]))
            else:
                token = atom_info[0].capitalize()
                atomic_numbers.append(element_symbol_to_atomic_number(token))
            coordinates.append([float(coord) for coord in atom_info[1:4]])

        return Molecule(np.array(atomic_numbers), np.array(coordinates), lines[1])

    def load(self) -> Molecules:
        """Read the file in self.path and creates a Molecules object."""
        molecules = Molecules()

        with open(self.path, encoding="utf-8") as file:
            lines = file.readlines()

        num_atoms = int(lines[0])
        finished = False
        max_mols = int(1e100)
        start_line = 0
        while not finished and max_mols >= molecules.num_mols:
            end_line = start_line + num_atoms + 2
            molecules.add_molecule(
                self._molecule_from_xyz(lines[start_line:end_line]),
            )
            finished = (
                start_line + 2 + num_atoms >= len(lines) or not lines[start_line + 2 + num_atoms].strip().isdigit()
            )
            start_line = end_line
        return molecules


class CoordImporter(MoleculesImporter):
    """Importer from *.coord files."""

    def load(self) -> Molecules:
        """Read the file in self.path and creates a Molecules object."""
        molecules = Molecules()

        with open(self.path, encoding=locale.getpreferredencoding(do_setlocale=False)) as file:
            lines = file.readlines()  # To skip first row

        atomic_numbers = []

        coordinates = []

        for line in lines[1:]:
            if "$" in line:
                break

            atom_info = line.split()
            if atom_info[-1].isnumeric():
                atomic_numbers.append(int(atom_info[-1]))
            else:
                atom_info[-1] = atom_info[-1].capitalize()
                atomic_numbers.append(element_symbol_to_atomic_number(atom_info[-1]))
            coordinates.append([float(coord) * 0.529177249 for coord in atom_info[:3]])

        molecules.add_molecule(
            Molecule(np.array(atomic_numbers), np.array(coordinates)),
        )

        return molecules


class MoldenImporter(MoleculesImporter):
    """Importer from *.molden files."""

    def load(self) -> Molecules:  # noqa: C901
        """Read the file in self.path and creates a Molecules object."""
        molecules = Molecules()

        with open(self.path, encoding=locale.getpreferredencoding(do_setlocale=False)) as file:
            lines = file.readlines()

        i = 0
        spherical_harmonics = ["[5D]", "[7F]", "[9G]"]

        while i < len(lines):
            if "[Atoms]" in lines[i]:
                i_start = i
                i += 1
                while "[" not in lines[i]:
                    i += 1
                atomic_numbers, coordinates = self.get_atoms(lines[i_start:i])
            if "[GTO]" in lines[i] or "[STO]" in lines[i]:
                i_start = i
                i += 1
                while "[" not in lines[i]:
                    i += 1
                basisset = self.get_basisset(lines[i_start:i])
            for sph_key in spherical_harmonics:
                if sph_key in lines[i]:
                    msg = "Spherical Harmonics not implemented."
                    raise FileFormatError(msg)
            if "[MO]" in lines[i]:
                i_start = i
                i += 1
                while "[" not in lines[i]:
                    i += 1
                    if i == len(lines):
                        break
                (
                    mo_coefficients,
                    labels,
                    energies,
                    spins,
                    occupations,
                ) = self.get_mo_coefficients(lines[i_start:i])
            i += 1

        molecules.add_molecule(
            Molecule(np.array(atomic_numbers), np.array(coordinates)),  # type: ignore[reportPossiblyUnboundVariable]
        )
        molecules.mols[0].mos = Mos(labels, energies, spins, occupations)  # type: ignore[reportPossiblyUnboundVariable]
        molecules.mols[0].mos.coefficients = np.array(mo_coefficients)  # type: ignore[reportPossiblyUnboundVariable]

        # WATCH OUT ONLY FOR GTOs!!!!!!!!
        for i, atom in enumerate(basisset):  # type: ignore[reportPossiblyUnboundVariable]
            molecules.mols[0].atoms[i].basis_set.basis_type = "GTO"
            molecules.mols[0].atoms[i].basis_set.generate_orbitals(
                atom["shells"],
                atom["exponents"],
                atom["coefficients"],
                molecules.mols[0].atoms[i].position,
            )
            molecules.mols[0].aos.extend(
                molecules.mols[0].atoms[i].basis_set.orbitals_list,
            )
        return molecules

    def get_atoms(self, lines: list[str]) -> tuple[list[int], list[list[float]]]:
        """Read the atomic numbers and coordinates from the lines of the atoms block.

        :param lines: The lines of the atom block.
        :return: The atomic numbers and coordinates.
        """
        atomic_numbers = []
        coordinates = []

        if "Angs" in lines[0]:
            angstrom = True
        elif "AU" in lines[0]:
            angstrom = False
        else:
            msg = "No unit specified in molden Atoms input."
            raise FileFormatError(msg)
        i = 1
        while i < len(lines):
            atom_info = lines[i].split()
            atomic_numbers.append(int(atom_info[2]))
            if not angstrom:
                coordinates.append(
                    [float(coord) * bohr_to_angstrom for coord in atom_info[3:6]],
                )
            else:
                coordinates.append([float(coord) for coord in atom_info[3:6]])
            i += 1

        return atomic_numbers, coordinates

    def get_basisset(self, lines: list[str]) -> list:  # noqa: C901
        """Read the basis set from the lines of the basisset block.

        :param lines: The lines of the basis set block.
        :return: The basis set.
        """
        if "STO" in lines[0]:
            msg = "STO type not implemented."
            raise FileFormatError(msg)
        i = 2
        coefficients = []
        exponents = []
        shells = ["s", "p", "d", "f", "g", "h", "i", "j", "k"]
        basisset: list = [
            {
                "shells": [],
                "exponents": [],
                "coefficients": [],
            },
        ]
        new_basisset_dict: dict = {
            "shells": [],
            "exponents": [],
            "coefficients": [],
        }
        words = lines[i].split()
        while i < len(lines):
            if not words:  # check if end of gto block
                while not words:
                    i += 1
                    if i == len(lines):
                        break
                    words = lines[i].split()
                if i == len(lines):
                    break
                basisset.append(new_basisset_dict)
                i += 1  # skip line after empty line
                words = lines[i].split()
            if words[0] == "sp":
                msg = "sp type not implemented."
                raise FileFormatError(msg)
            if words[0] in shells:
                basisset[-1]["shells"].append(words[0])
            i += 1
            words = lines[i].split()
            while words and words[0] not in shells:
                if "D" in words[0]:
                    words[0] = words[0].replace("D", "E")
                if "D" in words[1]:
                    words[1] = words[1].replace("D", "E")
                exponents.append(float(words[0]))
                coefficients.append(float(words[1]))
                i += 1
                words = lines[i].split()
            basisset[-1]["exponents"].append(exponents)
            basisset[-1]["coefficients"].append(coefficients)
            exponents = []
            coefficients = []

        return basisset

    def get_mo_coefficients(
        self,
        lines: list[str],
    ) -> tuple[list[list[float]], list[str], list[float], list[int], list[float]]:
        """Read the MO coefficients from the lines of the MO block.

        :param lines: The lines of the MO block.
        :return: The MO coefficients.
        """
        i = 1
        mo_coefficients: list = []
        labels = []
        energies = []
        spins = []
        occupations = []
        while i < len(lines):
            words = lines[i].split()
            if words[0] == "Sym=":
                labels.append(words[1])
                i += 1
                words = lines[i].split()
            if words[0] == "Ene=":
                energies.append(float(words[1]))
                i += 1
                words = lines[i].split()
            if words[0] == "Spin=":
                if words[1] == "Alpha":
                    spins.append(1)
                elif words[1] == "Beta":
                    spins.append(-1)
                i += 1
                words = lines[i].split()
            if words[0] == "Occup=":
                occupations.append(float(words[1]))
                i += 1
                words = lines[i].split()
            mo_coefficients.append([])
            while words[0] != "Sym=":
                mo_coefficients[-1].append(float(words[1]))
                i += 1
                if i == len(lines):
                    break
                words = lines[i].split()
        return mo_coefficients, labels, energies, spins, occupations


class QmImporter(MoleculesImporter):
    """importer for output files of various quantum chemistry programs."""

    def __init__(self, path: PathLike | str) -> None:
        """Instantiate QmImporter object.

        :param path: input file path
        """
        try:
            import cclib
        except ImportError as err:
            msg = "Could not import cclib."
            raise ImportError(msg) from err

        super().__init__(path)

        self._ccparser = cclib.io.ccopen(self.path)

        if self._ccparser is None:
            msg = "Not a QM output file."
            raise FileFormatError(msg)

    def load(self) -> Molecules:
        """Read the file in self.path and creates a Molecules object."""
        data = self._ccparser.parse()

        mols: list[Molecule] = self._get_geometries(data)
        energies = self._get_electronic_energies_in_hartree(data)

        molecules = Molecules()
        molecules.mols = mols
        molecules.energies = list(energies) if energies is not None else []

        return molecules

    def _get_electronic_energies_in_hartree(
        self,
        cclib_data: ccData,
    ) -> np.ndarray | None:
        """Convert cclib energy to hartree.

        :param cclib_data: cclib data
        """
        # conversion factor used by the cclib package
        cclib_ev_in_hartree = 27.21138505

        try:
            energy = np.array(cclib_data.scfenergies)

            energy /= cclib_ev_in_hartree

        except AttributeError:
            return None
        return energy

    def _get_geometries(self, cclib_data: ccData) -> list[Molecule]:
        """Extract geometries from cclib data.

        :param cclib_data: cclib data
        """
        try:
            atoms = cclib_data.atomnos

            mols = [Molecule(atoms, coords) for coords in cclib_data.atomcoords]

        except AttributeError as err:
            msg = "Could not read atomic coordinates."
            raise FileImporterError(msg) from err

        return mols


class GeneralImporter(MoleculesImporter):
    """Tries to determine the file format and calls the correct importer."""

    _IMPORTER_BY_SUFFIX: Mapping[str, Any] = {
        ".xyz": XyzImporter,
        ".trj": XyzImporter,
        ".log": XyzImporter,
        ".coord": CoordImporter,
        ".POSCAR": PoscarImporter,
        ".CONTCAR": PoscarImporter,
        ".vasp": PoscarImporter,
        ".cif": PymatgenImporter,
        ".xml": VasprunImporter,
        ".molden": MoldenImporter,
    }

    def __init__(
        self,
        path: PathLike | str,
    ) -> None:
        """Instantiate GeneralImporter object.

        :param path: input file path
        """
        super().__init__(path)

        suffix = self.path.suffix
        fname = self.path.name

        try:
            if suffix:
                self._importer = self._IMPORTER_BY_SUFFIX[suffix](path)
            elif fnmatch(fname, "*POSCAR*") or fnmatch(fname, "*CONTCAR*"):
                self._importer = PoscarImporter(path)
            elif fnmatch(fname, "*.json*") or fnmatch(fname, "*.mson*"):
                self._importer = PymatgenImporter(path)
        except KeyError:
            # Instead of the cclib import, we should open a dialog window to manually select the importer.
            try:
                self._importer = QmImporter(path)
            except FileFormatError as err:
                msg = "Could not open file."
                raise FileFormatError(msg) from err
            except ImportError as err:
                msg = "Missing modules. Could not open file."
                raise ImportError(msg) from err

    def load(self) -> Molecules | Crystals:
        """Read the file in self.path and creates a Molecules object."""
        return self._importer.load()
