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

import io
import os
import pathlib
from ac3es.exceptions import CliException
from ac3es.cli.helpers import prompt_file_exists, md5_for_file
from ac3es.ulz import UlzReader, UlzWriter


def decompress_file(ulz_path, dest_filename=None, create_parents=True, create_ulz_data=False, keep=False,
                    ulz_data_name='ulz_data'):
    """
    Decompress the files from command like using UlzReader
    """

    file_path = pathlib.Path(ulz_path)

    try:
        with file_path.open('rb') as ulz_file:
            ulz_stream = io.BytesIO(ulz_file.read())
    except IOError as err:
        raise CliException("Error reading the file {0}: {1}".format(ulz_path, err))

    ulz_reader = UlzReader(ulz_stream)
    data = ulz_reader.decompress()

    if dest_filename:
        file_path = pathlib.Path(dest_filename)

    data_type = '.bin'

    if data[0:4] == b'\x10\x00\x00\x00':
        data_type = '.tim'

    if create_ulz_data:
        file_path = pathlib.Path(file_path.parent, ulz_data_name, file_path.stem)

    file_path = file_path.with_suffix(data_type)

    if create_parents or create_ulz_data:
        file_path.parent.mkdir(0o644, True, True)

    if keep:
        prompt_file_exists(str(file_path.resolve()))

    with file_path.open('wb') as out_file:
        out_file.write(data)


def compress_file(input_file, output_file, ulz_type, level=None, store_only=False, create_parents=True, like_file=None,
                  keep=False):
    """
    Compress the files using the classes UlzWriter
    """

    level2nbits = {
        1: 10,
        2: 11,
        4: 12,
        8: 13
    }

    input_file = pathlib.Path(input_file)

    nbits = level2nbits.get(level, None)
    if nbits is None:
        raise CliException('Select the correct compression level')

    if like_file:
        try:
            like_file = pathlib.Path(like_file)
            with like_file.open('rb') as ulz_file:
                ulz_stream = io.BytesIO(ulz_file.read())

                print('creating ulz like', like_file)

                ulz_reader = UlzReader(ulz_stream)
                ulz_reader.decompress()

                ulz_type = ulz_reader.u_type
                nbits = ulz_reader.nbits
                store_only = ulz_reader.count_compressed == 0

        except IOError as err:
            raise CliException("Error reading the file {0}: {1}".format(like_file, err))

    if not output_file:
        output_file = input_file.with_suffix('.ulz')
    else:
        output_file = pathlib.Path(output_file)

    if keep:
        prompt_file_exists(output_file.resolve())

    if create_parents:
        output_file.mkdir(0o644, True, True)

    ulz_writer = UlzWriter(
        input_file.resolve(),
        ulz_type,
        nbits,
        store_only
    )

    ulz_writer.pack_file()
    ulz_writer.save(str(output_file.resolve()))


def get_ulz_info(ulz_path):
    try:
        with open(ulz_path, 'rb') as ulz_file:
            ulz_stream = io.BytesIO(ulz_file.read())
            ulz = UlzReader(ulz_stream)
            ulz.decompress()

            levels = {
                10: 1,
                11: 2,
                12: 4,
                13: 8
            }

            stats = (
                ('File', ulz_path),
                ('ulz type', ulz.u_type),
                ('compr. level', levels.get(ulz.nbits, 'ERROR')),
                ('nbits', ulz.nbits),
                ('longest jump', ulz.longest_jump),
                ('longest run', ulz.longest_run),
                ('ulz file size', os.path.getsize(ulz_path)),
                ('decompressed file size', ulz.uncompressed_size),
                ('hash md5', md5_for_file(ulz_path))
            )

            for key, value in stats:
                print(key, value, sep='\t')
            print()
    except IOError as err:
        print("Error reading the file {0}: {1}".format(ulz_path, err))
        exit()
