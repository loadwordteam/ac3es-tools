# -*- coding: utf-8 -*-
#  This file is part of AC3ES Tools.
#
#  AC3ES Tools is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  AC3ES Tools is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with AC3ES Tools.  If not, see <http://www.gnu.org/licenses/>.


from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('COPYING') as f:
    license = f.read()

setup(
    name='ac3tools',
    version='1.1',
    description='Various tools for manipulate Ace Combat 3 game files',
    long_description=readme,
    author='Gianluigi "Infrid" Cusimano',
    author_email='infrid@infrid.com',
    url='http://ac3es.infrid.com/',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[],
)
