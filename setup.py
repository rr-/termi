#!/usr/bin/env python
from distutils.core import setup

setup(
    name='termi',
    version='0.1',
    description='Images in your terminal, using ANSI and Unicode',
    long_description=open('README.md').read(),
    author='Marcin Kurczewski',
    author_email='rr-@sakuya.pl',
    url='https://github.com/rr-/termi',
    license='MIT',
    packages=['termi'],
    scripts=['bin/termi'],
    install_requires=['pillow >= 2.6'],
)
