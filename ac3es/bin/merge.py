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

import pathlib
import typing
import os
import struct

from ac3es.exceptions import CliException


def merge_files(source_path: pathlib.Path, dest_path: pathlib.Path, verbose=False):
    content_list = get_content_list(source_path)

    if verbose:
        for entry in content_list:
            print(dest_path.resolve(), entry)

    if dest_path is None:
        raise CliException('I need an output file')

    artefact = merge_all(content_list)
    with dest_path.open('wb') as dp:
        dp.write(artefact)


def get_content_list(source_list: pathlib.Path):
    if source_list.is_file():
        content_list = [
            pathlib.Path(x.strip()) for x in source_list.read_text().split("\n") if x.strip()
        ]
        content_list = [
            x.resolve() if x.is_absolute() else source_list.parent.joinpath(x).resolve()
            for x in content_list
        ]
    elif source_list.is_dir():
        content_list = [x.resolve() for x in source_list.iterdir() if
                        x.is_file() and str(x).find('bin_splitter_list.txt') == -1]
    else:
        raise CliException('I need a valid file list or a directory')

    return content_list


def merge_all(content_list: typing.List[pathlib.Path]) -> bytes:
    """
    Creates a bin container from a list of paths pointing to the files, returns a byte string

    :param content_list:
    :return:
    """
    chunks = []
    content_list.sort()
    for filename in content_list:
        if os.sep == '/' and str(filename).find('\\') >= 0:
            real_path = str(pathlib.Path(pathlib.PureWindowsPath(filename)).resolve())
        else:
            real_path = str(pathlib.Path(filename).resolve())

        if not os.path.isfile(real_path):
            raise CliException(f'File {real_path} does not exists')

        with open(real_path, 'rb') as entry_file:
            entry = entry_file.read()
            entry = entry + b'\x00' * (len(entry) % 4)
            chunks.append(entry)

    header = struct.pack('<I', len(chunks))
    start_offset = 4 + len(chunks) * 4
    offsets = []
    current_offset = 0
    for entry in chunks:
        offsets.append(
            struct.pack('<I', start_offset + current_offset)
        )
        current_offset += len(entry)

    return header + b''.join(offsets) + b''.join(chunks)
