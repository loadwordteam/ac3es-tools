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


from ac3es.cli import command_parser
from ac3es import InfoFile
from ac3es.exceptions import CliException
import ac3es.cli

if __name__ == '__main__':
    parser = command_parser()
    args = parser.parse_args()

    try:
        if args.command == 'ulz':
            if args.decompress:
                ac3es.cli.decompress_file(
                    args.decompress,
                    args.output_file,
                    args.parents,
                    False,
                    args.keep
                )
            elif args.compress:
                ac3es.cli.compress_file(
                    args.compress,
                    args.output_file,
                    args.ulz_type,
                    args.level,
                    args.store_only,
                    args.parents,
                    args.like_file,
                    args.keep
                )

        elif args.command == 'info':
            info = InfoFile()
            for x in args.FILES:
                info.detect(x)
        elif args.command == 'bin':
            if args.split:
                ac3es.cli.bin_file_split(
                    args.split,
                    args.out_list,
                    args.out_directory
                )
            elif args.merge:
                ac3es.cli.bin_file_merge(
                    args.merge,
                    args.out_bin,
                    args.verbose
                )

        elif args.command == 'bpb':
            if args.pack is not None:
                ac3es.cli.pack_bpb(args.bpb, args.bph, args.pack)
            elif args.unpack is not None:
                ac3es.cli.unpack_bpb(args.bpb, args.bph, args.unpack)
        elif args.command == 'tim':
            for tim_file in args.FILES:
                ac3es.cli.copy_tim_data(
                    args.source_tim,
                    tim_file,
                    args.copy_clut,
                    args.copy_vram,
                    args.set_vram_x,
                    args.set_vram_y
                )

    except CliException as e:
        print(e)
        exit(-1)
    
