"""Module for voxel grid storage and manipulation.

This module provides functionality for handling three-dimensional voxel grids,
which are essential for representing molecular orbital data and electron density
distributions in space. The VoxelGrid class serves as the primary interface for
storing and manipulating these volumetric data structures.

Example Usage:
    grid = VoxelGrid()
    grid.set_grid(data_array, origin_coords, voxel_dimensions)
"""

import numpy as np


class VoxelGrid:
    """Class for voxel grid storage and manipulation.

    Attributes:
        grid (np.ndarray): The 3D array containing voxel data values
        origin (np.ndarray): The coordinates of the grid's origin point
        voxel_size (np.ndarray): The dimensions of each voxel
        voxel_number (np.ndarray): The number of voxels along each axis
        is_initialized (bool): Flag indicating if the grid has been properly set up

    """

    def __init__(self) -> None:
        """Initialise the voxel grid with empty arrays.

        Initialises:
            - grid as empty 3D array
            - origin as empty 1D array of length 3
            - voxel_size as empty 1D array of length 3
            - voxel_number as empty 1D array of length 3
        """
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
