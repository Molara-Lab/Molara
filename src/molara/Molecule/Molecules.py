import numpy as np 

from .Molecule import Molecule

class Molecules():
   
    def __init__(self):
        self.molecules = []
        self.num_mols = 0

    def add_molecule(self,mol : Molecule) -> None:
        """
        Adds a molecule to the list of molecules
        param: mol: Molecule
        """

        if type(mol) == Molecule:

            self.molecules.append(mol)

            self.num_mols += 1

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