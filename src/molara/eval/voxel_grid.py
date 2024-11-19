"""Module for voxel grid storage and manipulation."""

import numpy as np


class VoxelGrid:
    """Class for voxel grid storage and manipulation."""

    def __init__(self) -> None:
        """Initialize the voxel grid."""
        self.grid = np.array([])
        self.origin = np.array([])
        self.voxel_size = np.array([])
        self.voxel_number = np.array([])
        self.is_initialized = False

    def set_grid(self, grid: np.ndarray, origin: np.ndarray, voxel_size: np.ndarray) -> None:
        """Set the grid, origin, and voxel size.

        :param grid: 3D array representing the voxel grid
        :param origin: 1D array of length 3 representing the origin of the grid
        :param voxel_size: 3D array of length representing the voxel size for each cartesian direction
        """
        number_of_cartesian_directions = 3
        assert grid.ndim == number_of_cartesian_directions
        assert origin.shape == (number_of_cartesian_directions,)
        assert voxel_size.shape == (number_of_cartesian_directions, number_of_cartesian_directions)
        assert np.any(voxel_size > 0)

        self.grid = grid
        self.origin = origin
        self.voxel_size = voxel_size
        self.voxel_number = np.array(grid.shape)
        self.is_initialized = True
