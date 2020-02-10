import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flaskdocs",
    version="0.0.1",
    author="Joseph L Buell V",
    author_email="jlrbuellv@gmail.com",
    description=
    "A packed to help generate documentation automatically for flask endpoints.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrincredibuell/flaskdocs",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
    ],
    install_requires=[
        "Flask",
        "schema",
    ],
)