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


import argparse
import errno
import io
import os.path
import sys

import ac3es

VERSION = '1.0b'


def prompt_file_exists(filename):
    if os.path.isfile(filename):
        print('Overwrite the file {0}? [y/n]'.format(filename), end=' ')
        choice = None
        while choice not in ('y', 'n'):
            choice = input().lower()
            if choice == 'n' or choice == 'no':
                print('exiting...')
                exit()
            elif choice == 'y' or choice == 'yes':
                break
            else:
                print('Please respond with yes/no', end=' ')


def compress_file(input_file,
                  output_file,
                  ulz_type,
                  level=None,
                  store_only=False,
                  create_parents=True,
                  like_file=None,
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

    nbits = level2nbits.get(level, None)
    if nbits is None:
        print('Select the correct compression level')
        exit(-1)

    if like_file:
        try:
            with open(like_file, 'rb') as ulz_file:
                ulz_stream = io.BytesIO(ulz_file.read())
        except IOError as err:
            print("Error reading the file {0}: {1}".format(ulz_file, err))
            exit()

        print('creating ulz like', like_file)

        ulzd = ac3es.UlzReader(ulz_stream)
        ulzd.decompress()

        ulz_type = ulzd.u_type
        nbits = ulzd.nbits
        store_only = ulzd.count_compressed == 0

    if output_file is None:
        output_file = input_file[:-4] + '.ulz'

    if keep:
        prompt_file_exists(output_file)

    if create_parents:
        try:
            os.makedirs(
                os.path.dirname(output_file),
                mode=0o644,
                exist_ok=True
            )
        except OSError as exception:
            if exception.errno != errno.EXIST:
                raise

    ulz_writer = ac3es.UlzWriter(
        input_file,
        ulz_type,
        nbits,
        store_only
    )

    ulz_writer.pack_file()
    ulz_writer.save(output_file)


def decompress_file(ulz_path,
                    dest_filename=None,
                    create_parents=True,
                    create_ulz_data=False,
                    keep=False):
    """
    Decompress the files from command like using UlzReader
    """

    try:
        with open(ulz_path, 'rb') as ulz_file:
            ulz_stream = io.BytesIO(ulz_file.read())
    except IOError as err:
        print("Error reading the file {0}: {1}".format(ulz_file, err))
        exit()

    ulz = ac3es.UlzReader(ulz_stream)
    data = ulz.decompress()

    decompressed_filename = dest_filename or os.path.basename(ulz_path)

    if data[0:4] == b'\x10\x00\x00\x00':
        decompressed_filename = decompressed_filename[:-4] + '.tim'
    else:
        decompressed_filename = decompressed_filename[:-4] + '.dat'

    base_path = [os.path.dirname(ulz_path)]

    if create_ulz_data:
        base_path.append('ulz_data')

    dest_final_directory = os.path.join(*base_path)

    if create_parents or create_ulz_data:
        try:
            os.makedirs(dest_final_directory)
        except OSError as exception:
            if exception.errno != errno.EXIST:
                raise

    final_path = os.path.join(dest_final_directory, decompressed_filename)

    if keep:
        prompt_file_exists(final_path)

    with open(final_path, 'wb') as out_file:
        out_file.write(data)


def command_parser():
    """
    Creates the parser and the options
    """

    epilog = """Example:

Compress an image and put the output into the same directory
  {0} ulz --compress image.tim --ulz-type=2 --level=1

or define another destination
  {0} ulz --compress jap_0002.tim --ulz-type=2 --level=1 --output-file=mycompress.ulz

Get what parameters use from the original file
  {0} info BPB/0386/0001/0000.ulz

More parameters are avaible, just type help for the sub command
  {0} ulz --help
  {0} info --help

Report bugs to: infrid@infrid.com
AC3ES Version {1}
Homepage: <http://ac3es.infrid.com/>
""".format(sys.argv[0], VERSION)

    parser = argparse.ArgumentParser(
        epilog=epilog,
        formatter_class=argparse.RawTextHelpFormatter
    )

    subparsers = parser.add_subparsers(help='Commands', dest='command')

    parser_ulz = subparsers.add_parser('ulz', help='Manipulate ulz files')
    sub_ulz = parser_ulz.add_mutually_exclusive_group()

    sub_ulz.add_argument(
        '--compress',
        '-c',
        metavar=('FILE'),
        help='Compress the file in ulz'
    )

    compression = parser_ulz.add_argument_group('compression')
    compression.add_argument(
        '--ulz-type',
        choices=(0, 2),
        type=int,
        help='Define the ulz version to use'
    )

    compression.add_argument(
        '--level',
        '-l',
        choices=(1, 2, 4, 8),
        type=int,
        help='Compression levels 1/2/4/8 uses a search buffer 1024/2048/4096/8192 bytes long.'
    )

    compression.add_argument(
        '--store-only',
        '-s',
        action='store_true',
        help='Store data on ulz file, needs anyway a compression level'
    )

    compression.add_argument(
        '--like-file',
        help='Get compression parameters from file'
    )

    sub_ulz.add_argument(
        '--decompress',
        '-d',
        metavar=('ULZ'),
        help='decompress the file in the current directory'
    )

    parser_ulz.add_argument(
        '--output-file',
        '-f',
        metavar=('FILE'),
        help='override output filename'
    )

    parser_ulz.add_argument(
        '--parents',
        '-p',
        action='store_true',
        help="Create directories for destination files if they don't exists"
    )

    parser_ulz.add_argument(
        '--keep',
        '-k',
        action='store_true',
        help='prompt before every removal or destructive change'
    )

    parser_info = subparsers.add_parser('info', help='Check files')
    parser_info.add_argument(
        'FILES',
        help="One or more file to get info",
        nargs="+"
    )

    return parser
