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
from ac3es.exceptions import CliException
from ac3es.bpb import BpbController


def unpack(bpb, bph, dest_dir):
    if not os.path.isfile(bpb):
        raise CliException('Cannot access to {} for BPB'.format(bpb))

    if not os.path.isfile(bph):
        raise CliException('Cannot access to {} for BPH'.format(bph))

    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    controller = BpbController(bpb, bph)
    controller.unpack(dest_dir)


def pack(bpb, bph, source_dir):
    if not os.path.isdir(source_dir):
        raise CliException('Cannot access to {} as source'.format(source_dir))

    controller = BpbController(bpb, bph)
    controller.pack(source_dir)
