#!/usr/bin/env python

from distutils.core import setup

setup(
    name='latex2sympy',
    version='0.1.3',
    description='latex2sympy parses LaTeX math expressions and converts it into the equivalent SymPy form',
    author='augustt198',
    author_email='aug@mit.edu',
    packages=['latex2sympy', 'latex2sympy.gen'],
    install_requires=[
        'sympy==0.7.6',
        'antlr4-python2-runtime==4.7.1',
    ],
)
