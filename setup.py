import os

from setuptools import setup, find_packages


setup(
  name="bib",
  version=os.environ.get("BIB_VERSION", "1.0.9999"),
  packages=find_packages(),
  package_data={"": "*.in"},
  license="Internal",
  long_description=open("README.md").read(),
  install_requires=[],
  entry_points={
    "console_scripts": ["bib=bib.cli:cli"],
  }
)
