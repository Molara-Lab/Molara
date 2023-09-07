from setuptools import setup

setup(
    name='Molara',
    version='',
    packages=[''],
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
