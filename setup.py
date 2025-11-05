#!/usr/bin/env python3
"""Setup script for wiiBalance package."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="wiiBalance",
    version="1.0.0",
    author="wiiBalance Contributors",
    description="Python library for connecting to Nintendo Wii Balance Board via Bluetooth",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/compscirunner/wiiBalance",
    py_modules=["wii_balance_board", "example_usage"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Hardware :: Hardware Drivers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
    ],
    python_requires=">=3.6",
    install_requires=[
        "pybluez>=0.23",
    ],
    entry_points={
        "console_scripts": [
            "wiibalance=wii_balance_board:main",
        ],
    },
)
