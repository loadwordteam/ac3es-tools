# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('COPYING') as f:
    license = f.read()

setup(
    name='ac3tools',
    version='0.1b',
    description='Various tools for manipulate Ace Combat 3 game files',
    long_description=readme,
    author='Gianluigi "Infrid" Cusimano',
    author_email='infrid@infrid.com',
    url='http://ac3es.infrid.com/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['bitarray'],
)
