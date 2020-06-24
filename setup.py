from glob import glob
from os.path import splitext, basename

from setuptools import setup, find_packages

setup(
    name="alma_rest",
    version="0.0.1",
    packages=find_packages(where="src"),
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    package_dir={"": "src"},
    install_requires=[
        'sqlalchemy~=1.3.0',
        'requests~=2.24.0',
    ],
)
