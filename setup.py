from setuptools import setup, find_packages

setup(
    name="viafoundry_sdk",
    version="1.0.8",
    description="A Python SDK and CLI for interacting with Via Foundry's API.",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(include=["viafoundry", "viafoundry.*"]),
    package_data={"viafoundry": ["bin/*.py"]},  # Include all .py files in `bin/`
    install_requires=[
        "click",
        "requests",
        "python-dotenv",
        "os",
	"io",
    ],
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
