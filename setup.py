# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.md')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='in-game-messages',
    version='0.1.0',
    description='Send planets.nu in-game messages to Slack',
    python_requires='==3.*,>=3.8.0',
    author='Juha Tiensyrjä',
    author_email='juha.tiensyrja@gmail.com',
    entry_points={"console_scripts": ["in-game-messages = in_game_messages.cli:main"]},
    packages=['in_game_messages'],
    package_dir={"": "."},
    package_data={},
    install_requires=['click==7.*,>=7.1.2', 'setuptools==51.*,>=51.0.0', 'requests==2.25.*,>=2.25.0', 'slack-sdk==3.1.*,>=3.1.0'],
    extras_require={"dev": ['pytest==6.*,>=6.1.2', 'black==20.*,>=20.8b1']},
)
