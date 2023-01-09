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
        "typer==0.7.0",
        "setuptools==65.6.3",
        "requests==2.28.1",
        "slack-sdk==3.19.5",
        "shellingham==1.5.0",
        "wheel==0.38.4",
    ],
    extras_require={
        "dev": [
            "pytest==7.2.0",
            "black==22.12.0",
            "pylint==2.15.8",
            "flake8==6.0.0",
            "mypy==0.991",
            "types-requests==2.28.11.2",
        ]
    },
)
