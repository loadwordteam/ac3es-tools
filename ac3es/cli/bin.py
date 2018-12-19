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


import os
import pathlib

from ac3es.exceptions import CliException
from ac3es.bin import BinController


def split(bin_path, list_path=None, output_path=None):
    if not os.path.exists(bin_path):
        raise CliException("File {} does not exists", format(bin_path))

    if not output_path:
        output_path = bin_path + '_bin_splitter'

    if not list_path:
        list_path = str(pathlib.Path(output_path).joinpath('bin_splitter_list.txt'))

    if not pathlib.Path(output_path).exists():
        os.mkdir(output_path)

    with open(bin_path, 'rb') as bin_stream:
        bs = BinController()
        bs.split(bin_stream, output_path, list_path)


def merge(source_list, dest_path, verbose=False):
    content_list = []
    if os.path.isfile(source_list):
        with open(source_list) as f:
            content_list = f.readlines()
        content_list = [x.strip() for x in content_list]
    elif os.path.isdir(source_list):
        p = pathlib.Path(source_list)
        content_list = [x for x in p.iterdir() if x.is_file()]
        content_list.sort()
    else:
        raise CliException('I need a valid file list or a directory')

    for entry in content_list:
        if str(entry).find('bin_splitter_list.txt') >= 0:
            content_list.remove(entry)

    if verbose:
        for entry in content_list:
            print(dest_path + ':', entry)

    bs = BinController()
    bs.merge_all(content_list, dest_path)
