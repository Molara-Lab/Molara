[![CI Status](https://github.com/Molara-Lab/Molara/actions/workflows/test.yml/badge.svg)](https://github.com/Molara-Lab/Molara/actions/workflows/test.yml)
[![code coverage](https://img.shields.io/codecov/c/gh/Molara-Lab/Molara)](https://codecov.io/gh/Molara-Lab/Molara)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Molara-Lab/Molara/main.svg)](https://results.pre-commit.ci/latest/github/Molara-Lab/Molara/main)
# Molara
Molara is an open-source program for the 3-dimensional visualization of molecules and crystal structures. These are some of its main features:

1. Import of .xyz, .coord, and POSCAR files
2. Export of rendered structures as raster graphics
3. Tools for creating custom molecular and crystal structures
4. Animation of trajectories

New features will follow soon!

## Installation
You first need to clone the repository:
```
git clone <this repo>
cd Molara
```

It is advisable to install Molara in a virtual Python environment.

<b>Virtual environment on Linux / Mac:</b>
```
python -m venv venv
source venv/bin/activate
```
<b>Virtual environment on Windows:</b>
```
python -m venv venv
.\venv\Scripts\activate.bat
```

Subsequently, Molara may be installed as follows.
```
pip install cython numpy setuptools
python -m cython_build build_ext --inplace
pip install -e .
```
Note that, for the Cython build, a C compiler must be installed on the system (a more detailed description can be found [here](https://cython.readthedocs.io/en/latest/src/quickstart/install.html)).

After the installation, Molara may then be started (within the virtual environment) by calling `molara` from the command line.
