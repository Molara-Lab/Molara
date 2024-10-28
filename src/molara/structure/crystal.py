"""Contains the Crystal class, which is a subclass of Structure."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy import constants

from molara.structure.atom import atomic_number_to_symbol, elements

from .structure import Structure

if TYPE_CHECKING:
    from numpy.typing import ArrayLike

    try:
        from pymatgen.core import Structure as Pmgstructure
    except ImportError:
        pmgstructure = None
    try:
        from ase import Atoms
    except ImportError:
        Atoms = None

__copyright__ = "Copyright 2024, Molara"


dimension = range(1, 4)


class Crystal(Structure):
    """Class that represents a crystal supercell."""

    def __init__(
        self,
        atomic_nums: list[int],
        coords: list[list[float]],
        basis_vectors: list[list[float]] | ArrayLike,
        supercell_dims: list[int],
    ) -> None:
        """Create a crystal supercell based on given particle positions in unit cell and lattice basis vectors.

        Particle positions are given in terms of the basis vectors:
        E.g. the position (0.5, 0.5, 0.) is always the center of a unit cell wall, regardless of the crystal system.

        :param atomic_numbers: contains the atomic numbers of the particles specified for the unit cell.
        :param coordinates: Nx3 matrix of particle (fractional) coordinates in the unit cell,
            i.e., coordinates in terms of the basis vectors.
        :param basis_vectors: 3x3 matrix of the lattice basis vectors.
        :param supercell_dims: side lengths of the supercell in terms of the cell constants
        """
        self.atomic_nums_unitcell = atomic_nums
        self.elements = [atomic_number_to_symbol(i) for i in self.atomic_nums_unitcell]
        self.coords_unitcell = self._fold_coords_into_unitcell(coords)
        self.basis_vectors = basis_vectors
        self.energy = 0.0  # TD: implement energy calculation

        self.make_supercell(supercell_dims)
        self.molar_mass = np.sum([elements[i]["Atomic mass"] for i in self.elements])
        self.volume_unitcell = Crystal.calc_volume_unitcell(self.basis_vectors)
        self.density_unitcell = float((self.molar_mass / constants.Avogadro) / self.volume_unitcell * 1e24)

    def _fold_coords_into_unitcell(
        self,
        fractional_coords: ArrayLike,
    ) -> list[list[float]]:
        """Folds coordinates into unit cell.

        :param fractional_coords: particle positions in fractional coordinates
        """
        return np.mod(fractional_coords, 1.0).tolist()

    def make_supercell(self, supercell_dims: list[int]) -> None:
        """Create a supercell of the crystal.

        :param supercell_dims: side lengths of the supercell in terms of the cell constants
        """
        self.supercell_dims = supercell_dims
        steps_a = np.arange(supercell_dims[0])
        steps_b = np.arange(supercell_dims[1])
        steps_c = np.arange(supercell_dims[2])
        steps_a.shape = (*steps_a.shape, 1, 1)
        steps_b.shape = (1, *steps_b.shape, 1)
        steps_c.shape = (1, 1, *steps_c.shape)
        translations_a = 1.0 * steps_a + 0.0 * steps_b + 0.0 * steps_c
        translations_b = 0.0 * steps_a + 1.0 * steps_b + 0.0 * steps_c
        translations_c = 0.0 * steps_a + 0.0 * steps_b + 1.0 * steps_c
        translation_vectors = np.array(
            [
                translations_a.flatten(),
                translations_b.flatten(),
                translations_c.flatten(),
            ],
        ).T

        num_unit_cells = translation_vectors.shape[0]
        self.fractional_coords_supercell = np.empty((0, 3), float)
        self.atomic_nums_supercell = np.empty(0, int)

        # create supercell arrays
        for atomic_number_i, position_i in zip(
            self.atomic_nums_unitcell,
            self.coords_unitcell,
            strict=True,
        ):
            self.atomic_nums_supercell = np.append(
                self.atomic_nums_supercell,
                [atomic_number_i] * num_unit_cells,
            )
            self.fractional_coords_supercell = np.append(
                self.fractional_coords_supercell,
                position_i + translation_vectors,
                axis=0,
            )

        # create extra atoms at edges of supercell (quasi periodic boundaries)
        extra_atomic_nums, extra_fractional_coords = self.make_supercell_edge_atoms()

        if extra_atomic_nums:
            self.atomic_nums_supercell = np.append(
                self.atomic_nums_supercell,
                extra_atomic_nums,
            )
            self.fractional_coords_supercell = np.append(
                self.fractional_coords_supercell,
                extra_fractional_coords,
                axis=0,
            )

        # transform fractional to cartesian coordinates and instantiate atoms in super().__init__
        self.cartesian_coordinates_supercell = Crystal.fractional_to_cartesian_coords(
            self.fractional_coords_supercell,
            self.basis_vectors,
        )
        # ... and instantiate atoms in super().__init__
        super().__init__(
            self.atomic_nums_supercell,
            self.cartesian_coordinates_supercell,
            draw_bonds=False,
        )

    @staticmethod
    def fractional_to_cartesian_coords(
        fractional_coords: ArrayLike,
        basis_vectors: ArrayLike,
    ) -> np.ndarray:
        """Transform fractional coordinates (coordinates in terms of basis vectors) to cartesian coordinates.

        :param fractional_coords: fractional coordinates of the atoms
        :param basis_vectors: basis vectors of the crystal lattice
        """
        return np.dot(fractional_coords, basis_vectors)

    def edge_atom_coords(self) -> tuple[np.ndarray, np.ndarray]:
        """Return the coordinates of the edge atoms in the supercell."""
        _fractional_coords_np = np.array(self.fractional_coords_supercell)
        if len(_fractional_coords_np.shape) != 2:  # noqa: PLR2004
            msg = "Faulty shape of fractional_coords_np array. Shape must be (N,3)."
            raise ValueError(msg)
        edges = np.where(_fractional_coords_np == 0)
        return edges[0], edges[1]

    def calc_number_of_supercell_atoms(self, supercell_dims: list[int]) -> int:
        """Calculate the number of atoms in the supercell."""
        num_atoms_unitcell = len(self.atomic_nums_unitcell)
        ids_edge_atoms = np.where(np.array(self.coords_unitcell) == 0)[0]
        ids_edge_atoms_unique = np.unique(ids_edge_atoms)
        num_edge_atoms_unitcell = len(ids_edge_atoms_unique)

        base_value = (num_atoms_unitcell - num_edge_atoms_unitcell) * np.prod(supercell_dims, dtype=int)
        for id_edge_atom in ids_edge_atoms_unique:
            factor = 1
            coords = np.array(self.coords_unitcell[id_edge_atom])
            factor *= supercell_dims[0] + 1 if coords[0] == 0.0 else supercell_dims[0]
            factor *= supercell_dims[1] + 1 if coords[1] == 0.0 else supercell_dims[1]
            factor *= supercell_dims[2] + 1 if coords[2] == 0.0 else supercell_dims[2]
            base_value += factor
        return base_value

    def make_supercell_edge_atoms(self) -> tuple[list[int], list[list[float]]]:
        """Extra atoms are created at supercell edges (periodic boundaries).

        :param atomic_nums: atomic numbers of the atoms
        :param fractional_coords: fractional coordinates,
          i.e., the coordinates of the atoms in terms of the basis vectors.
        :param supercell_dims: supercell dimensions, e.g., [3,2,5] for a 3x2x5 supercell.
        """
        # first get 2D info on where the zero-valued atom coordinates are located.
        # ids_edge_atoms contains the 0th-axis ids, i.e., the ids of the atoms with zero-valued coords.
        # ids_edge_atom_coords contains the 1st-axis ids, i.e., the ids of the specific coords that are zero-valued.
        # example: if there are five atoms, the 0th and the 3rd of which have coordinates (0, .5, .5) and (.5, 0, 0),
        # respectively, then ids_edge_atoms would be [0, 3, 3], and ids_edge_atom_coords would be [0, 1, 2].
        _fractional_coords_np = np.array(self.fractional_coords_supercell)
        _supercell_dims_np = np.array(self.supercell_dims)
        atomic_nums = self.atomic_nums_supercell

        ids_edge_atoms, ids_edge_atom_coords = self.edge_atom_coords()
        extra_atomic_nums = []  # atomic numbers of the newly created atoms
        extra_fractional_coords = []  # fractional coordinates of the newly created atoms

        # iterate over the relevant atoms
        for _id_atom_unique in np.unique(ids_edge_atoms):
            _atomic_num = atomic_nums[_id_atom_unique]
            # get the zero-valued coord ids of the respective atom
            _ids_atom_coords = ids_edge_atom_coords[ids_edge_atoms == _id_atom_unique]
            _fractional_coords_atom = _fractional_coords_np[_id_atom_unique]

            if len(_ids_atom_coords) == dimension[0]:  # e.g., (.5, 0, .5)
                extra_atomic_nums += [_atomic_num]
                extra_fractional_coords += [_fractional_coords_atom.copy()]
                id1 = _ids_atom_coords[0]
                dim1 = _supercell_dims_np[id1]
                extra_fractional_coords[-1][id1] = dim1

            elif len(_ids_atom_coords) == dimension[1]:  # e.g., (.5, 0, 0)
                extra_atomic_nums += [_atomic_num] * 3
                id1, id2 = _ids_atom_coords
                dim1, dim2 = _supercell_dims_np[_ids_atom_coords]
                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id1] = dim1  # (dim1,0)

                extra_fractional_coords += [extra_fractional_coords[-1].copy()]
                extra_fractional_coords[-1][id2] = dim2  # (dim1,dim2)

                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id2] = dim2  # (0,dim2)

            elif len(_ids_atom_coords) == dimension[2]:  # i.e., (0, 0, 0)
                extra_atomic_nums += [_atomic_num] * 7
                id1, id2, id3 = _ids_atom_coords
                dim1, dim2, dim3 = _supercell_dims_np[_ids_atom_coords]

                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id1] = dim1  # (dim1,0,0)
                extra_fractional_coords += [extra_fractional_coords[-1].copy()]
                extra_fractional_coords[-1][id2] = dim2  # (dim1,dim2,0)
                extra_fractional_coords += [extra_fractional_coords[-1].copy()]
                extra_fractional_coords[-1][id3] = dim3  # (dim1,dim2,dim3)

                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id1] = dim1
                extra_fractional_coords[-1][id3] = dim3  # (dim1,0,dim3)

                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id2] = dim2  # (0,dim2,0)
                extra_fractional_coords += [extra_fractional_coords[-1].copy()]
                extra_fractional_coords[-1][id3] = dim3  # (0,dim2,dim3)

                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id3] = dim3  # (0,0,dim3)
            else:
                msg = "Unexpected number of zero-valued coordinates encountered."
                raise ValueError(msg)
        return extra_atomic_nums, extra_fractional_coords

    @property
    def unitcell_boundaries_positions(self) -> np.ndarray:
        """Return the positions of the unit cell box."""
        basis_vectors_matrix = np.array(self.basis_vectors)
        zero_vec = np.array([0, 0, 0])

        return (
            np.array(
                [
                    [zero_vec, basis_vectors_matrix[0]],
                    [zero_vec, basis_vectors_matrix[1]],
                    [zero_vec, basis_vectors_matrix[2]],
                    [basis_vectors_matrix[0], basis_vectors_matrix[0] + basis_vectors_matrix[1]],
                    [basis_vectors_matrix[0], basis_vectors_matrix[0] + basis_vectors_matrix[2]],
                    [basis_vectors_matrix[1], basis_vectors_matrix[1] + basis_vectors_matrix[0]],
                    [basis_vectors_matrix[1], basis_vectors_matrix[1] + basis_vectors_matrix[2]],
                    [basis_vectors_matrix[2], basis_vectors_matrix[2] + basis_vectors_matrix[1]],
                    [basis_vectors_matrix[2], basis_vectors_matrix[2] + basis_vectors_matrix[0]],
                    [
                        basis_vectors_matrix[0] + basis_vectors_matrix[1],
                        basis_vectors_matrix[0] + basis_vectors_matrix[1] + basis_vectors_matrix[2],
                    ],
                    [
                        basis_vectors_matrix[0] + basis_vectors_matrix[2],
                        basis_vectors_matrix[0] + basis_vectors_matrix[1] + basis_vectors_matrix[2],
                    ],
                    [
                        basis_vectors_matrix[1] + basis_vectors_matrix[2],
                        basis_vectors_matrix[0] + basis_vectors_matrix[1] + basis_vectors_matrix[2],
                    ],
                ],
                dtype=np.float32,
            )
            - self.coordinate_shift
        )

    @staticmethod
    def calc_volume_unitcell(basis_vectors: list[list[float]] | ArrayLike) -> float:
        """Calculate unit cell volume based on given lattice basis vectors.

        :param volume: unit cell volume to be matched
        """
        basis_vectors = np.array(basis_vectors)
        if basis_vectors.shape != (3, 3):
            msg = "Faulty shape of basis_vectors array. Shape must be (3,3)."
            raise ValueError(msg)
        # result is rounded to 12 digits because the det function tends to give results like 63.99999999999998
        return round(np.abs(np.linalg.det(basis_vectors)), 12)

    @classmethod
    def from_pymatgen(
        cls: type[Crystal],
        structure: Pmgstructure,
        supercell_dims: list[int],
    ) -> Crystal:
        """Create a Crystal object from a pymatgen.Structure object.

        :param structure: pymatgen.Structure object
        """
        return cls(list(structure.atomic_numbers), structure.frac_coords, structure.lattice.matrix, supercell_dims)

    @classmethod
    def from_ase(cls: type[Crystal], atoms: Atoms) -> Crystal:
        """Create a Crystal object from an ase.Atoms object.

        :params atoms: ase.Atoms object
        """
        assert atoms.get_pbc().all(), (
            "You are attempting to create a crystal from a non-periodic ase.Atoms object. "
            "For non-periodic systems, use Molecule.from_ase(). "
            "Partially periodic systems are not supported yet."
        )
        return cls(
            atoms.get_atomic_numbers(),
            atoms.get_scaled_positions(),
            atoms.get_cell(),
            supercell_dims=[1, 1, 1],
        )

    def copy(self) -> Crystal:
        """Return a copy of the Crystal object."""
        return Crystal(
            self.atomic_nums_unitcell,
            self.coords_unitcell,
            self.basis_vectors,
            self.supercell_dims,
        )

    """ overloading operators """

    def __mul__(self, supercell_dims: list[int]) -> Crystal:
        """Multiply Crystal by a sequence.

        Current implementation: multiply Crystal by a sequence of three integers [M, N, K]
        to create MxNxK supercell

        :param supercell_dims:  side lengths of the supercell in terms of the cell constants
        """
        crystal_copy = self.copy()
        crystal_copy.make_supercell(supercell_dims)
        return crystal_copy

    def __rmul__(self, supercell_dims: list[int]) -> Crystal:
        """Multiply Crystal by a sequence.

        :param supercell_dims:  side lengths of the supercell in terms of the cell constants
        """
        return self.__mul__(supercell_dims)
