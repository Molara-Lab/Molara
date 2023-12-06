"""Does the setup for the Cython files."""
from __future__ import annotations

import numpy as np
from Cython.Build import cythonize
from setuptools import setup

# This is the function that is executed
setup(
    name="Molara",  # Required
    # A list of compiler Directives is available at
    # https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives
    # external to be compiled
    ext_modules=cythonize(
        [
            "src/molara/Rendering/cylinder.pyx",
            "src/molara/Rendering/sphere.pyx",
            "src/molara/Tools/mathtools.pyx",
        ],
    ),
    include_dirs=[np.get_include()],
)
