import pathlib
from setuptools import setup, find_packages

_HERE = pathlib.Path(__file__).parent   # directoy of setup.py

setup(
    name='Molara',
    version='0.0.1',
    package_dir={"": "src"},
    packages=find_packages(
        # install only the molara package and subpackes, not unit tests,
        # examples, ...
        include=('molara', 'molara.*')
    ),
    url='',
    license='GPL v3',
    author='Michel Heinz, Gereon Feldmann',
    author_email='',
    description='',
    install_requires=[
        'PySide6',
        'numpy',
        'pyrr',
        'scipy',
        'PyOpenGL'
    ],
    # optional dependencies:
    extras_require = {
        'reading_qm_output': ['cclib'],
    },
   entry_points={
        'console_scripts': [
            'molara=molara.__main__:main'
        ]
    } 
)
