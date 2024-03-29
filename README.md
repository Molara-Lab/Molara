[![CI Status](https://github.com/Molara-Lab/Molara/actions/workflows/test.yml/badge.svg)](https://github.com/Molara-Lab/Molara/actions/workflows/test.yml)
[![code coverage](https://img.shields.io/codecov/c/gh/Molara-Lab/Molara)](https://codecov.io/gh/Molara-Lab/Molara)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Molara-Lab/Molara/main.svg)](https://results.pre-commit.ci/latest/github/Molara-Lab/Molara/main)
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

To generate the documentation you need to install molara like this:

```
pip install -e . molara[doc]

```

then run


```
cd docs
make html

```
