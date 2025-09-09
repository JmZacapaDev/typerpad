from setuptools import setup, find_packages

setup(
    name="typerpad",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.17.4",
        "rich>=14.1.0",
        "appdirs>=1.4.4",
        "SQLAlchemy>=2.0.0"
    ],
    entry_points={
        "console_scripts": [
            "typerpad=notes_typer.cli:app",
        ],
    },
    author="JmZacapa",
    description="A simple CLI for managing quick notes with Typer",
    license="MIT",
    python_requires=">=3.8",
)

