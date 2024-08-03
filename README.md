<p align="center">
<img src="img/MolaraLogo.svg" alt="inPsights Logo" height="128"/>
</p>

[![PyPI version](https://badge.fury.io/py/Molara.svg)](https://badge.fury.io/py/Molara)
[![CI Status](https://github.com/Molara-Lab/Molara/actions/workflows/test.yml/badge.svg)](https://github.com/Molara-Lab/Molara/actions/workflows/test.yml)
[![code coverage](https://img.shields.io/codecov/c/gh/Molara-Lab/Molara)](https://codecov.io/gh/Molara-Lab/Molara)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Molara-Lab/Molara/main.svg)](https://results.pre-commit.ci/latest/github/Molara-Lab/Molara/main)
[![Zenodo](https://img.shields.io/badge/DOI-10.5281/zenodo.11120926-blue?logo=Zenodo&logoColor=white)](https://zenodo.org/records/11120926)

# Molara

Molara is an open-source program for the 3-dimensional visualization of molecules and crystal structures. These are some of its main features:

1. Import of .xyz, .coord, and POSCAR files
2. Export of rendered structures as raster graphics
3. Tools for creating custom molecular and crystal structures
4. Animation of trajectories

New features will follow soon!

## Installation

You first need to clone the repository:

```bash
git clone <this repo>
cd Molara
```

It is advisable to install Molara in a virtual Python environment.

<b>Virtual environment on Linux / Mac:</b>

```bash
python -m venv venv
source venv/bin/activate
```

<b>Virtual environment on Windows:</b>

```bash
python -m venv venv
.\venv\Scripts\activate.bat
```

Subsequently, Molara may be installed as follows.

```bash
pip install -e .
```

Note that, for the Cython build, a C compiler must be installed on the system (a more detailed description can be found [here](https://cython.readthedocs.io/en/latest/src/quickstart/install.html)).

After the installation, Molara can then be started (if applicable, within the virtual environment) by calling `molara` from the command line.

## Building the documentation locally

To generate the documentation, install molara as follows:

```bash
pip install -e . molara[doc]

```

then run

```bash
cd docs
make html
```

Note that, for the Cython build, a C compiler must be installed on the system (a more detailed description can be found [here](https://cython.readthedocs.io/en/latest/src/quickstart/install.html)).

After the installation, Molara may then be started (within the virtual environment) by calling `molara` from the command line.

## Known issues

Due to Apple's non existing support for OpenGL, displaying the indices of the atoms takes long for the first time. However after that it is instantaneous, even after restarting the program and rebooting the machine. As a solution we need to rework this routine with another strategy.
