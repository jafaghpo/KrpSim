from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="krpsim",
    version="0.0.1",
    author="John Afaghpour",
    author_email="johnafaghpour@gmail.com",
    description="Program that generate a task schedule under time/resources constraints",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jafaghpo/Gomoku",
    package_dir={"": "src"},
    license=license,
    packages=find_packages("src", exclude=("tests", "docs")),
    python_requires=">=3.10.1",
    install_requires=[
        "numpy>=1.22.2",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.1",
            "black>=22.1.0",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)