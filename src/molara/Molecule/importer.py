from molara.Molecule.atom import element_symbol_to_atomic_number
from molara.Molecule.molecule import Molecule
from molara.Molecule.molecules import Molecules


def read_xyz(file_path: str) -> Molecules:
    """
    Read-in function for .xyz files
    param: file_path: str
    """
    molecules = Molecules()

    with open(file_path) as file:
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

    molecules.add_molecule(Molecule(atomic_numbers, coordinates, lines[1]))
    # Read in for a single xyz file
    # Goes on if file has more than one structure stored
    if (len(lines) > 2 + num_atoms) and lines[2 + num_atoms].replace("\n", "").isdigit():
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

            molecules.add_molecule(Molecule(atomic_numbers, coordinates, lines[1 + xyz_len]))

    file.close()

    return molecules


def read_coord(file_path: str) -> Molecules:
    """
    Imports a coord file
    Returns the Molecule
    param: file_path: str
    """

    molecules = Molecules()

    with open(file_path) as file:
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

    molecules.add_molecule(Molecule(atomic_numbers, coordinates))

    return molecules
