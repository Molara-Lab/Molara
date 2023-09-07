import pathlib
from setuptools import setup, find_packages

setup(
    name='Molara',
    version='',
    packages= find_packages(
        where=str(pathlib.Path(__file__).parent / 'src'),
        # install only the chemtrayzer package, not the unit tests
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
   entry_points={
        'console_scripts': [
            'molara=molara_main.__main__:main'
        ]
    } 
)
