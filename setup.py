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
        "typer==0.6.1",
        "setuptools==65.0.0",
        "requests==2.28.1",
        "slack-sdk==3.18.1",
        "shellingham==1.5.0",
        "wheel==0.37.1",
    ],
    extras_require={
        "dev": [
            "pytest==7.1.2",
            "black==22.6.0",
            "pylint==2.14.5",
            "flake8==5.0.4",
            "mypy==0.971",
            "types-requests==2.28.8",
        ]
    },
)
