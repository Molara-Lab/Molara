
[![CI Status](https://github.com/Thursday-Evening-Hackathon/Molara/actions/workflows/test.yml/badge.svg)](https://github.com/Thursday-Evening-Hackathon/Molara/actions/workflows/test.yml)
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
