"""This module contains the tests for the exporter module."""

from __future__ import annotations

import time
import unittest
from pathlib import Path

import numpy as np
from molara.Molecule.structure import Structure
from molara.Structure.io.exporter import XyzExporter


class TestXyzExporter(unittest.TestCase):
    """This class contains the tests for the XyzExporter class."""

    def setUp(self) -> None:
        """Instantiates the XyzExporter object."""
        self.exporter = XyzExporter("output.xyz")
        self.timestamp = int(time.time())
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
        filename = f"output_temporary_{self.timestamp}.xyz"
        assert Path(filename).exists() is False
        self.exporter.write_structure(self.structure)
        # Assert that the output file exists
        assert Path(filename).exists()

        # Assert that the output file has the expected content
        with open(filename) as file:
            num_atoms = int(file.readline().strip())
            assert num_atoms == self.atomic_numbers.size
        data = np.genfromtxt(
            filename,
            skip_header=2,
            dtype=str,
        )
        assert data.shape == (6, 4)
        assert data[:, 0].tolist() == ["C", "O", "He", "Li", "H", "N"]
        assert data[:, 1:].tolist() == self.coordinates.tolist()
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
