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

from ac3es.cli import BaseCliCommand
from ac3es.exceptions import CliException
from ac3es.bin import BinController


class CliBin(BaseCliCommand):

    def __init__(self):
        self.name = 'bin'
        self.help = 'Split and merge bin container files'

    def get_parser(self, subparsers):

        parser_bin = subparsers.add_parser(
            self.name,
            help=self.help
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

        return subparsers

    def run_cmd(self, args):
        if args.split:
            self.split(
                args.split,
                args.out_list,
                args.out_directory
            )
        elif args.merge:
            self.merge(
                args.merge,
                args.out_bin,
                args.verbose
            )

    def split(self, bin_path, list_path=None, output_path=None):
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

    def merge(self, source_list, dest_path, verbose=False):
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

        if dest_path is None:
            raise CliException('I need an output file')

        bs = BinController()
        bs.merge_all(content_list, dest_path)
