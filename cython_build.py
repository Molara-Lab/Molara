"""This file is used to compile the cython modules.

It needs to be called manually with python3 cython_build.py build_ext --inplace.
"""
from __future__ import annotations

import numpy as np
from Cython.Build import cythonize
from setuptools import setup

# Modules to be compiled and include_dirs when necessary
extensions = [
    "src/molara/Rendering/cylinder.pyx",
    "src/molara/Rendering/sphere.pyx",
    "src/molara/Rendering/matrices.pyx",
    "src/molara/Tools/mathtools.pyx",
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