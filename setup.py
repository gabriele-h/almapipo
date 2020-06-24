from setuptools import setup, find_packages

setup(
        name="alma_rest",
        packages=find_packages(where="src"),
        package_dir={"": "src"}
)
