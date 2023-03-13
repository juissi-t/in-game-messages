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
        "py-cord==2.4.0",
        "typer==0.7.0",
        "setuptools==67.6.0",
        "requests==2.28.2",
        "slack-sdk==3.20.0",
        "shellingham==1.5.1",
        "wheel==0.38.4",
    ],
    extras_require={
        "dev": [
            "pytest==7.2.2",
            "black==23.1.0",
            "pylint==2.16.3",
            "flake8==6.0.0",
            "mypy==1.1.1",
            "types-requests==2.28.11.15",
        ]
    },
)
