import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mmkinetics-preis",
    version="0.0.2",
    author="António E. N. Ferreira, Pedro B. P. S. Reis",
    author_email="aeferreira@fc.ul.pt, pdreis@fc.ul.pt",
    description="Web app for the analysis of enzyme kinetics data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aeferreira/mmkinetics",
    install_requires=['numpy', 'scipy', 'matplotlib', 'flask', 'bokeh'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
