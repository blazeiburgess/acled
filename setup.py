from setuptools import setup, find_packages

setup(
    name="acled",
    version="0.1.7",
    description="A Python library that unofficially wraps the ACLED API.",
    author="Blaze Burgess",
    author_email="blaze.i.burgess@gmail.com",
    url="https://github.com/blazeiburgess/acled",
    packages=find_packages(include=["acled", "acled.*"]),
    install_requires=[
        "requests>=2.26.0",
    ],
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)
