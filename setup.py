from setuptools import setup, Extension
from Cython.Build import cythonize
from Cython.Compiler import Options
import numpy

# These are optional
# Options.docstrings = True
# Options.annotate = False

# Modules to be compiled and include_dirs when necessary
extensions = [
    # Extension(
    #     "pyctmctree.inpyranoid_c",
    #     ["src/pyctmctree/inpyranoid_c.pyx"],
    # ),
    Extension(
        "pyctmctree.domortho",
        ["src/pyctmctree/domortho.pyx"], include_dirs=[numpy.get_include()],
    ),
]


# This is the function that is executed
setup(
    name='Molara',  # Required

    # A list of compiler Directives is available at
    # https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#compiler-directives

    # external to be compiled
    ext_modules = cythonize(["src/molara/Rendering/cylinder.pyx", "src/molara/Rendering/sphere.pyx",
                             "src/molara/Tools/mathtools.pyx"]),
    include_dirs = [numpy.get_include()],
)
