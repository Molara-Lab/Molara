"""This module contains the Crystal class, which is a subclass of Molecule."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import numpy as np

from .atom import element_symbol_to_atomic_number
from .molecule import *

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Annotated

    from numpy.typing import ArrayLike


class Crystal(Molecule):
    """Creates a crystal supercell based on given particle positions in unit cell and lattice basis vectors.

    Particle positions are given in terms of the basis vectors:
    E.g. the position (0.5, 0.5, 0.) is always the center of a unit cell wall, regardless of the crystal system.

    :param atomic_nums: contains the atomic numbers of the particles specified for the unit cell.
    :type atomic_nums: numpy.array of int
    :param coords: Nx3 matrix of particle coordinates in the unit cell, in terms of the basis vectors.
    :type coords: numpy.ndarray of numpy.float64
    :param basis_vectors: 3x3 matrix of the lattice basis vectors.
    :type basis_vectors: numpy.ndarray of numpy.float64
    :param supercell_dimensions: side lengths of the supercell in terms of the cell constants
    :type supercell_dimensions: numpy.array of int
    """

    def __init__(
        self,
        atomic_nums: Sequence[int],
        coords: Sequence[Sequence[float]],
        basis_vectors: Sequence[Sequence[float]] | ArrayLike,
    ) -> None:
        """Creates a crystal supercell based on given particle positions in unit cell and lattice basis vectors."""
        self.atomic_nums_unitcell = atomic_nums
        self.coords_unitcell = coords
        self.basis_vectors = basis_vectors
        self.make_supercell([3, 3, 3])

    def make_supercell(self, supercell_dimensions: Annotated[Sequence, 3]) -> None:
        """Creates a supercell of the crystal."""
        self.supercell_dimensions = supercell_dimensions
        steps_a = np.arange(supercell_dimensions[0])
        steps_b = np.arange(supercell_dimensions[1])
        steps_c = np.arange(supercell_dimensions[2])
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
        extra_atomic_nums, extra_fractional_coords = Crystal.make_supercell_edge_atoms(
            self.atomic_nums_supercell,
            self.fractional_coords_supercell,
            supercell_dimensions,
        )
        self.atomic_nums_supercell = np.append(
            self.atomic_nums_supercell, extra_atomic_nums
        )
        self.fractional_coords_supercell = np.append(
            self.fractional_coords_supercell, extra_fractional_coords, axis=0
        )

        # transform fractional to cartesian coords ...
        self.cartesian_coords_supercell = np.dot(
            self.fractional_coords_supercell,
            self.basis_vectors,
        )
        # ... and instantiate atoms in super().__init__
        super().__init__(
            self.atomic_nums_supercell,
            self.cartesian_coords_supercell,
        )

    @classmethod
    def make_supercell_edge_atoms(
        cls: type[Crystal],
        atomic_nums: Sequence[float],
        fractional_coords: Sequence[Sequence[float]],
        supercell_dims: Sequence[int],
    ) -> (Sequence[int], Sequence[Sequence[float]]):
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
        _fractional_coords_np = np.array(fractional_coords)
        _supercell_dims_np = np.array(supercell_dims)

        ids_edge_atoms, ids_edge_atom_coords = np.where(_fractional_coords_np == 0)
        extra_atomic_nums = []  # atomic numbers of the newly created atoms
        extra_fractional_coords = (
            []
        )  # fractional coordinates of the newly created atoms

        # iterate over the relevant atoms
        for _id_atom_unique in np.unique(ids_edge_atoms):
            _atomic_num = atomic_nums[_id_atom_unique]
            # get the zero-valued coord ids of the respective atom
            _ids_atom_coords = ids_edge_atom_coords[ids_edge_atoms == _id_atom_unique]
            _fractional_coords_atom = _fractional_coords_np[_id_atom_unique]

            if len(_ids_atom_coords) == 1:  # e.g., (.5, 0, .5)
                extra_atomic_nums += [_atomic_num]
                extra_fractional_coords += [_fractional_coords_atom.copy()]
                id1 = _ids_atom_coords[0]
                dim1 = _supercell_dims_np[id1]
                extra_fractional_coords[-1][id1] = dim1

            elif len(_ids_atom_coords) == 2:  # e.g., (.5, 0, 0)
                extra_atomic_nums += [_atomic_num] * 3
                id1, id2 = _ids_atom_coords
                dim1, dim2 = _supercell_dims_np[_ids_atom_coords]
                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id1] = dim1  # (dim1,0)

                extra_fractional_coords += [extra_fractional_coords[-1].copy()]
                extra_fractional_coords[-1][id2] = dim2  # (dim1,dim2)

                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id2] = dim1  # (0,dim1)

            elif len(_ids_atom_coords) == 3:  # i.e., (0, 0, 0)
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
                # reset
                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id3] = dim3  # (0,0,dim3)
            else:
                raise (ValueError)
        return extra_atomic_nums, extra_fractional_coords

    @classmethod
    def from_poscar(cls: type[Crystal], file_path: str) -> Crystal:
        """Creates a Crystal object from a POSCAR file."""
        with open(file_path) as file:
            lines = file.readlines()
        header_length = 9
        if not len(lines) >= header_length:
            msg = "Error: faulty formatting of the POSCAR file."
            raise ValueError(msg)
        scale_, latvec_a_, latvec_b_, latvec_c_ = lines[1:5]
        species_, numbers_ = lines[5].strip(), lines[6]
        mode, positions_ = lines[7].strip(), lines[8:]
        try:
            scale = float(scale_)
            latvec_a = [float(vec) for vec in latvec_a_.split()]
            latvec_b = [float(vec) for vec in latvec_b_.split()]
            latvec_c = [float(vec) for vec in latvec_c_.split()]
            species = re.split(r"\s+", species_)
            numbers = [int(num) for num in numbers_.split()]
            positions = [np.fromstring(pos, sep=" ").tolist() for pos in positions_]
            basis_vectors = [latvec_a, latvec_b, latvec_c]
        except ValueError as err:
            msg = "Error: faulty formatting of the POSCAR file."
            raise ValueError(msg) from err
        if len(numbers) != len(species) or len(positions) != sum(numbers):
            msg = "Error: faulty formatting of the POSCAR file."
            raise ValueError(msg)
        if mode.lower() != "direct":
            msg = "Currently, Molara can only process direct mode in POSCAR files."
            raise NotImplementedError(msg)
        atomic_numbers = [element_symbol_to_atomic_number(symb) for symb in species]

        atomic_numbers_extended = []
        for num, an in zip(numbers, atomic_numbers):
            atomic_numbers_extended.extend(num * [an])

        return cls(
            atomic_numbers_extended,
            positions,
            [scale * np.array(bv, dtype=float) for bv in basis_vectors],
        )

    def copy(self) -> Crystal:
        """Returns a copy of the Crystal object."""
        # supercell dimensions not included yet!
        return Crystal(
            self.atomic_nums_unitcell,
            self.coords_unitcell,
            self.basis_vectors,
        )

    """ overloading operators """

    def __mul__(self, supercell_dimensions: Sequence[int]) -> Crystal:
        """Multiply Crystal by a sequence.

        Current implementation: multiply Crystal by a sequence of three integers [M, N, K]
        to create MxNxK supercell
        """
        crystal_copy = self.copy()
        crystal_copy.make_supercell(supercell_dimensions)
        return crystal_copy

    def __rmul__(self, supercell_dimensions: Sequence[int]) -> Crystal:
        """Multiply Crystal by a sequence."""
        return self.__mul__(supercell_dimensions)
