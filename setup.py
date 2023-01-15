#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="minecraft-python-utils",
    version="1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bds-nanny = bds_utils.nanny:run_server',
            'bds-console = bds_utils.console:run_console'
        ]
    }
)