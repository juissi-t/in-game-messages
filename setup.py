# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

package_root = os.path.abspath(os.path.dirname(__file__))

version = {}
with open(os.path.join(package_root, "in_game_messages/version.py")) as fp:
    exec(fp.read(), version)
version = version["__version__"]

readme = ""
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "rb") as stream:
        readme = stream.read().decode("utf8")


setup(
    long_description=readme,
    name="in-game-messages",
    version=version,
    description="Send planets.nu in-game messages to Slack",
    python_requires="==3.*,>=3.7.9",
    author="Juha Tiensyrjä",
    author_email="juha.tiensyrja@gmail.com",
    entry_points={"console_scripts": ["in-game-messages = in_game_messages.cli:app"]},
    packages=["in_game_messages"],
    package_dir={"": "."},
    package_data={},
    install_requires=[
        "py-cord==2.5.0",
        "typer==0.9.0",
        "setuptools==69.2.0",
        "requests==2.31.0",
        "slack-sdk==3.27.1",
        "shellingham==1.5.4",
        "wheel==0.42.0",
    ],
    extras_require={
        "dev": [
            "pytest==8.1.1",
            "black==24.2.0",
            "pylint==3.1.0",
            "flake8==7.0.0",
            "mypy==1.9.0",
            "types-requests==2.31.0.20240311",
        ]
    },
)
