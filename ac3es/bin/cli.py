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

from ac3es.cli import BaseCliCommand
from ac3es.bin import split_file
from ac3es.bin import merge_files


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
            split_file(
                pathlib.Path(args.split),
                pathlib.Path(args.out_directory),
                args.out_list
            )
        elif args.merge:
            merge_files(
                pathlib.Path(args.merge),
                pathlib.Path(args.out_bin),
                args.verbose
            )

