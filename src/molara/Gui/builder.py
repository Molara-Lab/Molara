"""Dialog for building molecules via a Z-matrix."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import QDialog, QMainWindow, QTableWidgetItem
from PySide6.QtOpenGLWidgets import QOpenGLWidget

from molara.Gui.ui_builder import Ui_builder
from scipy.spatial.transform.rotation import Rotation

from molara.Molecule.atom import element_symbol_to_atomic_number
from molara.Molecule.molecule import Molecule
from molara.Molecule.molecules import Molecules

if TYPE_CHECKING:
    from molara.MainWindow.main_window import MainWindow

__copyright__ = "Copyright 2024, Molara"



class BuilderDialog(QDialog):
    """Dialog to ask for information to build molecules."""


    def __init__(self, parent: QOpenGLWidget = None) -> None:
        """Initializes the ZMatBuilder dialog.

        params:
        parent: MainWindow: The widget of the MainWindow.
        """
        super().__init__(
            parent,
        )  # main window widget is passed as a parent, so dialog is closed if main window is closed.
        self.ui = Ui_builder()
        self.ui.setupUi(self)
        self.ui.AddAtomButton.clicked.connect(self.select_add)
        self.parent().mols = Molecules()

        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(4)

        self.z_matrix:dict[list] = {}

        text_data = ["Element","Distance[A]","Angle[°]","Dihedral[°]"]
        for column,text in enumerate(text_data):
            self.ui.tableWidget.setHorizontalHeaderItem(column, QTableWidgetItem(text))


    def select_add(self) -> None:
        """Selects the add procedure. Depends on the number of atoms in the molecule."""
        values = None 

        if self.parent().mols.num_mols == 0:
            values,atoms = self.add_first_atom()
            key = 1

        else:
            mol:Molecule = self.parent().mols.mols[0]
            self.n_atoms = len(mol.atomic_numbers)

            if self.n_atoms >= 3:  # noqa: PLR2004
                values,atoms = self.add_nth_atom(mol)

            elif self.n_atoms == 2:  # noqa: PLR2004
                values,atoms = self.add_third_atom(mol)

            elif self.n_atoms == 1:  # noqa: PLR2004
                values,atoms = self.add_second_atom(mol)

            self.parent().delete_molecule()
            self.parent().set_structure(mol)

            key = self.n_atoms+1

        if values is not None:

            params = {"values":values,
                      "atoms":atoms,
                      }
            self.z_matrix[key]= params

            self._extend_z_matrix(key)

        self.parent().clear_builder_selected_atoms()

    def orth(self,vec, unitvec):
        return vec - np.dot(vec, unitvec) * unitvec
    
    def add_first_atom(self) -> None:
        """Initializes a molecule and adds the first atom to it."""
        element = self.ui._0Element.text().capitalize()
        at_chrg = element_symbol_to_atomic_number(element)
        at_chrg_check = True if at_chrg is not None else False 

        init_xyz = np.zeros([1, 3])
        self.parent().mols.add_molecule(Molecule([at_chrg], init_xyz,draw_bonds=False))
        self.parent().set_structure(self.parent().mols.get_current_mol())

        if at_chrg_check: 

            self.ui.tableWidget.setRowCount(1)
            self.ui.tableWidget.setItem(0,0, QTableWidgetItem(element))
            values = [element]
            atoms = [None]

            return values,atoms
        
        else:
            return None,None   
    
    def add_second_atom(self,mol:Molecule) -> None:
        """Adds a second atom and deletes the ghost atom needed for the first atom.
        
        params:
        mol:Molecule: The molecule where a second atom shall be added."""
        element = self.ui._0Element.text().capitalize()
        at_chrg = element_symbol_to_atomic_number(element)
        dist = float(self.ui._1BondDistance.text())

        at_chrg_check = True if at_chrg is not None else False 
        boundary_check = self._check_value(dist)

        if boundary_check and at_chrg_check:
            coord = np.array([0.0,0.0,dist])
            mol.add_atom(at_chrg, coord)
            mol.toggle_bonds()
            
            values =  [element,str(dist)]
            atoms = [0]

            return values,atoms
        else:
            return None,None
        

    def add_third_atom(self,mol:Molecule) -> None:
        """Adds a third atom to the molecule.
        
        params:
        mol:Molecule: The molecule where a second atom shall be added."""
        element = self.ui._0Element.text().capitalize()

        at_chrg = element_symbol_to_atomic_number(element)

        at1_num:int = self.parent().builder_selected_spheres[0]

        #If 1 -> 0 if 0 -> 1
        at2_num:int = 1 - at1_num

        dist = float(self.ui._1BondDistance.text())

        angle = np.deg2rad(float(self.ui._2BondAngle.text()))

        boundary_check = self._check_value(dist,angle)
        at_chrg_check = True if at_chrg is not None else False 
        atom_selection_check = self._check_selected_atoms(at1_num,at2_num)

        if boundary_check and atom_selection_check and at_chrg_check:

            coord = np.array([dist * np.sin(angle), 0, dist * np.cos(angle)])

            if at1_num == 1:
                coord[2] = mol.atoms[at1_num].position[2] - coord[2]

            mol.add_atom(at_chrg,coord)
            values = [element,str(dist),str(np.rad2deg(angle))]
            atoms  = [at1_num,at2_num]

            return values,atoms
        else:
            return None,None   


    def add_nth_atom(self,mol:Molecule) -> None:
        """Adds an nth atom to the molecule."""
        element = self.ui._0Element.text().capitalize()

        at_chrg = element_symbol_to_atomic_number(element)

        at1_num:int = self.parent().builder_selected_spheres[0]

        at2_num:int = self.parent().builder_selected_spheres[1]

        at3_num:int = self.parent().builder_selected_spheres[2]

        dist = float(self.ui._1BondDistance.text())

        angle = np.deg2rad(float(self.ui._2BondAngle.text()))

        dihedral = np.deg2rad(float(self.ui._3DihedralAngle.text()))

        boundary_check = self._check_value(dist,angle)

        atom_selection_check = self._check_selected_atoms(at1_num,at2_num,at3_num)
        at_chrg_check = True if at_chrg is not None else False 

        if boundary_check and atom_selection_check and at_chrg_check:

            vec1 = mol.atoms[at2_num].position - mol.atoms[at1_num].position
            length = np.linalg.norm(vec1)
            vec1 = vec1 / length if length > 0 else np.array([0, 0, 1.])
            vec2 = self.orth(mol.atoms[at3_num].position - mol.atoms[at2_num].position, vec1)
            length =  np.linalg.norm(vec2)
            vec2 = vec2 / length if length > 0 else np.array([1., 0, 0])
            if np.linalg.norm(self.orth(vec2, vec1)) == 0:
                vec2 = np.array([0, 1., 0])
            vec3 = np.cross(vec1, vec2)
            vec3 = vec3 / np.linalg.norm(vec3)
            tmp = dist * np.sin(angle)
            coord = mol.atoms[at1_num].position + dist * np.cos(angle) * vec1 + tmp * np.cos(dihedral) * vec2 + tmp * np.sin(dihedral) * vec3
        
            mol.add_atom(at_chrg, np.squeeze(coord))

            key = str(self.n_atoms+1)
            values = [element,str(dist),str(np.rad2deg(angle)),str(np.rad2deg(dihedral))]
            atoms = [at1_num,at2_num,at3_num]

            return values,atoms
        else:
            return None,None  

    def _clear_all_text(self) -> None:
        """Clears all text in the zbuilder dialog."""
        for line_edit in [
            self.ui._0Element,
            self.ui._1BondDistance,
            self.ui._2BondAngle,
            self.ui._3DihedralAngle,
        ]:
            line_edit.clear()

    def _check_value(self,*args:float,threshold:float=1e-8)->bool:
        """Checks whether values are larger than a threshold

        args:float:Parameter to check whether threshold is reached.
        threshold:Threshold to be reached.
        """
        vals_above_threshold = True 

        for arg in args: 
            vals_above_threshold = arg>threshold
            if not(vals_above_threshold):
                break

        return vals_above_threshold
    
    def _check_selected_atoms(*selected_atoms:int)->bool:
        """Checks if all necessary atoms are selected.
        
        params:
        selected_atoms:int:Selected Atoms to check if not -1"""
        all_selected = True
        for idx in selected_atoms:
            if idx == -1:
                all_selected = False 
                break 

        return all_selected

    def _extend_z_matrix(self,n_atoms:int):
        self.ui.tableWidget.setRowCount(n_atoms)
        for i,text in enumerate(self.z_matrix[n_atoms]["values"]):
            self.ui.tableWidget.setItem(n_atoms-1,i, QTableWidgetItem(text))