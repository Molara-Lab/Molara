"""File used to compile the cython modules.

It needs to be called manually with python3 cython_build.py build_ext --inplace.
"""

from __future__ import annotations

import numpy as np
from Cython.Build import cythonize
from setuptools import setup

__copyright__ = "Copyright 2024, Molara"

# Modules to be compiled and include_dirs when necessary
extensions = [
    "src/molara/rendering/cylinder.pyx",
    "src/molara/rendering/sphere.pyx",
    "src/molara/rendering/matrices.pyx",
    "src/molara/tools/mathtools.pyx",
    "src/molara/tools/raycasting.pyx",
    "src/molara/eval/aos.pyx",
    "src/molara/eval/aos.pxd",
    "src/molara/eval/mos.pyx",
    "src/molara/eval/mos.pxd",
    "src/molara/eval/generate_voxel_grid.pyx",
    "src/molara/eval/marchingcubes.pyx",
]


# This is the function that is executed
setup(
    name="Molara",  # Required
    # A list of compiler Directives is available at
    # https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives
    # external to be compiled
    ext_modules=cythonize(extensions, compiler_directives={"language_level": 3}),
    include_dirs=[np.get_include()],
)
