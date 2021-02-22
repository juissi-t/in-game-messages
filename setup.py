# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ""
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "rb") as stream:
        readme = stream.read().decode("utf8")


setup(
    long_description=readme,
    name="in-game-messages",
    version="0.1.0",
    description="Send planets.nu in-game messages to Slack",
    python_requires="==3.*,>=3.7.9",
    author="Juha Tiensyrjä",
    author_email="juha.tiensyrja@gmail.com",
    entry_points={"console_scripts": ["in-game-messages = in_game_messages.cli:app"]},
    packages=["in_game_messages"],
    package_dir={"": "."},
    package_data={},
    install_requires=[
        "typer==0.3.*,>=0.3.2",
        "setuptools>=53,<54",
        "requests==2.25.*,>=2.25.0",
        "slack-sdk>=3.3,<3.4",
        "shellingham>=1.4,<1.5",
        "wheel==0.36.*,>=0.36.2",
    ],
    extras_require={
        "dev": [
            "pytest==6.*,>=6.1.2",
            "black==20.*,>=20.8b1",
            "pylint>=2.6,<2.8",
            "flake8==3.8.*,>=3.8.4",
            "mypy==0.800",
        ]
    },
)
