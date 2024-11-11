"""Module for displaying 3D surfaces from cube files."""

from __future__ import annotations

import numpy as np
from PySide6.QtWidgets import QDialog, QMainWindow

from molara.eval.marchingcubes import marching_cubes
from molara.gui.ui_surface_3d_dialog import Ui_Surface3D_dialog
from molara.structure.molecule import Molecule

__copyright__ = "Copyright 2024, Molara"


class Surface3DDialog(QDialog):
    """Dialog for displaying MOs."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initialize the MOs dialog.

        params:
        parent: MainWindow: The widget of the MainWindow.
        """
        super().__init__(
            parent,
        )
        self.molecule: None | Molecule = None
        self.ui = Ui_Surface3D_dialog()
        self.ui.setupUi(self)
        self.ui.visualize_surfaceButton.clicked.connect(self.visualize_surface)
        self.ui.isoSpinBox.valueChanged.connect(self.visualize_surface)

    def initialize_dialog(self):
        """Initialize the dialog."""
        self.molecule = self.parent().structure_widget.structures[0]

    def visualize_surface(self) -> None:
        """Visualize the surface."""
        print("Visualizing surface")
        print(self.molecule.voxel_grid.grid.shape)
        print(self.molecule.voxel_grid.origin)
        print(self.molecule.voxel_grid.voxel_size)
        print(self.molecule.voxel_grid.voxel_number)

        # 24 because each voxel can have up to 12 vertices and 12 normals
        # times 6 because each vertex has 3 coordinates and each normal has 3 coordinates
        # The +1 is to save the number of vertices in the marching cubes routine.
        max_vertices = (
            24
            * (self.molecule.voxel_grid.voxel_number[0] - 1)
            * (self.molecule.voxel_grid.voxel_number[1] - 1)
            * (self.molecule.voxel_grid.voxel_number[2] - 1)
            * 6
            + 1
        )
        vertices1 = np.zeros(max_vertices, dtype=np.float32)
        vertices2 = np.zeros(max_vertices, dtype=np.float32)

        iso = self.ui.isoSpinBox.value()

        _ = marching_cubes(
            self.molecule.voxel_grid.grid,
            iso,
            self.molecule.voxel_grid.origin,
            np.array(
                [
                    self.molecule.voxel_grid.voxel_size[0, 0],
                    self.molecule.voxel_grid.voxel_size[1, 1],
                    self.molecule.voxel_grid.voxel_size[2, 2],
                ],
                dtype=np.float64,
            ),
            self.molecule.voxel_grid.voxel_number,
            vertices1,
            vertices2,
        )

        number_of_vertices_entries_1 = int(vertices1[-1])
        number_of_vertices_entries_2 = int(vertices2[-1])
        vertices1 = vertices1[:number_of_vertices_entries_1]
        vertices2 = vertices2[:number_of_vertices_entries_2]

        orb1 = self.parent().structure_widget.renderer.draw_polygon(
            vertices1,
            np.array([[1, 0, 0]], dtype=np.float32),
        )
        orb2 = self.parent().structure_widget.renderer.draw_polygon(
            vertices2,
            np.array([[0, 0, 1]], dtype=np.float32),
        )
        self.parent().structure_widget.update()
