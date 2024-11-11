"""An importer class for all read in functions."""

from __future__ import annotations

import locale
import re
from abc import ABC, abstractmethod
from fnmatch import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from molara.structure.atom import element_symbol_to_atomic_number
from molara.structure.io.importer_crystal import (
    PoscarImporter,
    PymatgenImporter,
    VasprunImporter,
)
from molara.structure.molecularorbitals import MolecularOrbitals
from molara.structure.molecule import Molecule
from molara.structure.molecules import Molecules
from molara.util.constants import ANGSTROM_TO_BOHR
from molara.util.exceptions import FileFormatError, FileImporterError

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

BOHR_TO_ANGSTROM = 1 / ANGSTROM_TO_BOHR


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

        with self.path.open(encoding="utf-8") as file:
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

        with self.path.open(encoding=locale.getpreferredencoding(do_setlocale=False)) as file:
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

    def load(self) -> Molecules:  # noqa: C901 PLR0915 PLR0912
        """Read the file in self.path and creates a Molecules object."""
        molecules = Molecules()

        i = 0
        spherical_harmonics = ["[5D]", "[7F]", "[9G]"]
        spherical_order = "none"
        normalization_mode = "none"

        with self.path.open(encoding=locale.getpreferredencoding(do_setlocale=False)) as file:
            lines = file.readlines()

        while i < len(lines):
            if "Molpro" in lines[i]:
                normalization_mode = "molpro"

            if "[Title]" in lines[i]:
                i += 1
                while "[" not in lines[i]:
                    if "orca_2mkl" in lines[i]:
                        spherical_order = "molden"
                        normalization_mode = "orca"
                    if "TeraChem" in lines[i]:
                        spherical_order = "none"
                        normalization_mode = "molpro"
                    i += 1
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
                shells, exponents, coefficients = self.get_basisset(lines[i_start:i])
            for sph_key in spherical_harmonics:
                if sph_key in lines[i] and spherical_order == "none":
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
        molecules.mols[0].mos = MolecularOrbitals(labels, energies, spins, occupations)  # type: ignore[reportPossiblyUnboundVariable]
        orbital_labels = []
        for i in range(len(shells)):  # type: ignore[reportPossiblyUnboundVariable]
            molecules.mols[0].atoms[i].basis_set.basis_type = "GTO"
            molecules.mols[0].atoms[i].basis_set.generate_basis_functions(
                shells[i],  # type: ignore[reportPossiblyUnboundVariable]
                exponents[i],  # type: ignore[reportPossiblyUnboundVariable]
                coefficients[i],  # type: ignore[reportPossiblyUnboundVariable]
                molecules.mols[0].atoms[i].position,
                normalization_mode,
            )
            molecules.mols[0].basis_set.extend(
                molecules.mols[0].atoms[i].basis_set.basis_functions.values(),
            )
            orbital_labels.append(
                list(molecules.mols[0].atoms[i].basis_set.basis_functions.keys()),
            )
        molecules.mols[0].mos.basis_functions = orbital_labels
        molecules.mols[0].mos.set_mo_coefficients(
            np.array(mo_coefficients).T,  # type: ignore[reportPossiblyUnboundVariable]
            spherical_order=spherical_order,
        )
        if spherical_order == "molden":
            molecules.mols[0].mos.basis_type = "Spherical"

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
                    [float(coord) * BOHR_TO_ANGSTROM for coord in atom_info[3:6]],
                )
            else:
                coordinates.append([float(coord) for coord in atom_info[3:6]])
            i += 1

        return atomic_numbers, coordinates

    def get_basisset(  # noqa: PLR0915
        self,
        lines: list[str],
    ) -> tuple[
        list[list[str]],
        list[list[list[float]]],
        list[list[list[float]]],
    ]:
        """Read the basis set from the lines of the basisset block.

        :param lines: The lines of the basis set block.
        :return: The basis set.
        """
        if "STO" in lines[0]:
            msg = "STO type not implemented."
            raise FileFormatError(msg)
        coefficients: list = []
        exponents: list = []
        shells: list = []
        shells_check: list = ["s", "p", "d", "f", "g", "h", "i", "j", "k"]
        shells_all: list = []
        coefficients_all: list = []
        coefficients_shell: list = []
        exponents_all: list = []
        exponents_shell: list = []
        atom_idx = 0
        first = True
        last_empty_line = 0
        for i, line in enumerate(lines[2:]):
            words = line.split()
            if not words:
                if i != last_empty_line + 1:
                    last_empty_line = i
                    exponents_shell.append(exponents)
                    coefficients_shell.append(coefficients)
                    exponents = []
                    coefficients = []
                    shells_all.append(shells)
                    shells = []
                    exponents_all.append(exponents_shell)
                    exponents_shell = []
                    coefficients_all.append(coefficients_shell)
                    coefficients_shell = []
                    first = True
                    continue
                continue
            if words[0] in shells_check:
                shells.append(words[0])
                if not first:
                    exponents_shell.append(exponents)
                    coefficients_shell.append(coefficients)
                    exponents = []
                    coefficients = []
                first = False
                continue
            if words[0] == f"{atom_idx + 2}":
                atom_idx += 1
                continue
            if "D" in words[0]:
                words[0] = words[0].replace("D", "E")
            if "D" in words[1]:
                words[1] = words[1].replace("D", "E")
            exponents.append(float(words[0]))
            coefficients.append(float(words[1]))
        return shells_all, exponents_all, coefficients_all

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
        keys = ["Sym", "Ene", "Spin", "Occup"]
        regex_split_line = r"\s*=\s*|\s+"
        while i < len(lines):
            words = re.split(regex_split_line, lines[i])
            words = list(filter(None, words))
            if "Sym" in words:
                labels.append(words[1])
                i += 1
            elif "Ene" in words:
                energies.append(float(words[1]))
                i += 1
            elif "Spin" in words:
                if words[1] == "Alpha":
                    spins.append(1)
                elif words[1] == "Beta":
                    spins.append(-1)
                i += 1
            elif "Occup" in words:
                occupations.append(float(words[1]))
                i += 1
            else:
                mo_coefficients.append([])
                while words[0] not in keys:
                    mo_coefficients[-1].append(float(words[1]))
                    i += 1
                    if i == len(lines):
                        break
                    words = re.split(regex_split_line, lines[i])
                    words = list(filter(None, words))
        return mo_coefficients, labels, energies, spins, occupations


class CubeImporter(MoleculesImporter):
    """Importer from *.molden files."""

    def load(self) -> Molecules:
        """Read the file in self.path and creates a Molecules object."""
        molecules = Molecules()

        with self.path.open(encoding=locale.getpreferredencoding(do_setlocale=False)) as file:
            lines = file.readlines()

        # Get number of atoms and position of the origin
        atom_line = lines[2].split()
        n_atoms = int(atom_line[0])
        origin = np.array([float(x) * BOHR_TO_ANGSTROM for x in atom_line[1:4]], dtype=np.float64)
        number_of_values = 1
        dset_ids = True
        if n_atoms > 0:
            dset_ids = False
            try:
                number_of_values = int(atom_line[4])
            except IndexError:
                number_of_values = 1
        else:
            n_atoms = -n_atoms
        assert number_of_values == 1, "Only one value per grid point is supported"

        # Get voxel info
        number_of_voxels = np.zeros(3, dtype=np.int64)
        size_of_voxels = np.zeros((3, 3))
        for i in range(3):
            line = lines[3 + i].split()
            number_of_voxels[i] = int(line[0])
            for j in range(3):
                val = float(line[j + 1])
                if val < 0:
                    val = -val * ANGSTROM_TO_BOHR
                size_of_voxels[i, j] = val * BOHR_TO_ANGSTROM

        # Get atomic numbers and coordinates
        atomic_numbers = []
        coordinates = []
        charges = []
        for i in range(n_atoms):
            line = lines[6 + i].split()
            atomic_numbers.append(int(line[0]))
            charges.append(float(line[1]))
            coordinates.append([float(x) * BOHR_TO_ANGSTROM for x in line[2:5]])

        # Get the voxel grid data
        # Implement multiple values per voxel!
        line_index = 7 + n_atoms
        if not dset_ids:
            line_index -= 1
        all_vals = []
        while line_index < len(lines):
            line_ = lines[line_index]
            if line_ == "":
                break
            vals = [float(x) for x in line_.split()]
            all_vals += vals
            line_index += 1
        grid = np.array(all_vals).reshape(number_of_voxels)

        molecule = Molecule(np.array(atomic_numbers), np.array(coordinates))
        molecule.voxel_grid.set_grid(grid, origin, size_of_voxels)
        molecules.add_molecule(molecule)

        return molecules


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
        ".input": MoldenImporter,
        ".cube": CubeImporter,
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
