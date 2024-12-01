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
    python_requires="==3.*,>=3.11.0",
    author="Juha Tiensyrjä",
    author_email="juha.tiensyrja@gmail.com",
    entry_points={"console_scripts": ["in-game-messages = in_game_messages.cli:app"]},
    packages=["in_game_messages"],
    package_dir={"": "."},
    package_data={},
    install_requires=[
        "audioop-lts; python_version>='3.13'",
        "py-cord==2.6.1",
        "typer==0.12.5",
        "setuptools==75.3.0",
        "requests==2.32.3",
        "slack-sdk==3.33.4",
        "shellingham==1.5.4",
        "wheel==0.44.0",
    ],
    extras_require={
        "dev": [
            "pytest==8.3.3",
            "black==24.10.0",
            "pylint==3.3.1",
            "flake8==7.1.1",
            "mypy==1.13.0",
            "types-requests==2.32.0.20241016",
        ]
    },
)
