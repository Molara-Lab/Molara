"""Module for voxel grid storage and manipulation."""

import numpy as np


class VoxelGrid:
    """Class for voxel grid storage and manipulation."""

    def __init__(self):
        """Initialize the voxel grid."""
        self.grid = np.array([])
        self.origin = np.array([])
        self.voxel_size = np.array([])
        self.voxel_number = np.array([])
        self.is_initialized = False

    def set_grid(self, grid: np.ndarray, origin: np.ndarray, voxel_size: np.ndarray):
        """Set the grid, origin, and voxel size."""
        self.grid = grid
        self.origin = origin
        self.voxel_size = voxel_size
        self.voxel_number = np.array(grid.shape)
        self.is_initialized = True
