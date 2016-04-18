#!/usr/bin/env python3
"""Module setup.py."""

from distutils.core import setup

setup(
    name='menu-app',
    version='0.1',
    description='Application for listing lunch restaurant menus',
    author='Tero Paloheimo',
    author_email='tero@nullspace.eu',
    url='https://github.com/terop/menu-app',
    license='MIT',
    packages=['menu', 'test'],
)
