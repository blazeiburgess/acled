from setuptools import setup, find_packages

setup(
    name="acled",
    version="0.1.4",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "requests==2.32.3",
    ],
    author="Your Name",
    author_email="blaze.i.burgess@gmail.com",
    description="A Python library for interacting with ACLED data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/blazeiburgess/acled",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL 3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)