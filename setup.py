from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="rei",
    version="0.0.1",
    author="indigobuffalo",
    author_email="stephen.akerson@gmail.com",
    description="A service to query REI events",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/indigobuffalo/rei",
    packages=find_packages(),
    python_requires='>=3.6',
)
