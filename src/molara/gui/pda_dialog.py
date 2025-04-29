"""Module for the pda dialog."""

from __future__ import annotations

import numpy as np
from PySide6.QtWidgets import QDialog, QMainWindow, QTreeWidgetItem, QHeaderView, QPushButton
from PySide6.QtCore import Qt
from molara.structure.molecule import Molecule

from molara.gui.layouts.ui_pda import Ui_pda

__copyright__ = "Copyright 2024, Molara"


class PDADialog(QDialog):
    """Dialog for doing probability density analysis."""

    def __init__(self, parent: QMainWindow) -> None:  # noqa: PLR0915
        """Initialize the PDA dialog.

        :param parent: the MainWindow widget
        """
        super().__init__(
            parent,
        )
        self.main_window = parent
        self.molecule: Molecule | None = None

        self.ui = Ui_pda()
        self.ui.setupUi(self)
        self.structure_widget = self.parent().structure_widget

        self.structure_selector = self.ui.structurSelector

        # Map for reordering the data in the table
        self.item_data_idx_map = {}
        self.data_idx_item_map = {}

        # Variable to keep track of selected structures, contains the idx tuples from the map
        self.selected_structures: list[tuple] = []

        # parameters for the user
        self.electron_size = 0.03
        self.electron_colors = {
            -1: [1.0, 0.0, 0.0],
            1: [0.0, 0.0, 1.0],
        }
        self.spin_correlation_colors = {
            -1: [0.0, 1.0, 0.0],
            1: [1.0, 0.0, 1.0],
        }
        self.ref_phi = 0.0
        self.spin_correlation_radius = 0.01

        self.all_of_cluster_visible = False
        self.spin_corr_visible = False
        self.eigenvector_visible = False

        # not changeable by the user
        self.subdivisions = 20
        self.eigenvectors_present = False
        self.eigenvector_button_text = ["Show Eigenvector", "Hide Eigenvector"]
        self.spin_corr_button_text = ["Show Spin Correlations", "Hide Spin Correlations"]
        self.all_of_cluster_button_text = ["Show all of Cluster", "Hide all of Cluster"]

        # Triggers
        self.structure_selector.itemChanged.connect(self.on_check_state_changed)
        self.ui.show_all_of_clusterButton.clicked.connect(self.toggle_show_all_of_cluster)
        self.ui.deselect_all_button.clicked.connect(self.clear_selection)
        self.ui.show_spin_corrButton.clicked.connect(self.toggle_spin_correlation)
        self.ui.show_eigenvectorButton.clicked.connect(self.toggle_show_eigenvector)

        self.ui.Spin_correlationSpinBox.valueChanged.connect(self.update_spin_correlation)
        self.ui.eigenvectorSpinBox.valueChanged.connect(self.update_eigenvector)
        self.ui.deflectionSpinBox.valueChanged.connect(self.update_eigenvector)

        self.ui.reference_phiLineEdit.returnPressed.connect(self.update_ref_phi)

    def initialize_dialog(self) -> None:
        """Initialize the dialog.

        Check for the presence of pda data in the main window and set the tree widget accordingly.
        """
        if self.isVisible():
            return

        if len(self.structure_widget.structures) != 1:
            return
        self.molecule = self.structure_widget.structures[0]
        if not self.molecule.pda_data["initialized"]:
            return

        if self.molecule.pda_data["clusters"][0]["subclusters"][0]["pda_eigenvectors"].size > 0:
            self.eigenvectors_present = True
        else:
            self.eigenvectors_present = False

        self.ref_phi = self.molecule.pda_data['ref_phi']
        self.set_structure_selector()

        if self.eigenvectors_present:
            self.ui.eigenvectorSpinBox.setEnabled(True)
            self.ui.deflectionSpinBox.setEnabled(True)
            self.ui.show_eigenvectorButton.setEnabled(True)
            self.ui.eigenvectorSpinBox.setRange(1, self.molecule.pda_data['clusters'][0]['subclusters'][0]['pda_eigenvectors'].shape[0])
            self.ui.eigenvectorSpinBox.setValue(1)
            self.set_eigenvalue_label()
        else:
            self.ui.eigenvectorSpinBox.setEnabled(False)
            self.ui.deflectionSpinBox.setEnabled(False)
            self.ui.show_eigenvectorButton.setEnabled(False)

        self.ui.show_eigenvectorButton.setText("Show eigenvector")
        self.ui.show_all_of_clusterButton.setText("Show all of cluster")
        self.ui.show_spin_corrButton.setText("Show spin correlations")
        self.ui.deselect_all_button.setText("Deselect all")
        # set up the buttons

        self.show()

    def closeEvent(self, event) -> None:  # noqa: N802
        """Close the dialog."""
        self.clear_selection()
        self.ui.show_all_of_clusterButton.setText("")
        self.ui.show_spin_corrButton.setText("")
        self.ui.deselect_all_button.setText("")
        self.structure_selector.clear()
        self.molecule = None
        self.selected_structures.clear()
        self.item_data_idx_map.clear()
        self.data_idx_item_map.clear()
        self.all_of_cluster_visible = False
        self.spin_corr_visible = False
        self.eigenvector_visible = False

        if "all_of_cluster" in self.structure_widget.renderer.objects3d:
            self.structure_widget.renderer.remove_object("all_of_cluster")
        if "Spin_corr" in self.structure_widget.renderer.objects3d:
            self.structure_widget.renderer.remove_object("Spin_corr")
        if "eigenvector" in self.structure_widget.renderer.objects3d:
            self.structure_widget.renderer.remove_object("eigenvector")

        # update all button texts:
        self.ui.show_all_of_clusterButton.setText(self.all_of_cluster_button_text[0])
        self.ui.show_spin_corrButton.setText(self.spin_corr_button_text[0])
        self.ui.show_eigenvectorButton.setText(self.eigenvector_button_text[0])

        self.structure_widget.update()
        event.accept()

    def set_structure_selector(self) -> None:
        """Set up the structure selector."""
        self.structure_selector.setColumnCount(4)
        self.structure_selector.setHeaderLabels(["ID", "Weight / %", "Min ΔΦ", "Max ΔΦ"])
        self.structure_selector.setRootIsDecorated(True)  # Shows expand/collapse arrow

        for i in range(len(self.molecule.pda_data['clusters'])):
            cluster = self.molecule.pda_data['clusters'][i]
            top_item = QTreeWidgetItem()
            data_index = (i, -1)

            weight = cluster['sample_size'] / self.molecule.pda_data['sample_size'] * 100

            # set text right bound
            top_item.setTextAlignment(1, Qt.AlignRight)
            top_item.setTextAlignment(2, Qt.AlignRight)
            top_item.setTextAlignment(3, Qt.AlignRight)

            # values for sorting
            top_item.setData(1, Qt.UserRole, weight)
            top_item.setData(2, Qt.UserRole, cluster['min_phi'])
            top_item.setData(3, Qt.UserRole, cluster['max_phi'])

            # values for display
            top_item.setText(1, f"{weight:>6.1f}")
            top_item.setText(2, f"{cluster['min_phi'] - self.ref_phi:>6.3f}")
            top_item.setText(3, f"{cluster['max_phi'] - self.ref_phi:>6.3f}")

            # Add checkbox to first column
            top_item.setFlags(top_item.flags() | Qt.ItemIsUserCheckable)
            top_item.setCheckState(0, Qt.Unchecked)
            top_item.setText(0, f"{i + 1:>5}")

            if len(cluster['subclusters']) > 1:
                for j in range(len(cluster['subclusters'])):
                    child = QTreeWidgetItem()
                    data_index_subcluster = (i, j)

                    weight = cluster['subclusters'][j]['sample_size'] / cluster['sample_size'] * 100
                    min_phi = cluster['subclusters'][j]['min_phi']
                    max_phi = cluster['subclusters'][j]['max_phi']

                    # set text right bound
                    child.setTextAlignment(1, Qt.AlignRight)
                    child.setTextAlignment(2, Qt.AlignRight)
                    child.setTextAlignment(3, Qt.AlignRight)

                    # values for sorting
                    child.setData(1, Qt.UserRole, weight)
                    child.setData(2, Qt.UserRole, min_phi)
                    child.setData(3, Qt.UserRole, max_phi)

                    # values for display
                    child.setText(1, f"{weight:>6.1f}")
                    child.setText(2, f"{min_phi - self.ref_phi:>6.3f}")
                    child.setText(3, f"{max_phi - self.ref_phi:>6.3f}")

                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    child.setCheckState(0, Qt.Unchecked)
                    child.setText(0, f"{j + 1:>5}")

                    self.item_data_idx_map[child] = data_index_subcluster
                    self.data_idx_item_map[data_index_subcluster] = child
                    top_item.addChild(child)

            self.item_data_idx_map[top_item] = data_index
            self.data_idx_item_map[data_index] = top_item
            self.structure_selector.addTopLevelItem(top_item)

        # set size of the columns so that each column has the same width
        total_width = self.structure_selector.viewport().width()  # Or tree.width(), depending on layout
        other_columns_width = 0
        self.structure_selector.setColumnWidth(0, total_width)  # Set the first column to 0 width

        header = self.structure_selector.header()
        header.setSectionResizeMode(QHeaderView.Fixed)

        for i in range(1, 4):
            self.structure_selector.resizeColumnToContents(i)
            other_columns_width += self.structure_selector.columnWidth(i)

        # set the first column to be the total width minus the widths of all other columns
        # 20 is the padding (width of scrollbar)
        self.structure_selector.setColumnWidth(0, total_width - other_columns_width - 20)

        self.structure_selector.setSortingEnabled(True)
        self.structure_selector.sortItems(0, Qt.AscendingOrder)

        # check the first item
        first_item = self.structure_selector.topLevelItem(0)
        first_item.setCheckState(0, Qt.Checked)

    def on_check_state_changed(self, item: QTreeWidgetItem) -> None:
        """Handles the change in item check state"""
        if self.all_of_cluster_visible:
            self.hide_all_of_cluster()
            self.all_of_cluster_visible = False
            top_level_item = self.data_idx_item_map[(self.selected_structures[0][0], -1)]
            if top_level_item.childCount() > 0:
                old_item = self.data_idx_item_map[self.selected_structures[0]]
            else:
                old_item = top_level_item
            old_item.setCheckState(0, Qt.Unchecked)
            item.setCheckState(0, Qt.Checked)

        if self.spin_corr_visible:
            self.hide_spin_correlation()
            self.update_toggle_button(self.spin_corr_visible, self.ui.show_spin_corrButton, self.spin_corr_button_text)

        check_state = item.checkState(0)  # Get the new check state
        data_index = self.item_data_idx_map[item]
        if check_state == Qt.Checked:
            if data_index[1] == -1:
                data_index = (data_index[0], 0)
            self.draw_electron_arrangement(data_index)
        else:
            self.remove_electron_arrangement(data_index)

        # Check if the item has children
        if item.childCount() > 1:
            child = self.data_idx_item_map[(data_index[0], 0)]
            if check_state == Qt.Checked:
                child.setCheckState(0, Qt.Checked)  # Check the first child
            else:
                child.setCheckState(0, Qt.Unchecked)
        elif data_index[1] == 0 and item.parent() is not None:
            if check_state == Qt.Checked:
                item.parent().setCheckState(0, Qt.Checked)  # Check the first child
            else:
                item.parent().setCheckState(0, Qt.Unchecked)

    def draw_electron_arrangement(self, data_index: tuple[int, int]) -> None:
        """Draw the electron arrangement for a given cluster."""
        if self.molecule is None:
            return
        if data_index in self.selected_structures:
            return
        cluster_data = self.molecule.pda_data['clusters'][data_index[0]]
        electron_positions = cluster_data['subclusters'][data_index[1]]['electron_positions']
        spins = cluster_data['subclusters'][data_index[1]]['electrons_spin']

        # Get the colors array according to the spin if two opposite spin electron are in the same spot,
        # color them purple
        colors = np.zeros((electron_positions.shape[0], 3), dtype=np.float32)
        for i in range(electron_positions.shape[0]):
            for j in range(i + 1, electron_positions.shape[0]):
                if np.array_equal(electron_positions[i], electron_positions[j]) and spins[i] != spins[j]:
                    colors[i] = [0.8, 0.0, 0.8]
                    colors[j] = [0.8, 0.0, 0.8]
                    break
            else:
                colors[i] = self.electron_colors[spins[i]]



        electron_sizes = (np.ones(cluster_data['subclusters'][data_index[1]]['electron_positions'].shape[0],
                                  dtype=np.float32) * self.electron_size)

        # Draw the electron arrangement
        self.structure_widget.renderer.draw_spheres(
            f"electron_arrangement-{data_index[0]}_{data_index[1]}",
            electron_positions,
            electron_sizes,
            colors,
            self.subdivisions,
        )

        self.selected_structures.append(data_index)
        self.structure_widget.update()

    def draw_all_of_cluster(self, cluster_index: int) -> None:
        """Draw all of the electron arrangements for a given cluster."""
        if self.molecule is None:
            return
        cluster = self.molecule.pda_data['clusters'][cluster_index]
        data_indices = [(cluster_index, subcluster_index) for subcluster_index
                        in range(len(cluster['subclusters']))]
        electron_positions_list = []
        colors_list = []
        electron_sizes_list = []
        for data_index in data_indices:
            if f"electron_arrangement-{data_index[0]}_{data_index[1]}" in self.selected_structures:
                self.remove_electron_arrangement(data_index)
            cluster_data = self.molecule.pda_data['clusters'][data_index[0]]
            electron_positions_list.append(cluster_data['subclusters'][data_index[1]]['electron_positions'])
            spins = cluster_data['subclusters'][data_index[1]]['electrons_spin']

            # Get the colors array according to the spin
            colors_list.append(np.array([self.electron_colors[spin] for spin in spins], dtype=np.float32))
            electron_sizes_list.append(
                np.ones(cluster_data['subclusters'][data_index[1]]['electron_positions'].shape[0],
                        dtype=np.float32) * self.electron_size)

        # Draw the electron arrangements
        electron_positions = np.concatenate(electron_positions_list, axis=0, dtype=np.float32)
        electron_sizes = np.concatenate(electron_sizes_list, axis=0, dtype=np.float32)
        colors = np.concatenate(colors_list, axis=0, dtype=np.float32)

        self.structure_widget.renderer.draw_spheres(
            f"all_of_cluster",
            electron_positions,
            electron_sizes,
            colors,
            self.subdivisions,
        )

        self.structure_widget.update()

    def remove_electron_arrangement(self, data_index: tuple[int, int]) -> None:
        """Remove the electron arrangement for a given cluster."""
        if self.molecule is None:
            return
        if data_index[1] == -1:
            data_index = (data_index[0], 0)
        if data_index in self.selected_structures:
            self.structure_widget.renderer.remove_object(
                f"electron_arrangement-{data_index[0]}_{data_index[1]}",
            )
            self.selected_structures.remove(data_index)
        self.structure_widget.update()

    @staticmethod
    def update_toggle_button(visible: bool, button: QPushButton, text: list) -> None:
        """Update the text on a button

        :param visible: boolean indicating if the selection is visible
        :param button: the button to update
        :param text: the text to set on the button, list containing one option for visible and one for invisible
        """
        if not visible:
            button.setText(text[0])
        else:
            button.setText(text[1])

    def hide_all_of_cluster(self) -> None:
        """Hide all the electron arrangements."""
        if "all_of_cluster" not in self.structure_widget.renderer.objects3d:
            return

        self.structure_widget.renderer.remove_object("all_of_cluster")
        self.structure_selector.itemChanged.disconnect()
        top_level_item = self.data_idx_item_map[(self.selected_structures[0][0], -1)]
        top_level_item.setCheckState(0, Qt.Unchecked)
        for i in range(top_level_item.childCount()):
            item = top_level_item.child(i)
            item.setCheckState(0, Qt.Unchecked)
        self.structure_selector.itemChanged.connect(self.on_check_state_changed)
        if top_level_item.childCount() > 0:
            item = self.data_idx_item_map[(self.selected_structures[0])]
            item.setCheckState(0, Qt.Checked)

        self.all_of_cluster_visible = False
        self.update_toggle_button(self.all_of_cluster_visible, self.ui.show_all_of_clusterButton, self.all_of_cluster_button_text)
        self.structure_widget.update()

    def show_all_of_cluster(self) -> None:
        """Show all the electron arrangements."""
        self.draw_all_of_cluster(self.selected_structures[0][0])
        self.structure_selector.itemChanged.disconnect()
        top_level_item = self.data_idx_item_map[(self.selected_structures[0][0], -1)]
        top_level_item.setCheckState(0, Qt.Checked)
        for i in range(top_level_item.childCount()):
            item = top_level_item.child(i)
            item.setCheckState(0, Qt.Checked)

        self.all_of_cluster_visible = True
        self.update_toggle_button(self.all_of_cluster_visible, self.ui.show_all_of_clusterButton, self.all_of_cluster_button_text)
        self.structure_selector.itemChanged.connect(self.on_check_state_changed)

    def toggle_show_all_of_cluster(self) -> None:
        """Toggle the visibility of all arrangements of the cluster."""
        if self.molecule is None:
            return
        if self.spin_corr_visible:
            return
        if not self.selected_structures:
            return
        if self.data_idx_item_map[(self.selected_structures[0][0], -1)].childCount() == 0:
            return

        if not self.all_of_cluster_visible:
            if len(self.selected_structures) != 1:
                self.all_of_cluster_visible = False
                return
            else:
                self.show_all_of_cluster()
        else:
            self.hide_all_of_cluster()

        self.update_toggle_button(self.all_of_cluster_visible, self.ui.show_all_of_clusterButton, self.all_of_cluster_button_text)

    def clear_selection(self) -> None:
        """Clear the selection of the tree widget."""
        self.all_of_cluster_visible = False
        if "all_of_cluster" in self.structure_widget.renderer.objects3d:
            self.structure_widget.renderer.remove_object("all_of_cluster")
        self.update_toggle_button(self.all_of_cluster_visible, self.ui.show_all_of_clusterButton, self.all_of_cluster_button_text)
        for i in range(self.structure_selector.topLevelItemCount()):
            item = self.structure_selector.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                item.setCheckState(0, Qt.Unchecked)
            for j in range(item.childCount()):
                child = item.child(j)
                if child.checkState(0) == Qt.Checked:
                    child.setCheckState(0, Qt.Unchecked)

    def toggle_spin_correlation(self) -> None:
        """Toggle the visibility of the spin correlations."""
        if self.molecule is None:
            return
        if self.all_of_cluster_visible:
            return
        if len(self.selected_structures) != 1:
            return
        if self.data_idx_item_map[(self.selected_structures[0][0], -1)].childCount() == 0:
            return

        if not self.spin_corr_visible:
            self.show_spin_correlation()
        else:
            self.hide_spin_correlation()

        self.update_toggle_button(self.spin_corr_visible, self.ui.show_spin_corrButton, self.spin_corr_button_text)

    def hide_spin_correlation(self) -> None:
        """Hide the spin correlations."""
        if "Spin_corr" not in self.structure_widget.renderer.objects3d:
            return

        self.structure_widget.renderer.remove_object("Spin_corr")
        self.spin_corr_visible = False
        self.update_toggle_button(self.spin_corr_visible, self.ui.show_spin_corrButton, self.spin_corr_button_text)
        self.structure_widget.update()

    def show_spin_correlation(self) -> None:
        """Show the spin correlations."""
        subdivisions = 10

        if self.molecule is None:
            return

        threshold = self.ui.Spin_correlationSpinBox.value() / 100
        electron_pairs_corr = []
        cluster_data = self.molecule.pda_data['clusters'][self.selected_structures[0][0]]
        if self.selected_structures[0][1] == -1:
            subcluster_index = 0
        else:
            subcluster_index = self.selected_structures[0][1]
        subcluster_data = cluster_data['subclusters'][subcluster_index]
        for i in range(cluster_data['spin_correlations'].shape[0]):
            for j in range(i + 1, cluster_data['spin_correlations'].shape[1]):
                spin_cor = cluster_data['spin_correlations'][i, j]
                if abs(spin_cor) >= threshold:
                    electron_pairs_corr.append([i, j, spin_cor])
        positions = []
        radii = []
        colors = []
        for pair in electron_pairs_corr:
            positions.append(
                [subcluster_data['electron_positions'][pair[0]], subcluster_data['electron_positions'][pair[1]]]
            )
            colors.append(self.spin_correlation_colors[-1] if pair[2] < 0 else self.spin_correlation_colors[1])
            radii.append(self.spin_correlation_radius)
        if len(electron_pairs_corr) == 0:
            return
        self.structure_widget.renderer.draw_cylinders_from_to('Spin_corr', np.array(positions, dtype=np.float32), np.array(radii, dtype=np.float32), np.array(colors, dtype=np.float32), subdivisions)
        self.structure_widget.update()
        self.spin_corr_visible = True

    def update_spin_correlation(self) -> None:
        """Update the spin correlation."""
        if self.molecule is None:
            return
        if self.all_of_cluster_visible:
            return
        if len(self.selected_structures) != 1:
            return
        if self.eigenvector_visible:
            return

        if self.spin_corr_visible:
            self.hide_spin_correlation()
            self.show_spin_correlation()

    def show_eigenvector(self) -> None:
        """Show the eigenvector of the selected structure."""
        if self.molecule is None:
            return
        if self.all_of_cluster_visible:
            return
        if len(self.selected_structures) != 1:
            return

        if "eigenvector" in self.structure_widget.renderer.objects3d:
            self.structure_widget.renderer.remove_object("eigenvector")

        cluster_data = self.molecule.pda_data['clusters'][self.selected_structures[0][0]]
        if self.selected_structures[0][1] == -1:
            subcluster_index = 0
        else:
            subcluster_index = self.selected_structures[0][1]
        subcluster_data = cluster_data['subclusters'][subcluster_index]
        eigenvectors = subcluster_data['pda_eigenvectors']
        if eigenvectors.size == 0:
            return

        positions = []
        colors = []
        deflection = self.ui.deflectionSpinBox.value()
        eigenvector_index = self.ui.eigenvectorSpinBox.value() - 1
        for i in range(eigenvectors.shape[1]):
            electron_position = subcluster_data['electron_positions'][i]
            end_position = electron_position + eigenvectors[eigenvector_index, i] * deflection
            if np.linalg.norm(eigenvectors[eigenvector_index, i] * deflection) < 0.01:
                continue
            positions.append([electron_position, end_position])
            if subcluster_data['electrons_spin'][i] == -1:
                colors.append(self.electron_colors[-1])
            else:
                colors.append(self.electron_colors[1])

        if positions:
            self.structure_widget.renderer.draw_arrows(
                'eigenvector',
                np.array(positions, dtype=np.float32),
                np.array(colors, dtype=np.float32),
                10,
                arrow_ratio=0.2,
            )

        self.eigenvector_visible = True
        self.update_toggle_button(self.eigenvector_visible, self.ui.show_eigenvectorButton, self.eigenvector_button_text)
        self.structure_widget.update()

    def hide_eigenvector(self) -> None:
        """Hide the eigenvector."""
        if "eigenvector" not in self.structure_widget.renderer.objects3d:
            return

        self.structure_widget.renderer.remove_object("eigenvector")
        self.eigenvector_visible = False
        self.update_toggle_button(self.eigenvector_visible, self.ui.show_eigenvectorButton, self.eigenvector_button_text)
        self.structure_widget.update()

    def toggle_show_eigenvector(self) -> None:
        """Toggle the visibility of the eigenvector."""
        if self.molecule is None:
            return
        if self.all_of_cluster_visible:
            return
        if len(self.selected_structures) != 1:
            return
        if self.spin_corr_visible:
            return

        if self.eigenvector_visible:
            self.hide_eigenvector()
        else:
            self.show_eigenvector()

        self.update_toggle_button(self.eigenvector_visible, self.ui.show_eigenvectorButton, self.eigenvector_button_text)

    def update_eigenvector(self) -> None:
        """Update the eigenvector."""
        if self.molecule is None:
            return
        if self.all_of_cluster_visible:
            return
        if len(self.selected_structures) != 1:
            return
        if self.spin_corr_visible:
            return

        self.set_eigenvalue_label()

        if not self.eigenvector_visible:
            return

        self.hide_eigenvector()
        self.show_eigenvector()

    def set_eigenvalue_label(self) -> None:
        """Set the eigenvalue label."""
        cluster_data = self.molecule.pda_data['clusters'][self.selected_structures[0][0]]
        if self.selected_structures[0][1] == -1:
            subcluster_index = 0
        else:
            subcluster_index = self.selected_structures[0][1]
        subcluster_data = cluster_data['subclusters'][subcluster_index]
        eigenvalue = subcluster_data['pda_eigenvalues'][self.ui.eigenvectorSpinBox.value() - 1]
        self.ui.eigenvalueLabel.setText(f"{eigenvalue:8.4f}")

    def update_ref_phi(self) -> None:
        """Update the reference phi value."""
        try:
            self.ref_phi = float(self.ui.reference_phiLineEdit.text())
            self.set_phi_values()
        except ValueError:
            self.ui.reference_phiLineEdit.setText(f"Enter a valid number!")

    def set_phi_values(self) -> None:
        """Set the phi values in the structure selector."""
        for i in range(self.structure_selector.topLevelItemCount()):
            item = self.structure_selector.topLevelItem(i)
            item.setText(2, f"{self.molecule.pda_data['clusters'][i]['min_phi'] - self.ref_phi:>6.3f}")
            item.setText(3, f"{self.molecule.pda_data['clusters'][i]['max_phi'] - self.ref_phi:>6.3f}")
            for j in range(item.childCount()):
                child = item.child(j)
                child.setText(2, f"{self.molecule.pda_data['clusters'][i]['subclusters'][j]['min_phi'] - self.ref_phi:>6.3f}")
                child.setText(3, f"{self.molecule.pda_data['clusters'][i]['subclusters'][j]['max_phi'] - self.ref_phi:>6.3f}")

