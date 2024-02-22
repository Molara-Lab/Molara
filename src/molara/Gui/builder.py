"""Dialog for building molecules via a Z-matrix."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtWidgets import QDialog, QTableWidgetItem

from molara.Gui.ui_builder import Ui_builder
from molara.Structure.atom import element_symbol_to_atomic_number
from molara.Structure.molecule import Molecule
from molara.Structure.molecules import Molecules

if TYPE_CHECKING:
    from PySide6.QtOpenGLWidgets import QOpenGLWidget

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
        self.ui.DeleteAtomButton.clicked.connect(self.delete_atom)
        self.ui.tableWidget.itemChanged.connect(self.adapt_z_matrix)

        self.ui.tableWidget.acceptDrops()

        self.parent().mols = Molecules()

        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(4)

        self.z_matrix: list[dict] = []

        text_data = ["Element", "Distance[A]", "Angle[°]", "Dihedral[°]"]
        for column, text in enumerate(text_data):
            self.ui.tableWidget.setHorizontalHeaderItem(column, QTableWidgetItem(text))

    def select_add(self) -> None:
        """Selects the add procedure. Depends on the number of atoms in the molecule."""
        self.disable_slot = True

        if self.parent().mols.num_mols == 0:
            params, atom_nums = self._get_parameters(0)

            self.add_first_atom(params)

            mol: Molecule = self.parent().mols.mols[0]

        else:
            mol = self.parent().mols.mols[0]

            params, atom_nums = self._get_parameters(mol.n_at)

            if mol.n_at >= 3:  # noqa: PLR2004
                self.add_nth_atom(mol, params, atom_nums)

            elif mol.n_at == 2:  # noqa: PLR2004
                self.add_third_atom(mol, params, atom_nums)

            elif mol.n_at == 1:
                self.add_second_atom(mol, params)

            self.parent().delete_structure()
            self.parent().set_structure(mol)

        self.z_matrix.append({"parameter": params, "atom_nums": atom_nums})

        self._extend_z_matrix(mol)

        self.parent().clear_builder_selected_atoms()

        self.disable_slot = False

    def delete_atom(self) -> None:
        """Deletes an atom from the z-matrix visualization table and z_matrix itself."""
        index = self.ui.tableWidget.currentRow()

        mol: Molecule = self.parent().mols.mols[0]

        do_deletion = self._check_z_matrix_deletion(index)
        if do_deletion:
            error_msg = f"Atom {index} will be deleted."
            self.ui.ErrorMessageBrowser.setText(error_msg)
            self._delete_zmat_row(index, mol.n_at)
            self._delete_table_row(index)
            self.parent().mols.mols[0].remove_atom(index=index)
            self.parent().delete_structure()
            self.parent().set_structure(self.parent().mols.get_current_mol())

    def adapt_z_matrix(self, item: QTableWidgetItem) -> None:
        """Changes the z-matrix in dependence of the visualization table."""
        if not self.disable_slot:
            row = item.row()
            params = self._get_parameters_from_table(row)

            self.z_matrix[row]["parameter"] = params
            self.z_matrix_temp = self.z_matrix.copy()

            self.z_matrix = []

            self.parent().mols.remove_molecule(0)

            for i in range(len(self.z_matrix_temp)):
                if i == 0:
                    params = self.z_matrix_temp[0]["parameter"]
                    atom_nums = self.z_matrix_temp[0]["atom_nums"]

                    self.add_first_atom(params)

                    mol: Molecule = self.parent().mols.mols[0]

                else:
                    mol = self.parent().mols.mols[0]

                    params = self.z_matrix_temp[i]["parameter"]
                    atom_nums = self.z_matrix_temp[i]["atom_nums"]

                    if i >= 3:  # noqa: PLR2004
                        self.add_nth_atom(mol, params, atom_nums)

                    elif i == 2:  # noqa: PLR2004
                        self.add_third_atom(mol, params, atom_nums)

                    elif i == 1:
                        self.add_second_atom(mol, params)

                self.z_matrix.append({"parameter": params, "atom_nums": atom_nums})

            self.parent().delete_structure()
            self.parent().set_structure(mol)

            self._update_z_matrix(mol)

    def _orth(self, vec: np.ndarray, unitvec: np.ndarray) -> np.ndarray:
        return vec - np.dot(vec, unitvec) * unitvec

    def add_first_atom(self, params: tuple) -> None:
        """Initializes a molecule and adds the first atom to it."""
        element, _ = params
        at_chrg = element_symbol_to_atomic_number(element)
        at_chrg_check = self._check_element(at_chrg)

        init_xyz = np.zeros([1, 3])

        self.parent().mols.add_molecule(Molecule([at_chrg], init_xyz, draw_bonds=False))
        self.parent().set_structure(self.parent().mols.get_current_mol())
        self.disable_slot = True
        if at_chrg_check:
            self.ui.tableWidget.setRowCount(1)
            self.ui.tableWidget.setItem(0, 0, QTableWidgetItem(element))
        self.disable_slot = False

    def add_second_atom(self, mol: Molecule, params: tuple) -> None:
        """Adds a second atom.

        params:
        mol:Molecule: The molecule where a second atom shall be added.
        """
        element, dist = params

        at_chrg = element_symbol_to_atomic_number(element)

        at_chrg_check = self._check_element(at_chrg)

        boundary_check = self._check_value(dist)

        if boundary_check and at_chrg_check:
            coord = np.array([0.0, 0.0, dist])
            mol.add_atom(at_chrg, coord)
            mol.toggle_bonds()

    def add_third_atom(self, mol: Molecule, params: tuple, atom_nums: list) -> None:
        """Adds a third atom to the molecule.

        params:
        mol:Molecule: The molecule where a second atom shall be added.
        """
        element, dist, angle = params

        at1_num: int = atom_nums[0]

        at2_num: int = atom_nums[1]

        at_chrg = element_symbol_to_atomic_number(element)

        boundary_check = self._check_value(dist, angle)
        atom_selection_check = self._check_selected_atoms(at1_num, at2_num)
        at_chrg_check = self._check_element(at_chrg)

        if boundary_check and atom_selection_check and at_chrg_check:
            coord = np.array([dist * np.sin(angle), 0, dist * np.cos(angle)])

            if at1_num == 1:
                coord[2] = mol.atoms[at1_num].position[2] - coord[2]
            else:
                coord[2] = mol.atoms[at1_num].position[2] + coord[2]

            mol.add_atom(at_chrg, coord)

    def add_nth_atom(self, mol: Molecule, params: tuple, atom_nums: list) -> None:
        """Adds an nth atom to the molecule."""
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
        if at_chrg is None:
            is_element = False
            self.ui.ErrorMessageBrowser.setText(error_msg)
        return is_element

    def _extend_z_matrix(self, mol: Molecule) -> None:
        self.disable_slot = True
        self.ui.tableWidget.setRowCount(mol.n_at)
        for i, text in enumerate(self.z_matrix[mol.n_at - 1]["parameter"]):
            temp_text = np.rad2deg(text) if i > 1 else text
            if text is not None:
                self.ui.tableWidget.setItem(mol.n_at - 1, i, QTableWidgetItem(str(temp_text)))

        self.disable_slot = False

    def _update_z_matrix(self, mol: Molecule) -> None:
        self.disable_slot = True
        self.ui.tableWidget.setRowCount(mol.n_at)
        for j in range(mol.n_at):
            for i, text in enumerate(self.z_matrix[j]["parameter"]):
                temp_text = np.rad2deg(text) if i > 1 else text
                if text is not None:
                    self.ui.tableWidget.setItem(j, i, QTableWidgetItem(str(temp_text)))

        self.disable_slot = False

    def _delete_table_row(self, idx: int) -> None:
        self.ui.tableWidget.removeRow(idx)

    def _get_parameters(self, nat: int) -> tuple[tuple, list]:
        element: str = self.ui.Box_0Element.text().capitalize()
        dist: float = float(self.ui.Box_1BondDistance.text())
        angle: float = np.deg2rad(float(self.ui.Box_2BondAngle.text()))
        dihedral: float = np.deg2rad(float(self.ui.Box_3DihedralAngle.text()))
        atom_nums = self.parent().builder_selected_spheres

        if nat > 2:  # noqa: PLR2004
            return (
                element,
                dist,
                angle,
                dihedral,
            ), atom_nums
        if nat == 2:  # noqa: PLR2004
            return (element, dist, angle), atom_nums
        if nat == 1:
            return (element, dist), atom_nums
        # if nat == 0:
        return (element, None), atom_nums

    def _get_parameters_from_table(self, row: int) -> tuple:
        if row >= 0:
            element = str(self.ui.tableWidget.item(row, 0).text().capitalize())
        if row >= 1:
            dist = float(self.ui.tableWidget.item(row, 1).text())
        if row >= 2:  # noqa: PLR2004
            angle = np.deg2rad(float(self.ui.tableWidget.item(row, 2).text()))
        if row >= 3:  # noqa: PLR2004
            dihedral = np.deg2rad(float(self.ui.tableWidget.item(row, 3).text()))

        match row:
            case 0:
                return (element, None)
            case 1:
                return (element, dist)
            case 2:
                return (element, dist, angle)
            case other:  # noqa: F841
                return (element, dist, angle, dihedral)

        return None

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
