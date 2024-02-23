"""Dialog for building molecules via a Z-matrix."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import QDialog, QTableWidgetItem

from molara.Gui.ui_builder import Ui_builder
from molara.Structure.atom import element_symbol_to_atomic_number
from molara.Structure.molecule import Molecule
from molara.Structure.molecules import Molecules

if TYPE_CHECKING:
    from PySide6.QtWidgets import QMainWindow

    from molara.Gui.main_window import MainWindow
    from molara.Gui.structure_widget import StructureWidget

__copyright__ = "Copyright 2024, Molara"


class BuilderDialog(QDialog):
    """Dialog to ask for information to build molecules."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initializes the ZMatBuilder dialog.

        :param parent: QOpenGLWidget: The structure widget.
        """
        super().__init__(
            parent,
        )  # structure widget is passed as a parent
        self.ui = Ui_builder()
        self.ui.setupUi(self)
        self.ui.AddAtomButton.clicked.connect(self.select_add)
        self.ui.DeleteAtomButton.clicked.connect(self.delete_atom)
        self.ui.tableWidget.itemChanged.connect(self.adapt_z_matrix)

        self.ui.tableWidget.acceptDrops()

        self.main_window:MainWindow = self.parent()
        self.structure_widget:StructureWidget = self.parent().structure_widget

        self.main_window.mols = Molecules()

        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(7)

        self.z_matrix: list[dict] = []

        column_widths = [55,40,70,40,70,40,70]
        for col,width in enumerate(column_widths):
            self.ui.tableWidget.setColumnWidth(col,width)

        text_data = ["Element","At. 1","Distance[A]","At. 2", "Angle[°]","At. 3","Dihedral[°]"]
        for column, text in enumerate(text_data):
            self.ui.tableWidget.setHorizontalHeaderItem(column, QTableWidgetItem(text))

    def select_add(self) -> None:
        """Selects the add procedure. Depends on the number of atoms in the molecule."""
        self.disable_slot = True

        if self.main_window.mols.num_mols == 0:
            params, atom_nums = self._get_parameters(0)
            self.add_first_atom(params)
            mol: Molecule = self.main_window.mols.mols[0]
        else:
            mol = self.main_window.mols.mols[0]
            params, atom_nums = self._get_parameters(mol.n_at)

            match mol.n_at:
                case 1:
                    self.add_second_atom(mol, params)
                case 2:
                    self.add_third_atom(mol, params, atom_nums)
                case _:
                    self.add_nth_atom(mol, params, atom_nums)


        self.structure_widget.set_structure(mol)
        self.structure_widget.update()
        self.z_matrix.append({"parameter": params, "atom_nums": atom_nums})
        self._set_z_matrix_row(mol,mol.n_at-1)
        self.structure_widget.clear_builder_selected_atoms()
        self.disable_slot = False

    def delete_atom(self) -> None:
        """Deletes an atom from the z-matrix visualization table and z_matrix itself."""
        index = self.ui.tableWidget.currentRow()

        mol: Molecule = self.main_window.mols.mols[0]

        do_deletion = self._check_z_matrix_deletion(index)
        if do_deletion:
            error_msg = f"Atom {index} will be deleted."
            self.ui.ErrorMessageBrowser.setText(error_msg)
            self._delete_zmat_row(index, mol.n_at)
            self._delete_table_row(index)
            self.main_window.mols.mols[0].remove_atom(index=index)
            self.structure_widget.delete_structure()
            self.structure_widget.set_structure(self.main_window.mols.get_current_mol())

    def adapt_z_matrix(self, item: QTableWidgetItem) -> None:
        """Changes the z-matrix in dependence of the visualization table.

        :param item: passed item from the visualization table
        """
        if self.disable_slot:
            return

        row = item.row()

        params = self._get_parameters_from_table(row)

        if params is None:
            error_msg = "Incorrect input type."
            self.ui.ErrorMessageBrowser.setText(error_msg)
            self._set_z_matrix_row(self.main_window.mols.mols[0],row)
        else:
            self.z_matrix[row]["parameter"] = params
            self.z_matrix_temp = self.z_matrix.copy()

            self.z_matrix = []

            self.main_window.mols.remove_molecule(0)

            for i in range(len(self.z_matrix_temp)):

                if i == 0:
                    params = self.z_matrix_temp[0]["parameter"]
                    atom_nums = self.z_matrix_temp[0]["atom_nums"]
                    self.add_first_atom(params)
                    mol: Molecule = self.main_window.mols.mols[0]
                else:
                    mol = self.main_window.mols.mols[0]
                    params = self.z_matrix_temp[i]["parameter"]
                    atom_nums = self.z_matrix_temp[i]["atom_nums"]
                    if i >= 3:  # noqa: PLR2004
                        self.add_nth_atom(mol, params, atom_nums)
                    elif i == 2:  # noqa: PLR2004
                        self.add_third_atom(mol, params, atom_nums)
                    elif i == 1:
                        self.add_second_atom(mol, params)

                self.z_matrix.append({"parameter": params, "atom_nums": atom_nums})

            self.structure_widget.delete_structure()
            self.structure_widget.set_structure(mol)

            self._update_z_matrix(mol)

    def _orth(self, vec: np.ndarray, unitvec: np.ndarray) -> np.ndarray:
        """Orthogonalize the vector.

        :param vec: vector to orthogonalize
        :param unitvec: unitvector

        """
        return vec - np.dot(vec, unitvec) * unitvec

    def add_first_atom(self, params: tuple) -> None:
        """Initializes a molecule and adds the first atom to it.

        :param params: parameters that are passed for the first atom
        """
        element, _ = params
        at_chrg = element_symbol_to_atomic_number(element)
        at_chrg_check = self._check_element(at_chrg)

        init_xyz = np.zeros([1, 3])

        self.main_window.mols.add_molecule(Molecule([at_chrg], init_xyz, draw_bonds=False))
        self.disable_slot = True
        if at_chrg_check:
            self.ui.tableWidget.setRowCount(1)
            self.ui.tableWidget.setItem(0, 0, QTableWidgetItem(element))
        self.disable_slot = False

    def add_second_atom(self, mol: Molecule, params: tuple) -> None:
        """Adds a second atom.

        :param mol: The molecule where a second atom shall be added.
        """
        element, dist = params
        at_chrg = element_symbol_to_atomic_number(element)
        at_chrg_check = self._check_element(at_chrg)
        boundary_check = self._check_value(dist)
        if boundary_check and at_chrg_check:
            coord = np.array([0.0, 0.0, dist])
            mol.add_atom(at_chrg, coord)
            mol.toggle_bonds()

    def add_third_atom(self, mol: Molecule, params: tuple, atom_ids: list) -> None:
        """Adds a third atom to the molecule.

        :param mol: The molecule where a second atom shall be added.
        :param params: atom parameters (element, distance to selected atom, angle to selected bond)
        """
        element, dist, angle = params
        at1_id: int = atom_ids[0]
        at2_id: int = atom_ids[1]
        at_chrg = element_symbol_to_atomic_number(element)
        boundary_check = self._check_value(dist, angle)
        atom_selection_check = self._check_selected_atoms(at1_id, at2_id)
        at_chrg_check = self._check_element(at_chrg)

        if boundary_check and atom_selection_check and at_chrg_check:
            coord = np.array([dist * np.sin(angle), 0, dist * np.cos(angle)])
            if at1_id == 1:
                coord[2] = mol.atoms[at1_id].position[2] - coord[2]
            else:
                coord[2] = mol.atoms[at1_id].position[2] + coord[2]
            mol.add_atom(at_chrg, coord)

    def add_nth_atom(self, mol: Molecule, params: tuple, atom_nums: list) -> None:
        """Adds an nth atom to the molecule.

        :param mol: The molecule where an nth atom shall be added.
        :param params: atom parameters (element, distance to selected atom, angle to selected bond)

        """
        element, dist, angle, dihedral = params
        at1_num: int = atom_nums[0]
        at2_num: int = atom_nums[1]
        at3_num: int = atom_nums[2]
        at_chrg = element_symbol_to_atomic_number(element)
        boundary_check = self._check_value(dist, angle)
        atom_selection_check = self._check_selected_atoms(at1_num, at2_num, at3_num)
        at_chrg_check = self._check_element(at_chrg)

        if boundary_check and atom_selection_check and at_chrg_check:
            vec1 = mol.atoms[at2_num].position - mol.atoms[at1_num].position
            length = np.linalg.norm(vec1)
            vec1 = vec1 / length if length > 0 else np.array([0, 0, 1.0])
            vec2 = self._orth(mol.atoms[at3_num].position - mol.atoms[at2_num].position, vec1)
            length = np.linalg.norm(vec2)
            vec2 = vec2 / length if length > 0 else np.array([1.0, 0, 0])
            if np.linalg.norm(self._orth(vec2, vec1)) == 0:
                vec2 = np.array([0, 1.0, 0])
            vec3 = np.cross(vec1, vec2)
            vec3 = vec3 / np.linalg.norm(vec3)
            tmp = dist * np.sin(angle)
            coord = mol.atoms[at1_num].position + dist * np.cos(angle) * vec1
            coord += tmp * np.cos(dihedral) * vec2 + tmp * np.sin(dihedral) * vec3

            mol.add_atom(at_chrg, np.squeeze(coord))

    def _clear_all_text(self) -> None:
        """Clears all text in the zbuilder dialog."""
        for line_edit in [
            self.ui.Box_0Element,
            self.ui.Box_1BondDistance,
            self.ui.Box_2BondAngle,
            self.ui.Box_3DihedralAngle,
        ]:
            line_edit.clear()

    def _check_value(self, *args: float, threshold: float = 1e-8) -> bool:
        """Checks whether values are larger than a threshold.

        args:float:Parameter to check whether threshold is reached.
        threshold:Threshold to be reached.
        """
        error_msg = "Parameter values are not valid."
        vals_above_threshold = True

        for arg in args:
            vals_above_threshold = arg > threshold
            if not (vals_above_threshold):
                self.ui.ErrorMessageBrowser.setText(error_msg)

                break

        return vals_above_threshold

    def _check_selected_atoms(self, *selected_atoms: int) -> bool:
        """Checks if all necessary atoms are selected.

        params:
        selected_atoms:int:Selected Atoms to check if not -1
        """
        error_msg = "Not enough atoms selected."
        all_selected = True
        for idx in selected_atoms:
            if idx == -1:
                all_selected = False
                self.ui.ErrorMessageBrowser.setText(error_msg)
                break

        return all_selected

    def _check_element(self, at_chrg: int | None) -> bool:
        """Checks if the element which should be added exists.

        params:
        at_charg:atomic charge which is None if not an element.
        """
        error_msg = "This is not an element."
        is_element = True
        if at_chrg == 0:
            is_element = False
            self.ui.ErrorMessageBrowser.setText(error_msg)
        return is_element

    def _set_z_matrix_row(self, mol: Molecule,row:int) -> None:

        self.disable_slot = True
        param_rows = [0,2,4,6]
        atom_id_rows = [0,1,3,5]

        self.ui.tableWidget.setRowCount(mol.n_at)

        for i, text in enumerate(self.z_matrix[row]["parameter"]):

            if text is not None:

                match i:
                    case 0:
                        temp_text = text
                    case 1:
                        temp_text = f"{text:.2f}"
                    case _:
                        temp_text = f"{np.rad2deg(text):.2f}"

                self.ui.tableWidget.setItem(row, param_rows[i], QTableWidgetItem(temp_text))
                if param_rows[i] != 0:
                    atom_id = self.z_matrix[row]["atom_nums"][i-1]
                    self.ui.tableWidget.setItem(row, atom_id_rows[i], QTableWidgetItem(str(atom_id+1)))

        self.disable_slot = False

    def _update_z_matrix(self, mol: Molecule) -> None:
        self.disable_slot = True
        self.ui.tableWidget.setRowCount(mol.n_at)
        for j in range(mol.n_at):
            self._set_z_matrix_row(mol,j)

        self.disable_slot = False

    def _delete_table_row(self, idx: int) -> None:
        self.ui.tableWidget.removeRow(idx)

    def _get_parameters(self, nat: int) -> tuple[tuple, list]:
        element: str = self.ui.Box_0Element.text().capitalize()
        dist: float = float(self.ui.Box_1BondDistance.text())
        angle: float = np.deg2rad(float(self.ui.Box_2BondAngle.text()))
        dihedral: float = np.deg2rad(float(self.ui.Box_3DihedralAngle.text()))
        atom_nums = self.structure_widget.builder_selected_spheres

        match nat:
            case 0:
                return (element, None), []
            case 1:
                return (element, dist), [0]
            case 2:
                return (element, dist, angle), atom_nums
            case _:
                return (
                    element,
                    dist,
                    angle,
                    dihedral,
                ), atom_nums

    def _get_parameters_from_table(self, row: int) -> tuple|None:

        param_type_validity = True

        if row >= 0:
            element = str(self.ui.tableWidget.item(row, 0).text().capitalize())
            param_type_validity = bool(element_symbol_to_atomic_number(element))

        if row >= 1:
            dist = self.ui.tableWidget.item(row, 2).text()
            param_type_validity = bool(re.match(r"^-?\d+(\.\d+)?$", dist))

        if row >= 2: #noqa: PLR2004
            angle = self.ui.tableWidget.item(row, 4).text()
            param_type_validity = bool(re.match(r"^-?\d+(\.\d+)?$", angle))

        if row >= 3: #noqa: PLR2004
            dihedral = self.ui.tableWidget.item(row, 6).text()
            param_type_validity = bool(re.match(r"^-?\d+(\.\d+)?$", dihedral))

        if not param_type_validity:
            return None

        match row:
            case 0:
                return (element, None)
            case 1:
                return (element, float(dist))
            case 2:
                return (element, float(dist), np.deg2rad(float(angle)))
            case _:
                return (element, float(dist), np.deg2rad(float(angle)), np.deg2rad(float(dihedral)))


    def _check_z_matrix_deletion(self, index: int) -> bool:
        do_deletion = True

        if index == -1:
            error_msg = "No Atom was chosen to be deleted."
            self.ui.ErrorMessageBrowser.setText(error_msg)
            do_deletion = False

        else:
            for entry in self.z_matrix:
                if index in entry["atom_nums"]:
                    error_msg = f"Cannot be deleted. Atom {index+1} depends on this atom."
                    do_deletion = False
                    self.ui.ErrorMessageBrowser.setText(error_msg)

        return do_deletion

    def _delete_zmat_row(self, index: int, nat: int) -> None:
        for i in range(index, nat):
            for j, at_num in enumerate(self.z_matrix[i]["atom_nums"]):
                if at_num > index and at_num != -1:
                    self.z_matrix[i]["atom_nums"][j] -= 1

        self.z_matrix.pop(index)
