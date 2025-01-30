from setuptools import setup, find_packages

setup(
    name="viafoundry_sdk",
    version="1.0.12",
    description="A Python SDK and CLI for interacting with Via Foundry's API.",
    author="Alper Kucukural",
    author_email="alper@viascientific.com",
    packages=find_packages(include=["viafoundry", "viafoundry.*"]),
    package_data={"viafoundry": ["bin/*.py"]},  # Include all .py files in `bin/`
    entry_points={
        "console_scripts": [
            "foundry=viafoundry.bin.foundry:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
