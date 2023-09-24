import numpy as np 

from .Molecule import Molecule

class Molecules():
    """
    A class to store and manipulate a list of Molecules
    """
   
    def __init__(self):
        self.molecules = []
        self.num_mols = 0
        self.mol_index = 0
        self.energies = []

    def get_next_mol(self):

        molecule = self.molecules[self.mol_index]

        self.mol_index += 1 
        self.mol_index %= self.num_mols

        return molecule

    def get_previous_mol(self):
    
        self.mol_index -= 1 

        if self.mol_index < 0:
            self.mol_index = self.num_mols-1

        molecule = self.molecules[self.mol_index]

        return molecule        

    def get_mol(self,index):
        return self.molecules[index]

    def add_molecule(self,mol : Molecule) -> None:
        """
        Adds a molecule to the list of molecules
        param: mol: Molecule
        """

        if type(mol) == Molecule:

            self.molecules.append(mol)

            self.num_mols += 1

            self.energies.append(mol.energy)

        else:

            print('Input not of type mol.')
            
        return

    def remove_molecule(self,index : int) -> None:
        """
        Removes a molecule from the list of molecules
        param: index: int
        """

        self.molecules.pop(index)
        self.num_mols -= 1

        return
