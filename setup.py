"""Setup file for Molara."""

from __future__ import annotations

import pathlib

from setuptools import find_packages, setup

_HERE = pathlib.Path(__file__).parent  # directory of setup.py

setup(
    name="Molara",
    version="0.0.1",
    description="",
    url="",
    author="Michel Heinz, Gereon Feldmann",
    author_email="",
    maintainer="Michel Heinz, Gereon Feldmann, Adrian Usler, Alexander Bonkowski",
    maintainer_email="",
    license="GPL v3",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["analysis, science, structure, visualisation"],
    packages=find_packages(
        # install only the molara package and subpackes, not unit tests,
        # examples, ...
        include=("molara", "molara.*"),
    ),
    package_dir={"": "src"},
    install_requires=["PySide6", "numpy", "pyrr", "scipy", "PyOpenGL"],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["molara=molara.__main__:main"]},
)
