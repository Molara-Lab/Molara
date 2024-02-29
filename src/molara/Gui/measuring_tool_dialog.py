"""Module for the measuring tool dialog."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from PySide6.QtGui import QBrush, QColor
from PySide6.QtWidgets import QDialog, QHeaderView, QMainWindow, QTableWidget, QTableWidgetItem

from molara.Gui.ui_measuring_tool import Ui_measuring_tool

if TYPE_CHECKING:
    from molara.Structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"


class MeasurementDialog(QDialog):
    """Dialog for displaying measurements."""

    def __init__(self, parent: QMainWindow) -> None:
        """Initializes the measurement dialog.

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

        self.ui.tableDistances.setColumnCount(3)
        self.ui.tableDistances.setRowCount(3)
        self.ui.tableAngles.setRowCount(3)
        self.ui.tableAngles.setColumnCount(1)
        self.ui.tablePositions.setColumnCount(5)
        self.ui.tablePositions.setRowCount(4)

        def set_resize_modes(obj: QHeaderView, modes: list) -> None:
            for i, mode in enumerate(modes):
                obj.setSectionResizeMode(i, mode)

        def set_horizontal_items(obj: QTableWidget, items: list[QTableWidgetItem]) -> None:
            for i, item in enumerate(items):
                obj.setHorizontalHeaderItem(i, item)

        def set_vertical_items(obj: QTableWidget, items: list[QTableWidgetItem]) -> None:
            for i, item in enumerate(items):
                obj.setVerticalHeaderItem(i, item)

        def color_item(text: str, color: str) -> None:
            brush = QBrush(QColor(color))
            item = QTableWidgetItem(text)
            item.setForeground(brush)
            return item

        fixed, resize, stretch = QHeaderView.Fixed, QHeaderView.ResizeToContents, QHeaderView.Stretch

        header_positions = self.ui.tablePositions.horizontalHeader()
        sidelabels_positions = self.ui.tablePositions.verticalHeader()
        header_distances = self.ui.tableDistances.horizontalHeader()
        header_angles = self.ui.tableAngles.horizontalHeader()

        set_resize_modes(header_positions, [resize, stretch, resize, resize, resize])
        set_resize_modes(sidelabels_positions, [fixed, fixed, fixed, stretch])
        set_resize_modes(header_distances, [resize, resize, stretch])
        set_resize_modes(header_angles, [stretch])

        colors = ["#f00", "#0d0", "#00f", "#cc0"]
        items_distance_horizontal = [color_item(rf"Atom {i+2}", color_i) for i, color_i in enumerate(colors[1:])]
        items_distance_vertical = [color_item(rf"Atom {i+1}", color_i) for i, color_i in enumerate(colors[:-1])]
        # for i, brush in enumerate(brushes[1:]):
        #     item_horizontal = QTableWidgetItem(rf"Atom {i+2}")
        #     item_horizontal.setForeground(brush)
        #     self.ui.tableDistances.setHorizontalHeaderItem(i, item_horizontal)
        # for i, brush in enumerate(brushes[:-1]):
        #     item_vertical = QTableWidgetItem(rf"Atom {i+1}")
        #     item_vertical.setForeground(brush)
        #     self.ui.tableDistances.setVerticalHeaderItem(i, item_vertical)

        set_horizontal_items(self.ui.tableDistances, items_distance_horizontal)
        set_vertical_items(self.ui.tableDistances, items_distance_vertical)

        item123 = QTableWidgetItem("\u2222 123")
        item234 = QTableWidgetItem("\u2222 234")
        item1234 = QTableWidgetItem("\u2222 1234")
        itemheader = QTableWidgetItem("Angle")
        set_horizontal_items(self.ui.tableAngles, [itemheader])
        # self.ui.tableAngles.setHorizontalHeaderItem(0, itemheader)
        # self.ui.tableAngles.setVerticalHeaderItem(0, item123)
        # self.ui.tableAngles.setVerticalHeaderItem(1, item234)
        # self.ui.tableAngles.setVerticalHeaderItem(2, item1234)
        set_vertical_items(self.ui.tableAngles, [item123, item234, item1234])

        set_horizontal_items(
            self.ui.tablePositions,
            [
                QTableWidgetItem("symbol"),
                QTableWidgetItem("name"),
                QTableWidgetItem("x"),
                QTableWidgetItem("y"),
                QTableWidgetItem("z"),
            ],
        )

        for i, color in enumerate(colors):
            brush = QBrush(QColor(color))
            item = QTableWidgetItem(rf"Atom {i+1}")
            item.setForeground(brush)
            self.ui.tablePositions.setVerticalHeaderItem(i, item)

    def display_metrics(self, structure: Structure, selected_atoms: list) -> None:
        """Display the metrics in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        self.display_distances(structure, selected_atoms)
        self.display_angles(structure, selected_atoms)
        self.display_dihedral(structure, selected_atoms)

    def display_distances(self, structure: Structure, selected_atoms: list) -> None:
        """Display the distances in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        for i in range(4):
            if selected_atoms[i] != -1:
                pos = structure.atoms[selected_atoms[i]].position
                self.ui.tablePositions.setItem(i, 0, QTableWidgetItem(structure.atoms[selected_atoms[i]].symbol))
                self.ui.tablePositions.setItem(i, 1, QTableWidgetItem(structure.atoms[selected_atoms[i]].name))
                self.ui.tablePositions.setItem(i, 2, QTableWidgetItem(f"{pos[0]:.3f}"))
                self.ui.tablePositions.setItem(i, 3, QTableWidgetItem(f"{pos[1]:.3f}"))
                self.ui.tablePositions.setItem(i, 4, QTableWidgetItem(f"{pos[2]:.3f}"))
            else:
                self.ui.tablePositions.setItem(i, 0, QTableWidgetItem(""))
                self.ui.tablePositions.setItem(i, 1, QTableWidgetItem(""))
                self.ui.tablePositions.setItem(i, 2, QTableWidgetItem(""))
                self.ui.tablePositions.setItem(i, 3, QTableWidgetItem(""))
                self.ui.tablePositions.setItem(i, 4, QTableWidgetItem(""))
            for k in range(i + 1, 4):
                if selected_atoms[i] == -1 or selected_atoms[k] == -1:
                    self.ui.tableDistances.setItem(i, k, QTableWidgetItem(""))
                    continue
                d = np.linalg.norm(
                    structure.atoms[selected_atoms[i]].position - structure.atoms[selected_atoms[k]].position,
                )
                self.ui.tableDistances.setItem(i, k - 1, QTableWidgetItem(f"{d.round(3):.3f}" + " \u00c5"))

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
                # angles[i].setText(f"{np.degrees(a).round(1):.3f}")
                self.ui.tableAngles.setItem(i, 0, QTableWidgetItem(f"{np.degrees(a).round(1):.3f}" + " \u00b0"))
            else:
                # angles[i].setText("")
                self.ui.tableAngles.setItem(i, 0, QTableWidgetItem(""))

    def display_dihedral(self, structure: Structure, selected_atoms: list) -> None:
        """Display the dihedral in the table.

        :param structure: The structure to measure.
        :param selected_atoms: The selected atoms.
        :return:
        """
        if selected_atoms[0] == -1 or selected_atoms[1] == -1 or selected_atoms[2] == -1 or selected_atoms[3] == -1:
            self.ui.tableAngles.setItem(2, 0, QTableWidgetItem(""))
            return

        ab = structure.atoms[selected_atoms[1]].position - structure.atoms[selected_atoms[0]].position
        bc = structure.atoms[selected_atoms[2]].position - structure.atoms[selected_atoms[1]].position
        cd = structure.atoms[selected_atoms[3]].position - structure.atoms[selected_atoms[2]].position
        nabc = np.cross(ab, bc)
        nbcd = np.cross(bc, cd)
        t = np.cross(nabc, bc)
        a = np.arctan2(np.dot(t, nbcd), np.dot(nabc, nbcd))
        a_deg = np.degrees(a)
        if a_deg > 0:
            a_deg = a_deg - 360
        a_deg = -a_deg
        self.ui.tableAngles.setItem(2, 0, QTableWidgetItem(f"{a_deg:.3f}" + " \u00b0"))

    def reset(self) -> None:
        """Reset the measurement dialog (unselect atoms and clear the tables)."""

    def reject(self) -> None:
        """Function that is called when dialog window is closed."""
        self.main_window.structure_widget.unselect_all_atoms()
        self.close()
