"""Contains the tests for the exporter module."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

import numpy as np
from molara.structure.io.exporter import GeneralExporter, XyzExporter
from molara.structure.structure import Structure
from numpy.testing import assert_array_equal


class TestXyzExporter(unittest.TestCase):
    """Contains the tests for the XyzExporter class."""

    def setUp(self) -> None:
        """Instantiate the XyzExporter object."""
        # self.timestamp = int(time.time())
        with NamedTemporaryFile(suffix=".xyz") as file:
            self.filename = file.name
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


class TestGeneralExporter(unittest.TestCase):
    """Contains the tests for the GeneralExporter class."""

    def setUp(self) -> None:
        """Instantiate the GeneralExporter object."""
        with NamedTemporaryFile(suffix=".xyz") as file:
            self.filename_xyz = file.name
        self.exporter_xyz = GeneralExporter(self.filename_xyz)
        self.atomic_numbers = np.array([9, 10, 17, 30, 15, 3])  # F, Ne, Cl, Zn, P, Li
        self.coordinates = np.array(
            [
                [7.0, 3.0, 9.0],  # F
                [1.3, -20.0, -300.0],  # Ne
                [4.0e-3, 5.0e-4, 6.0e-2],  # Cl
                [10.0, 11.0, 12.0],  # Zn
                [13.2, 14.1, 15.123],  # P
                [0, 0, 0],  # Li
            ],
        )
        self.structure = Structure(
            atomic_numbers=self.atomic_numbers,
            coordinates=self.coordinates,
        )

    def test_write_structure_to_xyz(self) -> None:
        """Tests the write_structure method of the GeneralExporter class."""
        assert Path(self.filename_xyz).exists() is False
        self.exporter_xyz.write_structure(self.structure)
        # Assert that the output file exists
        assert Path(self.filename_xyz).exists()

        # Assert that the output file has the expected content
        with open(self.filename_xyz) as file:
            num_atoms = int(file.readline().strip())
            assert num_atoms == self.atomic_numbers.size
        data = np.genfromtxt(
            self.filename_xyz,
            skip_header=2,
            dtype=str,
        )
        assert data.shape == (6, 4)
        assert data[:, 0].tolist() == ["F", "Ne", "Cl", "Zn", "P", "Li"]
        coordinates = data[:, 1:].astype(float)
        assert_array_equal(coordinates, self.coordinates)
