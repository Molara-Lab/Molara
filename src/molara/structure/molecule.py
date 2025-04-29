"""Contains the Molecule class."""

from __future__ import annotations

import numpy as np

from molara.eval.voxel_grid import VoxelGrid3D
from molara.structure.molecularorbitals import MolecularOrbitals
from molara.structure.structure import Structure

__copyright__ = "Copyright 2024, Molara"


class Molecule(Structure):
    """Creates a new Molecule object."""

    def __init__(
        self,
        atomic_numbers: np.ndarray,
        coordinates: np.ndarray,
        header: str | None = None,
        dummy: bool = False,
        draw_bonds: bool = True,
    ) -> None:
        """Create a new Molecule object.

        :param atomic_numbers:np.ndarray: atomic numbers of the atoms
        :param coordinates:np.ndarray: coordinates of the molecule
        :param header:str: header from the imported file
        :param dummy: bool: a dummy object.
        :param draw_bonds: bool: draw bonds between atoms (Default is True)
        """
        if dummy:
            self.dummy = True

        self.mos = MolecularOrbitals()
        self.subdivisions = 20
        self.gen_energy_information(header)
        self.basis_set: list = []
        self.voxel_grid = VoxelGrid3D()


        # Container for all pda data:
        # The dict should be filled as follows:
        # dict = {
        #    'ref_phi': float, reference value of phi
        #    'sample_size': int, number of total structures that have been clustered
        #    'initialized': bool, True if the data has been initialized
        #    'clusters': [, list of cluster data
        #       {
        #             'sample_size': int, number of equivalent structures that have been clustered
        #             'min_phi: float, minimum value of phi
        #             'max_phi: float, maximum value of phi
        #             'spin_correlations': np.ndarray, spin correlations of the electrons (size n_ele x n_ele)
        #             'subclusters': [
        #                {
        #                    'min_phi: float, minimum value of phi
        #                    'max_phi: float, maximum value of phi
        #                    'sample_size': int, number of equivalent structures that have been clustered
        #                    'electron_positions': np.ndarray, cartesian coordinates of the electrons
        #                    'electrons_spin': np.ndarray, spin of the electrons (-1 for down, 1 for up)
        #                    'pda_eigenvectors': np.ndarray, eigenvectors of the electrons
        #                    'pda_eigenvalues': np.ndarray, eigenvalues of the electrons
        #                }
        #             ]
        #          }
        #       }
        #    ]

        self.pda_data: dict = {
            "sample_size": 0,
            "initialized": False,
            "clusters": [],
        }

        super().__init__(atomic_numbers, coordinates, draw_bonds)

    def update_basis_set(self) -> None:
        """Update the basis set positions after the atoms have been updated."""
        self.basis_set = []
        for atom in self.atoms:
            if not hasattr(atom, "basis_set") or atom.basis_set is None:
                continue
            for basis_function in atom.basis_set.basis_functions.values():
                if basis_function is not None:
                    self.basis_set.append(basis_function)

    def center_coordinates(self: Molecule) -> None:
        """Centers the structure around the center of mass."""
        self.center_of_mass = self.calculate_center_of_mass()
        self.geometric_center = np.mean(self.coords, axis=0)
        for _i, atom in enumerate(self.atoms):
            position = atom.position - self.center_of_mass
            atom.set_position(position)

        self.drawer.set_spheres(self.atoms)
        if self.draw_bonds:
            self.drawer.update_bonds()

        if self.pda_data['initialized']:
            for cluster in self.pda_data['clusters']:
                for subcluster in cluster['subclusters']:
                    subcluster['electron_positions'] -= self.center_of_mass
        self.coords -= self.center_of_mass

        self.center_of_mass = self.calculate_center_of_mass()
        self.geometric_center = np.mean(self.coords, axis=0)
        self.update_basis_set()

    def gen_energy_information(self, string: str | None) -> None:
        """Read the energy from the second line.

        :param string: file header from which energy info is extracted
        """
        self.energy = 0.0

        if isinstance(string, str):
            split_string = string.split()

            if "energy:" in split_string:
                index_e = split_string.index("energy:")

                if index_e + 1 < len(split_string):
                    self.energy = float(
                        string.split()[split_string.index("energy:") + 1],
                    )
