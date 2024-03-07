"""This module contains the tests for the exporter module."""

from __future__ import annotations

import time
import unittest
from pathlib import Path

import numpy as np
from molara.Structure.io.exporter import XyzExporter
from molara.Structure.structure import Structure
from numpy.testing import assert_array_equal


class TestXyzExporter(unittest.TestCase):
    """This class contains the tests for the XyzExporter class."""

    def setUp(self) -> None:
        """Instantiates the XyzExporter object."""
        self.timestamp = int(time.time())
        self.filename = f"output_temporary_{self.timestamp}.xyz"
        self.exporter = XyzExporter(self.filename)
        self.atomic_numbers = np.array([6, 8, 2, 3, 1, 7])  # C, O, He, Li, H, N
        self.coordinates = np.array(
            [
                [0.0, 0.0, 0.0],  # C
                [0.9, 2.7, 1.6],  # O
                [-0.4, 1.0, 3.3],  # He
                [10.1, -10.2, -10.3],  # Li
                [1.3, -1.4, 0.5],  # H
                [2.0, 4.0, 6.0],  # N
            ],
        )
        self.structure = Structure(
            atomic_numbers=self.atomic_numbers,
            coordinates=self.coordinates,
        )

    def test_write_structure(self) -> None:
        """Tests the write_structure method of the XyzExporter class."""
        assert Path(self.filename).exists() is False
        self.exporter.write_structure(self.structure)
        # Assert that the output file exists
        assert Path(self.filename).exists()

        # Assert that the output file has the expected content
        with open(self.filename) as file:
            num_atoms = int(file.readline().strip())
            assert num_atoms == self.atomic_numbers.size
        data = np.genfromtxt(
            self.filename,
            skip_header=2,
            dtype=str,
        )
        assert data.shape == (6, 4)
        assert data[:, 0].tolist() == ["C", "O", "He", "Li", "H", "N"]
        coordinates = data[:, 1:].astype(float)
        assert_array_equal(coordinates, self.coordinates)

        # Delete file
        Path(f"output_temporary_{self.timestamp}.xyz").unlink()


# class TestGeneralExporter(unittest.TestCase):
#     """This class contains the tests for the GeneralExporter class."""

#     def test_write_structure_with_xyz_file(self) -> None:
#         """Tests the write_structure method of the GeneralExporter class with an XYZ file."""
#         exporter = GeneralExporter("output.xyz")
#         structure = Structure()
#         # Add atoms to the structure
#         # ...
#         exporter.write_structure(structure)
#         # Assert that the output file exists
#         assert Path("output.xyz").exists()

#     def test_write_structure_with_unknown_file_format(self) -> None:
#         """Tests the write_structure method of the GeneralExporter class with an unknown file format."""
#         exporter = GeneralExporter("output.txt")
#         structure = Structure()
#         # Add atoms to the structure
#         # ...
#         # Assert that a FileFormatError is raised
#         with pytest.raises(FileFormatError):
#             exporter.write_structure(structure)
