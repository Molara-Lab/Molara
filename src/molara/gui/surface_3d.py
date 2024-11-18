"""Contain the class for the 3D surfaces."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent

    from molara.structure.molecule import Molecule
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QDialog, QMainWindow

from molara.eval.marchingcubes import marching_cubes
from molara.eval.voxel_grid import VoxelGrid


class Surface3DDialog(QDialog):
    """Class for 3D surfaces, all dialogues plotting surface will inherit from this class."""

    def __init__(self, parent: QMainWindow = None) -> None:
        """Initialize the class."""
        super().__init__(parent)
        self.molecule: None | Molecule = None
        self.voxel_grid: VoxelGrid = VoxelGrid()
        self.iso_value = 0.0
        self.drawn_surfaces = [-1, -1]
        self.vertices_1: np.ndarray = np.array([])
        self.vertices_2: np.ndarray = np.array([])

        # Color initialization
        self.color_surface_1 = np.array([255, 0, 0])
        self.color_surface_2 = np.array([0, 0, 255])
        self.color_surface_1_dialog = QColorDialog()
        self.color_surface_2_dialog = QColorDialog()
        self.color_surface_1_dialog.accepted.connect(self.change_color_surface_1)
        self.color_surface_2_dialog.accepted.connect(self.change_color_surface_2)

    def show_color_dialog_1(self) -> None:
        """Show the color dialog for the first surface."""
        self.color_surface_1_dialog.setCurrentColor(
            QColor(self.color_surface_1[0], self.color_surface_1[1], self.color_surface_1[2]),
        )
        self.color_surface_1_dialog.show()

    def show_color_dialog_2(self) -> None:
        """Show the color dialog for the second surface."""
        self.color_surface_2_dialog.setCurrentColor(
            QColor(self.color_surface_2[0], self.color_surface_2[1], self.color_surface_2[2]),
        )
        self.color_surface_2_dialog.show()

    def change_color_surface_1(self) -> None:
        """Change the color of the first surface."""
        color = self.color_surface_1_dialog.currentColor()
        self.color_surface_1 = np.array([color.red(), color.green(), color.blue()])

    def vertices_are_initialized(self) -> bool:
        """Check if the vertices are initialized."""
        return self.vertices_1.shape[0] != 0 or self.vertices_2.shape[0] != 0

    def change_color_surface_2(self) -> None:
        """Change the color of the second surface."""
        color = self.color_surface_2_dialog.currentColor()
        self.color_surface_2 = np.array([color.red(), color.green(), color.blue()])
        self.color_surface_2_dialog.close()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        """Close the dialog."""
        self.remove_surfaces()
        self.parent().structure_widget.update()
        event.accept()

    def set_iso_value(self, iso_value: float) -> None:
        """Set the iso value."""
        self.iso_value = iso_value

    def set_color_surface_1(self, color: np.ndarray) -> None:
        """Set the color of the first surface."""
        self.color_surface_1 = color

    def set_color_surface_2(self, color: np.ndarray) -> None:
        """Set the color of the second surface."""
        self.color_surface_2 = color

    def set_molecule(self, molecule: Molecule) -> None:
        """Set the molecule."""
        self.molecule = molecule

    def set_voxel_grid(self, voxel_grid: VoxelGrid) -> None:
        """Set the voxel grid."""
        self.voxel_grid = voxel_grid

    def remove_surfaces(self) -> None:
        """Remove the surfaces."""
        self.parent().structure_widget.makeCurrent()
        for surface in self.drawn_surfaces:
            if surface != -1:
                self.parent().structure_widget.renderer.remove_polygon(surface)
        self.drawn_surfaces = [-1, -1]
        self.parent().structure_widget.update()

    def display_surfaces(self) -> None:
        """Display the surfaces."""
        if self.vertices_are_initialized():
            self.draw_surfaces()
        else:
            self.visualize_surfaces()

    def draw_surfaces(self) -> None:
        """Draw the surfaces."""
        self.remove_surfaces()
        surface_1 = self.parent().structure_widget.renderer.draw_polygon(
            self.vertices_1,
            np.array([self.color_surface_1 / 255], dtype=np.float32),
        )
        self.drawn_surfaces = [surface_1]
        surface_2 = self.parent().structure_widget.renderer.draw_polygon(
            self.vertices_2,
            np.array([self.color_surface_2 / 255], dtype=np.float32),
        )
        self.drawn_surfaces.append(surface_2)
        self.parent().structure_widget.update()

    def toggle_wire_mesh(self) -> None:
        """Display the orbitals in the wire mesh mode."""
        self.parent().structure_widget.makeCurrent()
        self.parent().structure_widget.renderer.wire_mesh_surfaces = not (
            self.parent().structure_widget.renderer.wire_mesh_surfaces
        )
        self.parent().structure_widget.update()

    def visualize_surfaces(self) -> None:
        """Visualize the surface. A grid has to be set before calling this function."""
        # 24 because each voxel can have up to 12 vertices and 12 normals
        # times 6 because each vertex has 3 coordinates and each normal has 3 coordinates
        # The +1 is to save the number of vertices in the marching cubes routine.
        max_vertices = (
            24
            * (self.voxel_grid.voxel_number[0] - 1)
            * (self.voxel_grid.voxel_number[1] - 1)
            * (self.voxel_grid.voxel_number[2] - 1)
            * 6
            + 1
        )
        vertices1 = np.zeros(max_vertices, dtype=np.float32)
        vertices2 = np.zeros(max_vertices, dtype=np.float32)

        _ = marching_cubes(
            self.voxel_grid.grid,
            self.iso_value,
            self.voxel_grid.origin,
            np.array(
                [self.voxel_grid.voxel_size[0, 0], self.voxel_grid.voxel_size[1, 1], self.voxel_grid.voxel_size[2, 2]],
                dtype=np.float64,
            ),
            self.voxel_grid.voxel_number,
            vertices1,
            vertices2,
        )
        # Get the number of vertices from the last entry, to shrink the memory usage
        number_of_vertices_entries_1 = int(vertices1[-1])
        number_of_vertices_entries_2 = int(vertices2[-1])
        self.vertices_1 = vertices1[:number_of_vertices_entries_1]
        self.vertices_2 = vertices2[:number_of_vertices_entries_2]

        self.draw_surfaces()
