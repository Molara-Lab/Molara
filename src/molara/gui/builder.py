"""Dialog for building molecules via a Z-matrix."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import TYPE_CHECKING, Any, TypeVar

import numpy as np
from PySide6.QtWidgets import QDialog, QTableWidgetItem

from molara.gui.ui_builder import Ui_builder
from molara.structure.atom import element_symbol_to_atomic_number
from molara.structure.molecule import Molecule
from molara.structure.molecules import Molecules

if TYPE_CHECKING:
    from collections.abc import Callable

    from PySide6.QtWidgets import QMainWindow
    from typing_extensions import ParamSpec

    from molara.gui.main_window import MainWindow
    from molara.gui.structure_widget import StructureWidget

    T = TypeVar("T")
    P = ParamSpec("P")

__copyright__ = "Copyright 2024, Molara"


def toggle_slot(func: Callable[..., Any]) -> Callable[..., Any]:
    """Toggles the disable slot variable to circumvent recursivity."""

    def wrapper(self: BuilderDialog, *args: P.args, **kwargs: P.kwargs) -> None:
        if self.disable_slot:
            return
        self.disable_slot = True
        func(self, *args, **kwargs)
        self.disable_slot = False

    return wrapper


class BuilderDialog(QDialog):
    """Dialog to ask for information to build molecules."""

    def __init__(self, parent: QMainWindow | None = None) -> None:
        """Initialize the ZMatBuilder dialog.

        :param parent: the parent widget (main window).
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

        self.main_window: MainWindow = self.parent()
        self.structure_widget: StructureWidget = self.parent().structure_widget

        self.main_window.mols = Molecules()
        self.z_matrix: list[dict] = []

        self.disable_slot: bool = False
        self.colliding_idx: int | None = None

        self._initialize_table()

    def _initialize_table(self) -> None:
        """Initialize the table of the builder."""
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.setColumnCount(7)

        column_widths = [55, 40, 70, 40, 70, 40, 70]
        for col, width in enumerate(column_widths):
            self.ui.tableWidget.setColumnWidth(col, width)

        text_data = ["Element", "At. 1", "Distance[A]", "At. 2", "Angle[°]", "At. 3", "Dihedral[°]"]
        for column, text in enumerate(text_data):
            self.ui.tableWidget.setHorizontalHeaderItem(column, QTableWidgetItem(text))

    @toggle_slot
    def select_add(self) -> None:
        """Select the add procedure. Depends on the number of atoms in the molecule."""
        self.disable_slot = False
        num_atoms = 0 if self.main_window.mols.num_mols == 0 else self.main_window.mols.mols[0].n_at
        params, atom_ids = self._get_parameters(num_atoms)
        self.exec_add_atom(num_atoms, params, atom_ids)

    def exec_add_atom(self, count_atoms: int, params: tuple, atom_ids: list) -> None:
        """Execute the addition of an atom."""
        self.add_atom(count_atoms, params, atom_ids)
        mol = self.main_window.mols.mols[0]

        if not self.err and self.colliding_idx is None:
            self.ui.ErrorMessageBrowser.setText("")
            self.structure_widget.set_structure([mol])
            self.structure_widget.update()
            self.z_matrix.append({"parameter": params, "atom_ids": atom_ids})
            self._set_z_matrix_row(mol.n_at, mol.n_at - 1)
            self.structure_widget.clear_builder_selected_atoms()

    def delete_atom(self) -> None:
        """Delete an atom from the z-matrix visualization table and z_matrix itself."""
        index = self.ui.tableWidget.currentRow()

        mol = self.main_window.mols.mols[0]

        do_deletion = self._check_z_matrix_deletion(index)

        if not do_deletion:
            return

        error_msg = f"Atom {index+1} will be deleted."
        self.ui.ErrorMessageBrowser.setText(error_msg)
        self._delete_zmat_row(index, mol.n_at)
        self._delete_table_row(index)

        if mol.n_at <= 2:  # noqa: PLR2004
            mol.draw_bonds = False

        mol.remove_atom(index=index)

        self.structure_widget.delete_structure()

        if mol.n_at > 0:
            self.structure_widget.set_structure([mol])
        else:
            self.main_window.mols.remove_molecule(0)
            self.structure_widget.update()

    @toggle_slot
    def adapt_z_matrix(self, item: QTableWidgetItem) -> None:
        """Change the z-matrix in dependence of the visualization table.

        :param item: passed item from the visualization table
        """
        row = item.row()

        self.disable_slot = False
        self._clear_upper_table_entries(self.main_window.mols.mols[0].n_at)

        params = self._get_parameters_from_table(row)

        if params[0] is None:
            error_msg = "Incorrect input type."
            self.ui.ErrorMessageBrowser.setText(error_msg)
            self._set_z_matrix_row(self.main_window.mols.mols[0].n_at, row)
            return

        self.z_matrix_temp = deepcopy(self.z_matrix)
        self.z_matrix[row]["parameter"] = params
        mol_temp = self.main_window.mols.mols[0]
        self.main_window.mols.remove_molecule(0)

        if not self.z_matrix:
            return

        mol: Molecule = Molecule(np.array([1]), np.array([[0.0, 0.0, 0.0]]), None, dummy=True, draw_bonds=False)
        for i in range(len(self.z_matrix)):
            params = self.z_matrix[i]["parameter"]
            atom_ids = self.z_matrix[i]["atom_ids"]
            if i == 0:
                self.disable_slot = False
            self.add_atom(i, params, atom_ids)
            mol = self.main_window.mols.mols[0]

            if self.colliding_idx is not None:
                mol = mol_temp
                self.z_matrix = self.z_matrix_temp
                self.main_window.mols.mols[0] = mol_temp
                break

        self.structure_widget.delete_structure()
        self.structure_widget.set_structure([mol])
        self._update_z_matrix(mol.n_at)

    def _orth(self, vec: np.ndarray, unitvec: np.ndarray) -> np.ndarray:
        """Calculate a vector that is orthogonal to the two given vectors.

        :param vec: vector to orthogonalize
        :param unitvec: unitvector

        """
        return vec - np.dot(vec, unitvec) * unitvec

    def add_atom(self, count_atoms: int, params: tuple, atom_ids: list) -> None:
        """Add an atom to the molecule.

        :param count_atoms: number of atoms that have been added so far
        :param params: parameters that are passed for the atom (angles in rad)
        :param atom_ids: atom ids of the selected atoms
        """
        self.err = False
        element, dist = params[0], params[1]
        angle = params[2] if len(params) > 2 else None  # noqa: PLR2004
        # dihedral = params[3] if len(params) > 3 else None

        atomic_num = element_symbol_to_atomic_number(element)
        atomic_num_valid = self._check_element(atomic_num)
        dist_valid = self._check_value(dist) if count_atoms > 0 else True
        angle_valid = self._check_value(angle) if angle is not None else True
        values_valid = atomic_num_valid and dist_valid and angle_valid

        if not (atomic_num_valid and values_valid):
            return

        # check if atom is the very first to be added
        if count_atoms == 0:
            pos = self.calc_position_new_atom(count_atoms, params, atom_ids)
            self.main_window.mols.add_molecule(
                Molecule(np.array([atomic_num]), pos, draw_bonds=False),
            )
            return

        # starting from the third atom, atoms must have been selected in order to specify relative position
        atom_selection_check = self._check_selected_atoms(*atom_ids[:count_atoms]) if count_atoms >= 2 else True  # noqa: PLR2004
        if not atom_selection_check:
            return

        mol = self.main_window.mols.mols[0]
        pos = self.calc_position_new_atom(count_atoms, params, atom_ids)

        # check for collisions
        self.colliding_idx = mol.compute_collision(pos) if count_atoms >= 3 else None  # noqa: PLR2004
        if self.colliding_idx is not None:
            error_msg = f"The atom would collide with atom {self.colliding_idx+1}."
            self.ui.ErrorMessageBrowser.setText(error_msg)
            return

        mol.toggle_bonds() if count_atoms == 1 else None
        mol.add_atom(atomic_num, np.squeeze(pos))

    def calc_position_new_atom(self, count_atoms: int, params: tuple, atom_ids: list) -> np.ndarray:
        """Calculate the position of the new atom to be added.

        :param count_atoms: number of atoms that have been added so far
        :param params: parameters that are passed for the atom
        :param atom_ids: atom ids of the selected atoms
        """
        if count_atoms == 0:
            return np.zeros([1, 3])

        dist = params[1]
        angle = params[2] if len(params) > 2 else None  # noqa: PLR2004
        dihedral = params[3] if len(params) > 3 else None  # noqa: PLR2004
        # add second atom
        if count_atoms == 1:
            return np.array([0.0, 0.0, dist])

        mol = self.main_window.mols.mols[0]
        # add third atom
        if count_atoms == 2:  # noqa: PLR2004
            coord = np.array([dist * np.sin(angle), 0, dist * np.cos(angle)])
            coord[2] = (
                mol.atoms[atom_ids[0]].position[2] - coord[2]
                if atom_ids[0] == 1
                else mol.atoms[atom_ids[0]].position[2] + coord[2]
            )
            return coord

        # add nth atom
        at1_id, at2_id, at3_id = atom_ids
        vec1 = mol.atoms[at2_id].position - mol.atoms[at1_id].position
        length = np.linalg.norm(vec1)
        vec1 = vec1 / length if length > 0 else np.array([0, 0, 1.0])
        vec2 = self._orth(mol.atoms[at3_id].position - mol.atoms[at2_id].position, vec1)
        length = np.linalg.norm(vec2)
        vec2 = vec2 / length if length > 0 else np.array([1.0, 0, 0])
        if np.linalg.norm(self._orth(vec2, vec1)) == 0:
            vec2 = np.array([0, 1.0, 0])
        vec3 = np.cross(vec1, vec2)
        vec3 /= np.linalg.norm(vec3)
        tmp = dist * np.sin(angle)
        coord = mol.atoms[at1_id].position + dist * np.cos(angle) * vec1
        coord += tmp * np.cos(dihedral) * vec2 + tmp * np.sin(dihedral) * vec3
        return coord

    def _clear_all_text(self) -> None:
        """Clear all text in the zbuilder dialog."""
        for line_edit in [
            self.ui.Box_0Element,
            self.ui.Box_1BondDistance,
            self.ui.Box_2BondAngle,
            self.ui.Box_3DihedralAngle,
        ]:
            line_edit.clear()

    def _check_value(self, *args: float, threshold: float = 1e-8) -> bool:
        """Check whether values are larger than a threshold.

        :param args: Parameter to check whether threshold is reached.
        :param threshold: Threshold to be reached.
        """
        error_msg = "Parameter values are not valid."
        vals_above_threshold = True

        for arg in args:
            vals_above_threshold = arg > threshold
            if not (vals_above_threshold):
                self.ui.ErrorMessageBrowser.setText(error_msg)
                self.err = True
                break

        return vals_above_threshold

    def _check_selected_atoms(self, *selected_atoms: int) -> bool:
        """Check if all necessary atoms are selected.

        :param selected_atoms:int: Selected Atoms to check if not -1
        """
        error_msg = "Not enough atoms selected."
        all_selected = True
        for idx in selected_atoms:
            if idx == -1:
                all_selected = False
                self.ui.ErrorMessageBrowser.setText(error_msg)
                self.err = True
                break

        return all_selected

    def _check_element(self, atomic_num: int | None) -> bool:
        """Check if the element which should be added exists.

        :param atomic_num: atomic number (core charge) which is None if not an element.
        """
        error_msg = "This is not an element."
        is_element = True
        if atomic_num == 0:
            is_element = False
            self.ui.ErrorMessageBrowser.setText(error_msg)
            self.err = True

        return is_element

    @toggle_slot
    def _set_z_matrix_row(self, tot_row: int, row: int) -> None:
        """Set a z matrix row in the table in builder dialog.

        :param tot_row: Total number of rows
        :param row: The idx of the row to be changed
        """
        param_rows = [0, 2, 4, 6]
        atom_id_rows = [0, 1, 3, 5]

        self.ui.tableWidget.setRowCount(tot_row)

        for i, text in enumerate(self.z_matrix[row]["parameter"]):
            if text is not None:
                if i == 0:  # atom id
                    temp_text = text
                elif i == 1:  # distance
                    temp_text = f"{text:.2f}"
                else:  # angles (bond angle, dihedral angle)
                    temp_text = f"{np.rad2deg(text):.2f}"

                self.ui.tableWidget.setItem(row, param_rows[i], QTableWidgetItem(temp_text))
                if param_rows[i] != 0:
                    atom_id = self.z_matrix[row]["atom_ids"][i - 1]
                    self.ui.tableWidget.setItem(row, atom_id_rows[i], QTableWidgetItem(str(atom_id + 1)))

    def _update_z_matrix(self, tot_row: int) -> None:
        """Update the complete z-matrix table.

        :param tot_row: Total number of rows
        """
        self.ui.tableWidget.setRowCount(tot_row)
        for j in range(tot_row):
            self._set_z_matrix_row(tot_row, j)

    def _delete_table_row(self, idx: int) -> None:
        """Delete a row from the table.

        :param idx: Index of the row to be deleted
        """
        self.ui.tableWidget.removeRow(idx)

    def _get_parameters(self, num_atoms: int) -> tuple[tuple, list]:
        """Return the parameter from the input boxes.

        :param num_atoms: Current number of atoms of the molecule.
        """
        element: str = self.ui.Box_0Element.text().capitalize()
        dist: float = float(self.ui.Box_1BondDistance.text())
        angle: float = np.deg2rad(float(self.ui.Box_2BondAngle.text()))
        dihedral: float = np.deg2rad(float(self.ui.Box_3DihedralAngle.text()))
        atom_ids = self.structure_widget.builder_selected_spheres

        if num_atoms == 0:
            return (element, None), []
        if num_atoms == 1:
            return (element, dist), [0]
        if num_atoms == 2:  # noqa: PLR2004
            return (element, dist, angle), atom_ids
        return (
            element,
            dist,
            angle,
            dihedral,
        ), atom_ids

    def _get_parameters_from_table(self, row: int) -> tuple:
        """Return the parameter of a specified row in the table.

        :param row: Index of the row of interest.
        """
        param_type_validity = True

        if row >= 0:
            element = str(self.ui.tableWidget.item(row, 0).text().capitalize())
            param_type_validity = bool(re.match("^[A-Z]", element))
            param_type_validity = bool(element_symbol_to_atomic_number(element)) and param_type_validity

        if row >= 1:
            dist = self.ui.tableWidget.item(row, 2).text()
            param_type_validity = bool(re.match(r"^-?\d+(\.\d+)?$", dist)) and param_type_validity

        if row >= 2:  # noqa: PLR2004
            angle = self.ui.tableWidget.item(row, 4).text()
            param_type_validity = bool(re.match(r"^-?\d+(\.\d+)?$", angle)) and param_type_validity

        if row >= 3:  # noqa: PLR2004
            dihedral = self.ui.tableWidget.item(row, 6).text()
            param_type_validity = bool(re.match(r"^-?\d+(\.\d+)?$", dihedral)) and param_type_validity

        if not param_type_validity:
            return (None,)

        if row == 0:
            return (element, None)  # type: ignore[reportPossiblyUnboundVariable]
        if row == 1:
            return (element, float(dist))  # type: ignore[reportPossiblyUnboundVariable]
        if row == 2:  # noqa: PLR2004
            return (element, float(dist), np.deg2rad(float(angle)))  # type: ignore[reportPossiblyUnboundVariable]

        return (element, float(dist), np.deg2rad(float(angle)), np.deg2rad(float(dihedral)))  # type: ignore[reportPossiblyUnboundVariable]

    def _check_z_matrix_deletion(self, idx: int) -> bool:
        """Check if the deletion of the z-matrix entry is valid.

        :param idx: Index of the row to be deleted
        """
        if idx == -1:
            error_msg = "No Atom was chosen to be deleted."
            self.ui.ErrorMessageBrowser.setText(error_msg)
            return False

        for entry in self.z_matrix:
            if idx in entry["atom_ids"]:
                error_msg = f"Cannot be deleted. Atom {idx+1} depends on this atom."
                self.ui.ErrorMessageBrowser.setText(error_msg)
                return False

        return True

    def _delete_zmat_row(self, idx: int, num_atoms: int) -> None:
        """Delete an entry in the z-matrix.

        :param idx: Index of the row to be deleted
        :param num_atoms: Total number of atoms in the molecule.
        """
        for i in range(idx, num_atoms):
            for j, at_id in enumerate(self.z_matrix[i]["atom_ids"]):
                if at_id > idx and at_id != -1:
                    self.z_matrix[i]["atom_ids"][j] -= 1

        self.z_matrix.pop(idx)

    @toggle_slot
    def _clear_upper_table_entries(self, number_of_rows: int) -> None:
        """Clear the unnecessary table entries if there is some input."""
        first_row = 0
        second_row = 1
        third_row = 2
        if number_of_rows > first_row:
            for col in range(1, 6):
                self.ui.tableWidget.setItem(first_row, col, QTableWidgetItem(""))
        if number_of_rows > second_row:
            for col in range(3, 6):
                self.ui.tableWidget.setItem(second_row, col, QTableWidgetItem(""))
        if number_of_rows > third_row:
            for col in range(5, 6):
                self.ui.tableWidget.setItem(third_row, col, QTableWidgetItem(""))
