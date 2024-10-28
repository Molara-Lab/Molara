"""Module for the measuring tool dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QDialog, QHeaderView, QMainWindow, QTableWidget, QTableWidgetItem

from molara.gui.ui_measuring_tool import Ui_measuring_tool

if TYPE_CHECKING:
    from molara.structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"


class MeasurementDialog(QDialog):
    """Dialog for displaying measurements."""

    def __init__(self, parent: QMainWindow) -> None:  # noqa: PLR0915
        """Initialize the measurement dialog.

        :param parent: the MainWindow widget
        """
        super().__init__(
            parent,
        )
        self.main_window = parent

        self.ui = Ui_measuring_tool()
        self.ui.setupUi(self)

        self.ui.info_text.setText("Select / unselect atoms: SHIFT + Left Click on atoms.")
        self.ui.info_text_2.setText("Unselect all atoms: SHIFT + CTRL + Left Click on empty area.")

        # basic setup of the tables
        self.ui.tableDistances.setColumnCount(3)
        self.ui.tableDistances.setRowCount(3)
        self.ui.tableAngles.setRowCount(3)
        self.ui.tableAngles.setColumnCount(1)
        self.ui.tablePositions.setColumnCount(5)
        self.ui.tablePositions.setRowCount(4)

        proto_item = QTableWidgetItem()
        proto_item.setTextAlignment(Qt.AlignRight)
        self.ui.tablePositions.setItemPrototype(proto_item)

        # resize modes: specify how the tables are filled with the columns / rows
        def set_resize_modes(obj: QHeaderView, modes: list) -> None:
            for i, mode in enumerate(modes):
                obj.setSectionResizeMode(i, mode)

        fixed, resize, stretch = QHeaderView.Fixed, QHeaderView.ResizeToContents, QHeaderView.Stretch

        header_positions = self.ui.tablePositions.horizontalHeader()
        set_resize_modes(header_positions, [resize, stretch, resize, resize, resize])
        sidelabels_positions = self.ui.tablePositions.verticalHeader()
        set_resize_modes(sidelabels_positions, [fixed, fixed, fixed, stretch])
        header_distances = self.ui.tableDistances.horizontalHeader()
        set_resize_modes(header_distances, [stretch, stretch, stretch])
        sidelabels_distances = self.ui.tableDistances.verticalHeader()
        set_resize_modes(sidelabels_distances, [stretch, stretch, stretch])
        header_angles = self.ui.tableAngles.horizontalHeader()
        set_resize_modes(header_angles, [stretch])
        sidelabels_angles = self.ui.tableAngles.verticalHeader()
        set_resize_modes(sidelabels_angles, [stretch, stretch, stretch])

        # create labels for the table rows & columns
        def _set_table_labels(
            horizontal: bool,
            obj: QTableWidget,
            labels: list[str],
            colors: list[None] | list[str] | None,
            align_right: bool = True,
        ) -> None:
            _set_item = obj.setHorizontalHeaderItem if horizontal else obj.setVerticalHeaderItem
            if colors is None:
                colors = [None] * len(labels)
            for i, (label_i, color_i) in enumerate(zip(labels, colors, strict=True)):
                item = QTableWidgetItem(label_i)
                if align_right:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                if color_i is not None:
                    brush = QBrush(QColor(color_i))
                    item.setForeground(brush)
                _set_item(i, item)

        def set_horizontal_table_labels(obj: QTableWidget, labels: list[str], colors: list[str] | None = None) -> None:
            horizontal = True
            _set_table_labels(horizontal, obj, labels, colors)

        def set_vertical_table_labels(obj: QTableWidget, labels: list[str], colors: list[str] | None = None) -> None:
            vertical = False
            _set_table_labels(vertical, obj, labels, colors)

        colors = ["#f00", "#0d0", "#00f", "#cc0"]
        atom_labels = [rf"Atom {i+1}" for i in range(len(colors))]

        set_horizontal_table_labels(
            self.ui.tablePositions,
            ["Symbol", "Name", "x / \u00c5", "y / \u00c5", "z / \u00c5"],
        )
        set_vertical_table_labels(self.ui.tablePositions, atom_labels, colors)
        set_horizontal_table_labels(self.ui.tableDistances, atom_labels[1:], colors[1:])
        set_vertical_table_labels(self.ui.tableDistances, atom_labels[:-1], colors[:-1])
        set_horizontal_table_labels(self.ui.tableAngles, ["Angle"])
        set_vertical_table_labels(self.ui.tableAngles, ["\u2222 123", "\u2222 234", "\u2222 1234"])

    def display_metrics(self, structure: Structure, selected_atoms: list) -> None:
        """Display the metrics in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        self.display_positions_distances(structure, selected_atoms)
        self.display_angles(structure, selected_atoms)
        self.display_dihedral(structure, selected_atoms)

    def display_positions_distances(self, structure: Structure, selected_atoms: list) -> None:
        """Display the distances and positions in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        for i in range(4):
            if selected_atoms[i] != -1:
                pos = structure.atoms[selected_atoms[i]].position

                items = []
                items.append(QTableWidgetItem(structure.atoms[selected_atoms[i]].symbol))
                items.append(QTableWidgetItem(structure.atoms[selected_atoms[i]].name))
                items.append(QTableWidgetItem(f"{pos[0]:.3f}"))
                items.append(QTableWidgetItem(f"{pos[1]:.3f}"))
                items.append(QTableWidgetItem(f"{pos[2]:.3f}"))

                for item in items:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.ui.tablePositions.setItem(i, items.index(item), item)

            else:
                self.ui.tablePositions.setItem(i, 0, QTableWidgetItem(""))
                self.ui.tablePositions.setItem(i, 1, QTableWidgetItem(""))
                self.ui.tablePositions.setItem(i, 2, QTableWidgetItem(""))
                self.ui.tablePositions.setItem(i, 3, QTableWidgetItem(""))
                self.ui.tablePositions.setItem(i, 4, QTableWidgetItem(""))
            for k in range(i + 1, 4):
                if selected_atoms[i] == -1 or selected_atoms[k] == -1:
                    self.ui.tableDistances.setItem(i, k - 1, QTableWidgetItem(""))
                    continue
                d = np.linalg.norm(
                    structure.atoms[selected_atoms[i]].position - structure.atoms[selected_atoms[k]].position,
                )
                item = QTableWidgetItem(f"{d:.3f}" + " \u00c5")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.ui.tableDistances.setItem(i, k - 1, item)

    def display_angles(self, structure: Structure, selected_atoms: list) -> None:
        """Display the angles in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        for i in range(2):
            if selected_atoms[i] != -1 and selected_atoms[i + 1] != -1 and selected_atoms[i + 2] != -1:
                v1 = structure.atoms[selected_atoms[i]].position - structure.atoms[selected_atoms[i + 1]].position
                v2 = structure.atoms[selected_atoms[i + 2]].position - structure.atoms[selected_atoms[i + 1]].position
                a = np.arccos(
                    np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)),
                )
                item = QTableWidgetItem(f"{np.degrees(a):.3f}" + " \u00b0")
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.ui.tableAngles.setItem(i, 0, item)
            else:
                self.ui.tableAngles.setItem(i, 0, QTableWidgetItem(""))

    def display_dihedral(self, structure: Structure, selected_atoms: list) -> None:
        """Display the dihedral in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        atom_id1, atom_id2, atom_id3, atom_id4 = selected_atoms
        if atom_id1 == -1 or atom_id2 == -1 or atom_id3 == -1 or atom_id4 == -1:
            self.ui.tableAngles.setItem(2, 0, QTableWidgetItem(""))
            return

        ab = structure.atoms[atom_id2].position - structure.atoms[atom_id1].position
        bc = structure.atoms[atom_id3].position - structure.atoms[atom_id2].position
        cd = structure.atoms[atom_id4].position - structure.atoms[atom_id3].position
        # explanations on the calculation see https://math.stackexchange.com/a/47084
        nabc = np.cross(ab, bc)
        nbcd = np.cross(bc, cd)
        nabc /= np.linalg.norm(nabc)
        nbcd /= np.linalg.norm(nbcd)
        m1 = np.cross(nabc, bc / np.linalg.norm(bc))
        x = np.dot(nabc, nbcd)
        y = np.dot(m1, nbcd)
        a = np.arctan2(y, x)
        a_deg = np.degrees(a)
        item = QTableWidgetItem(f"{a_deg:.3f}" + " \u00b0")
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.ui.tableAngles.setItem(2, 0, item)

    def reject(self) -> None:
        """Close the dialog window."""
        structure_widget = self.main_window.structure_widget
        self.main_window.structure_widget.unselect_all_atoms()
        self.display_metrics(structure_widget.structures[0], structure_widget.measurement_selected_spheres)
        self.setVisible(False)
