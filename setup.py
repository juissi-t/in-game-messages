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
        "py-cord==2.7.0",
        "typer==0.21.1",
        "setuptools==80.10.2",
        "requests==2.32.5",
        "slack-sdk==3.40.1",
        "shellingham==1.5.4",
        "wheel==0.46.3",
    ],
    extras_require={
        "dev": [
            "pytest==9.0.2",
            "black==26.1.0",
            "pylint==4.0.4",
            "flake8==7.3.0",
            "mypy==1.19.1",
            "types-requests==2.32.4.20260107",
        ]
    },
)
