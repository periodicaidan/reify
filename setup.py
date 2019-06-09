from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md"), "r") as h:
    readme = h.read()

setup(
    name="reify",
    version="0.2.0-beta",
    description="The Reify Template Compiler",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/periodicaidan/reify",
    author="Aidan T. Manning",
    author_email="periodicaidan@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["Click"],
    entry_points="""
        [console_scripts]
        reify=reify.cli:reify
    """
)
