
import io

from setuptools import find_packages
from setuptools import setup

with io.open("README.rst", "rt", encoding="utf8") as f:
    readme = f.read()

setup(
    name="example",
    version="1.0.0",
    license="",
    maintainer="",
    maintainer_email="",
    description="",
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "flask",
        "flaskdocs",
        "jinja2",
    ],
    # extras_require={"test": ["pytest", "coverage"]},
)