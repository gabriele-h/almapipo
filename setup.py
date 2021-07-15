from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="almapipo",
    version="1.0.0",
    description="Use Alma's REST APIs and store data in a Postgres DB.",
    long_description=long_description,
    long_description_content="text/markdown",
    url="https://github.com/gabriele-h/almapipo",
    packages=find_packages(where="src"),
    package_dir={'': 'src'},
    scripts=[
        'bin/db_create_tables',
        'bin/delete_hol',
        'bin/input_check',
        'bin/fetched_records_to_tsv',
        'bin/locations_export',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.5',
    install_requires=[
        "psycopg2 ~= 2.8.0; sys_platform == 'linux'",
        "psycopg2-binary ~= 2.8.0; sys_platform != 'linux'",
        "pytest ~= 5.4.3",
        "requests ~= 2.23.0",
        "sqlalchemy ~= 1.4.21",
    ],
)
