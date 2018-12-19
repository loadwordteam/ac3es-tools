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
import sys

VERSION_NUMBER = '2.3.3'


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
  {0} tim --help
  {0} bpb --help

Report bugs to: infrid@infrid.com
AC3ES Version {1}
Homepage: <http://ac3es.infrid.com/>
""".format(sys.argv[0], VERSION_NUMBER)

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
        '--copy-header',
        action='store_true',
        help='Copy the entire header data from source'
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
