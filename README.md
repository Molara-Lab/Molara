
[![CI Status](https://github.com/Molara-Lab/Molara/actions/workflows/test.yml/badge.svg)](https://github.com/Molara-Lab/Molara/actions/workflows/test.yml)
[![code coverage](https://img.shields.io/codecov/c/gh/Molara-Lab/Molara)](https://codecov.io/gh/Molara-Lab/Molara)
# Molara
```
git clone <this repo>
cd Molara
```
You first need to create a virtual environment and activate it in order to install molara as follows:
```
python -m venv venv
source venv/bin/activate
pip install cython numpy setuptools
python -m cython_build build_ext --inplace
pip install -e .
molara
```
