"""This module contains the Crystal class, which is a subclass of Structure."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy import constants

from molara.Structure.atom import elements

from .structure import Structure

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Annotated

    from numpy.typing import ArrayLike

__copyright__ = "Copyright 2024, Molara"

ONE, TWO, THREE = 1, 2, 3


class Crystal(Structure):
    """Creates a crystal supercell based on given particle positions in unit cell and lattice basis vectors.

    Particle positions are given in terms of the basis vectors:
    E.g. the position (0.5, 0.5, 0.) is always the center of a unit cell wall, regardless of the crystal system.

    :param atomic_numbers: contains the atomic numbers of the particles specified for the unit cell.
    :param coordinates: Nx3 matrix of particle (fractional) coordinates in the unit cell,
        i.e., coordinates in terms of the basis vectors.
    :param basis_vectors: 3x3 matrix of the lattice basis vectors.
    :param supercell_dims: side lengths of the supercell in terms of the cell constants
    """

    def __init__(
        self,
        atomic_nums: Sequence[int],
        coords: Sequence[Sequence[float]],
        basis_vectors: Sequence[Sequence[float]] | ArrayLike,
        supercell_dims: Annotated[Sequence[int], 3],
    ) -> None:
        """Creates a crystal supercell based on given particle positions in unit cell and lattice basis vectors."""
        self.atomic_nums_unitcell = atomic_nums
        self.coords_unitcell = self._fold_coords_into_unitcell(coords)
        self.basis_vectors = basis_vectors
        # if supercell_dims is None:
        #     supercell_dims = [1, 1, 1]
        #     SupercellDialog.get_supercell_dims(supercell_dims)
        self.make_supercell(supercell_dims)
        self.molar_mass = np.sum([elements[i]["atomic_weight"] for i in self.atomic_nums_unitcell])
        self.volume_unitcell = float(np.linalg.det(np.array(self.basis_vectors)))
        self.density_unitcell = float((self.molar_mass / constants.Avogadro) / self.volume_unitcell * 1e24)

    def _fold_coords_into_unitcell(
        self,
        fractional_coords: ArrayLike,
    ) -> list[list[float]]:
        """Folds coordinates into unit cell."""
        return np.mod(fractional_coords, 1.0).tolist()

    def make_supercell(self, supercell_dims: Annotated[Sequence[int], 3]) -> None:
        """Creates a supercell of the crystal."""
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
            self.atomic_nums_supercell.tolist(),
            self.fractional_coords_supercell.tolist(),
            supercell_dims,
        )
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

    @classmethod
    def make_supercell_edge_atoms(
        cls: type[Crystal],
        atomic_nums: Sequence[float],
        fractional_coords: Sequence[Sequence[float]],
        supercell_dims: Sequence[int],
    ) -> tuple[Sequence[int], Sequence[Sequence[float]]]:
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
        extra_fractional_coords = []  # fractional coordinates of the newly created atoms

        # iterate over the relevant atoms
        for _id_atom_unique in np.unique(ids_edge_atoms):
            _atomic_num = atomic_nums[_id_atom_unique]
            # get the zero-valued coord ids of the respective atom
            _ids_atom_coords = ids_edge_atom_coords[ids_edge_atoms == _id_atom_unique]
            _fractional_coords_atom = _fractional_coords_np[_id_atom_unique]

            if len(_ids_atom_coords) == ONE:  # e.g., (.5, 0, .5)
                extra_atomic_nums += [_atomic_num]
                extra_fractional_coords += [_fractional_coords_atom.copy()]
                id1 = _ids_atom_coords[0]
                dim1 = _supercell_dims_np[id1]
                extra_fractional_coords[-1][id1] = dim1

            elif len(_ids_atom_coords) == TWO:  # e.g., (.5, 0, 0)
                extra_atomic_nums += [_atomic_num] * 3
                id1, id2 = _ids_atom_coords
                dim1, dim2 = _supercell_dims_np[_ids_atom_coords]
                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id1] = dim1  # (dim1,0)

                extra_fractional_coords += [extra_fractional_coords[-1].copy()]
                extra_fractional_coords[-1][id2] = dim2  # (dim1,dim2)

                extra_fractional_coords += [_fractional_coords_atom.copy()]
                extra_fractional_coords[-1][id2] = dim2  # (0,dim2)

            elif len(_ids_atom_coords) == THREE:  # i.e., (0, 0, 0)
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
                raise (ValueError)
        return extra_atomic_nums, extra_fractional_coords

    def copy(self) -> Crystal:
        """Returns a copy of the Crystal object."""
        return Crystal(
            self.atomic_nums_unitcell,
            self.coords_unitcell,
            self.basis_vectors,
            self.supercell_dims,
        )

    """ overloading operators """

    def __mul__(self, supercell_dims: Sequence[int]) -> Crystal:
        """Multiply Crystal by a sequence.

        Current implementation: multiply Crystal by a sequence of three integers [M, N, K]
        to create MxNxK supercell
        """
        crystal_copy = self.copy()
        crystal_copy.make_supercell(supercell_dims)
        return crystal_copy

    def __rmul__(self, supercell_dims: Sequence[int]) -> Crystal:
        """Multiply Crystal by a sequence."""
        return self.__mul__(supercell_dims)