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
import io
import os.path
import sys
import pathlib
import ac3es
import struct
from ac3es.exceptions import CliException, NotTimException

VERSION = '2.3'


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
        raise CliException('Select the correct compression level')

    if like_file:
        try:
            with open(like_file, 'rb') as ulz_file:
                ulz_stream = io.BytesIO(ulz_file.read())
        except IOError as err:
            raise CliException("Error reading the file {0}: {1}".format(ulz_file, err))

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
        os.makedirs(
            os.path.dirname(output_file),
            mode=0o644,
            exist_ok=True
        )

    ulz_writer = ac3es.UlzWriter(
        input_file,
        ulz_type,
        nbits,
        store_only
    )

    ulz_writer.pack_file()
    ulz_writer.save(output_file)

def bin_file_split(bin_path, list_path=None, outdir_path=None):
    if not os.path.exists(bin_path):
        raise CliException("File {} does not exists",format(bin_path))

    if not outdir_path:
        outdir_path = bin_path + '_bin_splitter'

    if not list_path:
        list_path = str(pathlib.Path(outdir_path).joinpath('bin_splitter_list.txt'))

    if not pathlib.Path(outdir_path).exists():
        os.mkdir(outdir_path)

    with open(bin_path, 'rb') as bin_stream:
        bs = ac3es.BinSplitter()
        bs.split(bin_stream, outdir_path, list_path)


def bin_file_merge(source_list, dest_path, verbose=False):
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
            print(dest_path+':', entry)

    bs = ac3es.BinSplitter()
    bs.merge_all(content_list, dest_path)


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
        raise CliException("Error reading the file {0}: {1}".format(ulz_file, err))

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
        exist_ok=True
        os.makedirs(
            dest_final_directory,
            mode=0o644,
            exist_ok=True
        )

    final_path = os.path.join(dest_final_directory, decompressed_filename)

    if keep:
        prompt_file_exists(final_path)

    with open(final_path, 'wb') as out_file:
        out_file.write(data)


def copy_tim_data(source_path,
                  dest_path,
                  replace_clut=False,
                  replace_vram=False,
                  vram_x=None,
                  vram_y=None):

    if pathlib.Path(source_path).resolve() == pathlib.Path(dest_path).resolve():
        raise CliException('cannot operate on the same file')

    try:
        with open(source_path, 'rb') as source_stream, open(dest_path, 'rb+') as dest_stream:
            source_tim = ac3es.Tim(source_stream)
            dest_tim = ac3es.Tim(dest_stream)
            
            if replace_clut:
                if source_tim.bpp not in (4, 8):
                    raise CliException('Source is {}bpp, clut data is only for 4bpp or 8bpp'.format(source_tim.bpp))

                if dest_tim.bpp not in (4, 8):
                    raise CliException('Destination is {}bpp, clut data is only for 4bpp or 8bpp'.format(dest_tim.bpp))

                if dest_tim.bpp != source_tim.bpp:
                    raise CliException('BBP must to be the same, source {}bpp, destination {}bpp'.format(source_tim.bpp, dest_tim.bpp))

                source_stream.seek(source_tim.offsets['clut_header_start'], 0)
                clut = source_stream.read(
                    source_tim.offsets['clut_header_end'] - source_tim.offsets['clut_header_start']
                )
                dest_stream.seek(dest_tim.offsets['clut_header_start'], 0)
                dest_stream.write(clut)

            if replace_vram:
                dest_stream.seek(dest_tim.offsets['vram_x'], 0)
                dest_stream.write(struct.pack('<H', source_tim.vram_x))
                dest_stream.seek(dest_tim.offsets['vram_y'], 0)
                dest_stream.write(struct.pack('<H', source_tim.vram_y))

            if vram_x is not None:
                if vram_x < 0 or vram_x > 255:
                    raise CliException('vram-x out of range (0-255)')

                dest_stream.seek(dest_tim.offsets['vram_x'], 0)
                dest_stream.write(struct.pack('<H', vram_x))

            if vram_y is not None:
                if vram_y < 0 or vram_y > 255:
                    raise CliException('vram-y out of range (0-255)')

                dest_stream.seek(dest_tim.offsets['vram_y'], 0)
                dest_stream.write(struct.pack('<H', vram_y))
    except NotTimException as e:
        raise CliException(str(e))


def unpack_bpb(bpb, bph, dest_dir):
    if not os.path.isfile(bpb):
        raise CliException('Cannot access to {} for BPB'.format(bpb))

    if not os.path.isfile(bph):
        raise CliException('Cannot access to {} for BPH'.format(bph))

    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    BpbManager = ac3es.Bpb(bpb, bph)
    BpbManager.unpack(dest_dir)


def pack_bpb(bpb, bph, source_dir):
    if not os.path.isdir(source_dir):
         raise CliException('Cannot access to {} as source'.format(source_dir))

    BpbManager = ac3es.Bpb(bpb, bph)
    BpbManager.pack(source_dir)


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

Work on bin containers
  {0} bin --split=BPB/0114/0007.bin --out-directory=splitted/0007 --out-list=splitted/0007.txt
  {0} bin --merge=splitted/0007.txt --out-bin=mod_0007.bin

More parameters are available, just type help for the sub command
  {0} ulz --help
  {0} info --help
  {0} bin --help

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

    # BPB

    parser_bpb = subparsers.add_parser(
        'bpb',
        help='Unpack and repack ACE.BPB and ACE.BPH'
    )

    parser_bpb_main = parser_bpb.add_mutually_exclusive_group()
    parser_bpb_main.add_argument(
        '--unpack',
        '-u',
        metavar=('DIRECTORY'),
        help='Unpack ACE.BPB/BPH to the given directory'
    )

    parser_bpb_main.add_argument(
        '--pack',
        '-p',
        metavar=('DIRECTORY'),
        help='Pack ACE.BPB and create ACE.BPH from a given directory'
    )

    parser_bpb.add_argument(
        '--bpb',
        metavar=('ACE.BPB'),
        help='Path for ACE.BPB'
    )

    parser_bpb.add_argument(
        '--bph',
        metavar=('ACE.BPH'),
        help='Path for ACE.BPH'
    )

    parser_bpb.set_defaults(bpb='ACE.BPB', bph='ACE.BPH')

    # INFO

    parser_info = subparsers.add_parser('info', help='Check files')
    parser_info.add_argument(
        'FILES',
        help="One or more file to get info",
        nargs="+"
    )

    parser_bin = subparsers.add_parser(
        'bin',
        help='Split and merge bin container files'
    )
    sub_bin_splitter = parser_bin.add_mutually_exclusive_group()

    sub_bin_splitter.add_argument(
        '--split',
        '-s',
        metavar=('BIN_FILE'),
        help='Split a bin container'
    )

    bin_splitter = parser_bin.add_argument_group('bin split')
    bin_splitter.add_argument(
        '--out-directory',
        '-d',
        metavar=('DIRECTORY'),
        help='Output directory where to store the bin\'s components'
    )

    bin_splitter.add_argument(
        '--out-list',
        '-f',
        metavar=('DIRECTORY'),
        help='Save a components\' list to a txt'
    )

    sub_bin_splitter.add_argument(
        '--merge',
        '-m',
        metavar=('FILE_LIST|DIR'),
        help='Reconstruct a bin file starting from a component list or a directory'
    )

    bin_splitter.add_argument(
        '--out-bin',
        '-b',
        metavar=('FILE_BIN'),
        help='Output bin filename'
    )

    bin_splitter.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Print more information while merges'
    )

    tim_parser = subparsers.add_parser(
        'tim',
        help='Edit TIM header information and/or replace CLUT data'
    )

    tim_parser.add_argument(
        '--source-tim',
        '-s',
        required=True,
        metavar=('TIM_FILE'),
        help='Source TIM'
    )

    tim_parser.add_argument(
        '--copy-clut',
        action='store_true',
        help='Copy CLUT data from source'
    )

    tim_parser.add_argument(
        '--copy-vram',
        action='store_true',
        help='Copy V-RAM coordinates'
    )

    tim_parser.add_argument(
        '--set-vram-x',
        type=int,
        metavar=('X'),
        help='Set V-RAM coordinate X'
    )

    tim_parser.add_argument(
        '--set-vram-y',
        type=int,
        metavar=('Y'),
        help='Set V-RAM coordinate Y'
    )

    tim_parser.add_argument(
        'FILES',
        help="Apply the changes to one or more TIM files",
        nargs="+"
    )

    return parser
