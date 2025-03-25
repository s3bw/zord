from setuptools import setup, find_packages

setup(
    name="zord",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "Pillow>=9.0.0",
        "numpy>=1.20.0",
        "click>=8.0.0",
        "watchdog>=2.1.0",
    ],
    entry_points={
        "console_scripts": [
            "zord=zord.cli:cli",
        ],
    },
    author="Your Name",
    description="A Python library for creating animated GIFs from scene descriptions",
    python_requires=">=3.7",
) 