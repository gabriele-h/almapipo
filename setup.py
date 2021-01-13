from os.path import splitext, basename

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="alma_rest",
    version="0.0.1",
    description="Use Alma's REST APIs and store data in a Postgres DB.",
    long_description=long_description,
    long_description_content="text/markdown",
    url="https://github.com/gabriele-h/alma_rest",
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    scripts=[
        'bin/db_create_tables',
        'bin/input_check',
        'bin/fetched_records_to_tsv',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "psycopg2 ~= 2.8.0; sys_platform == 'linux'",
        "psycopg2-binary ~= 2.8.0; sys_platform != 'linux'",
        "pytest ~= 5.4.0",
        "requests ~= 2.23.0",
        "sqlalchemy ~= 1.3.0",
    ],
)
