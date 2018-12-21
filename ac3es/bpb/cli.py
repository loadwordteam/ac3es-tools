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

from ac3es.cli import BaseCliCommand
from ac3es.exceptions import CliException
from ac3es.bpb import BpbController


class CliBpb(BaseCliCommand):
    def __init__(self):
        self.name = 'bpb'
        self.help = ''
        self.args = None

    def get_parser(selfs, subparsers):
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

        return subparsers

    def run_cmd(self, args):
        self.args = args

        if args.pack is not None:
            self.pack(args.bpb, args.bph, args.pack)
        elif args.unpack is not None:
            self.unpack(args.bpb, args.bph, args.unpack)

    def unpack(self, bpb, bph, dest_dir):
        if not os.path.isfile(bpb):
            raise CliException('Cannot access to {} for BPB'.format(bpb))

        if not os.path.isfile(bph):
            raise CliException('Cannot access to {} for BPH'.format(bph))

        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)

        controller = BpbController(bpb, bph)
        controller.unpack(dest_dir)

    def pack(self, bpb, bph, source_dir):
        if not os.path.isdir(source_dir):
            raise CliException('Cannot access to {} as source'.format(source_dir))

        controller = BpbController(bpb, bph)
        controller.pack(source_dir)
