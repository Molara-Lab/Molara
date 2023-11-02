"""An importer class for all read in functions."""
from __future__ import annotations
from abc import ABC, abstractmethod
from os import PathLike
from pathlib import Path
from typing import List, Mapping

import numpy as np

from molara.Molecule.atom import element_symbol_to_atomic_number
from molara.Molecule.molecule import Molecule
from molara.Molecule.molecules import Molecules


class FileImporterError(Exception):
    '''base class for errors occuring when loading molecules from file'''

class FileFormatError(FileImporterError):
    '''raised when the file format is wrong or unsupported'''

class MoleculesImporter(ABC):
    '''base class for importers loading molecules from files'''

    def __init__(self, path: PathLike | str) -> None:
        super().__init__()

        self.path = Path(path)

    @abstractmethod
    def load(self) -> Molecules:
        '''reads the file in self.path and create a Molecules object from its
        contents'''

class XyzImporter(MoleculesImporter):
    '''
    import xyz files
    '''

    def load(self) -> Molecules:
        molecules = Molecules()

        with open(self.path, encoding='utf-8') as file:
            lines = file.readlines()

            num_atoms = int(lines[0])

            atomic_numbers = []

            coordinates = []

            for line in lines[2 : 2 + num_atoms]:
                atom_info = line.split()

                if atom_info[0].isnumeric():
                    atomic_numbers.append(int(atom_info[0]))

                else:
                    atomic_numbers.append(element_symbol_to_atomic_number(atom_info[0]))

                coordinates.append([float(coord) for coord in atom_info[1:4]])

        molecules.add_molecule(Molecule(np.array(atomic_numbers), np.array(coordinates), lines[1]))
        
        # Read in for a single xyz file
        # Goes on if file has more than one structure stored
        if (len(lines) > 2 + num_atoms) and lines[2 + num_atoms].replace(
            "\n",
            "",
        ).isdigit():
            not_finished = True

            max_mols = 10000

            xyz_len = 0

            while not_finished and max_mols > molecules.num_mols:
                atomic_numbers = []
                coordinates = []

                xyz_len += 2 + num_atoms

                for line in lines[2 + xyz_len : 2 + num_atoms + xyz_len]:
                    atom_info = line.split()

                    if atom_info[0].isnumeric():
                        atomic_numbers.append(int(atom_info[0]))

                    else:
                        atomic_numbers.append(element_symbol_to_atomic_number(atom_info[0]))

                    coordinates.append([float(coord) for coord in atom_info[1:4]])

                if not (
                    (len(lines) > 2 + xyz_len + num_atoms) and lines[xyz_len + 2 + num_atoms].replace("\n", "").isdigit()
                ):
                    not_finished = False

                molecules.add_molecule(
                    Molecule(np.array(atomic_numbers), np.array(coordinates), lines[1 + xyz_len]),
                )

        file.close()

        return molecules

class CoordImporter(MoleculesImporter):
    '''importer fro *.coord files'''

    def load(self) -> Molecules:
        molecules = Molecules()

        with open(self.path) as file:
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

        molecules.add_molecule(Molecule(np.array(atomic_numbers), np.array(coordinates)))

        return molecules

class QmImporter(MoleculesImporter):
    '''importer for output files of various quantum chemistry programs'''

    def __init__(self, path: PathLike | str) -> None:
        import cclib
        super().__init__(path)

        self._ccparser = cclib.io.ccopen(self.path)

        if self._ccparser is None:
            raise FileFormatError('Not a QM output file.')

    def load(self) -> Molecules:
        data = self._ccparser.parse()

        mols: List[Molecule] = self._get_geometries(data)
        energies = self._get_electronic_energies_in_hartree(data)

        molecules = Molecules()
        molecules.mols = mols
        molecules.energies = energies if energies is not None else []

        return molecules

    def _get_electronic_energies_in_hartree(self, cclib_data) -> np.ndarray | None:
        # conversion factor used by the cclib package
        CCLIB_EV_IN_HARTREE = 27.21138505

        try:
            energy = np.array(cclib_data.scfenergies)

            energy /= CCLIB_EV_IN_HARTREE

            return energy
        except AttributeError as err:
            return None

    def _get_geometries(self, cclib_data) -> List[Molecule]:
        try: 
            atoms = cclib_data.atomnos

            mols = [
                Molecule(atoms, coords)
                for coords in cclib_data.atomcoords
            ]

            return mols
        except AttributeError as err:
            raise FileImporterError('Could not read atomic coordinates.')

class GeneralImporter(MoleculesImporter):
    '''tries to determine the file format and calls the correct importer'''

    _IMPORTER_BY_SUFFIX: Mapping[str, MoleculesImporter] = {
        '.xyz': XyzImporter,
        '.coord': CoordImporter
    }

    def __init__(self, path: PathLike | str) -> None:
        super().__init__(path)

        suffix = self.path.suffix

        try:
            self._importer = self._IMPORTER_BY_SUFFIX[suffix](path)
        except KeyError:
            try:
                self._importer = QmImporter(path)
            except FileFormatError:
                raise FileFormatError('Could not open file.')


    def load(self) -> Molecules:
        return self._importer.load()
