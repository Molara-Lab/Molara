'''
This module contains functions to import molecular geometries, etc. from
different file formats
'''


from abc import ABC, abstractmethod
import os
import pathlib
from molara.Molecule.Atom import element_symbol_to_atomic_number
from molara.Molecule.Molecule import Molecule

class ParsingError(Exception):
    '''base class for all parsing related errors'''

def read_xyz(file_path : str) -> Molecule:
    '''
    read an xyz file
    '''

    with open(file_path, 'r') as file:
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

    file.close()

    return Molecule(atomic_numbers, coordinates)

def read_coord(file_path : str) -> Molecule:
    """
    Imports a coord file
    Returns the Molecule
    """

    with open(file_path, encoding='utf-8') as file:
        lines = file.readlines() #To skip first row

    atomic_numbers = []
    coordinates = []

    for line in lines[1:]:

        if '$' in line:

            break

        else:
            
            atom_info = line.split()
            if atom_info[-1].isnumeric():
                atomic_numbers.append(int(atom_info[-1]))
            else:
                atom_info[-1] = atom_info[-1].capitalize()
                atomic_numbers.append(element_symbol_to_atomic_number(atom_info[-1]))
            coordinates.append([float(coord)*0.529177249 for coord in atom_info[:3]])

    return Molecule(atomic_numbers,coordinates)


class Parser(ABC):
    '''base class for file parsers, i.e., classes for converting the content of
    a file (e.g., an ORCA output file) to instances of classes belonging to the
    molara data model, such as the Molecule class

    Any parser must implement the parse method, which parses the file and writes
    the result to member variables.
    
    Args:
        path: path to the file to parse'''

    def __init__(self, path: str | os.PathLike) -> None:
        self.path = pathlib.Path(path)

    @abstractmethod
    def parse(self) -> None:
        '''parse the file in self.path
        
        :raises ParsingError: when the file could not be parsed
        :raises FileNotFoundError: when self.path is not a file'''

class GeometryOptimizerParser(Parser, ABC):
    '''base class for parsing output of computational chemistry software that
    can optimize molecular geometries'''

    @property
    @abstractmethod
    def final_geometry(self) -> Molecule:
        '''optmized geometry'''


class OrcaOutParser(GeometryOptimizerParser):
    '''parses ORCA output
    
    Args:
        path: path to the file containing the ORCA output
    '''

    def __init__(self, path: str | os.PathLike) -> None:
        # cclib is an optional dependency. We import it here so that an
        # ImportError is already raised when creating the object, in case cclib
        # is not installed
        import cclib

        super().__init__(path)

        self.final_geometry: Molecule = None

    def parse(self) -> None:
        import cclib

        try:
            parser = cclib.parser.ORCA(self.path)
            data = parser.parse()
        except FileNotFoundError as err:
            raise ParsingError(f'Error reading {self.path}: File not found')\
                    from err

        self.final_geometry = self.__extract_final_geometry(data)

    def __extract_final_geometry(self, cclib_data) -> Molecule:
        try:
            atomnos = cclib_data.atomnos
            coords = cclib_data.atomcoords
        # cclib does not add attributes to data that could not be read, so we
        # need to check it
        except AttributeError as err:
            raise ParsingError(f'Error reading {self.path}: Final geometry'
                               ' could not be read.') from err
        else:
            return Molecule(atomnos, coords[-1])