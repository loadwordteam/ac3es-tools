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


from ac3es import command_parser
from ac3es import InfoFile
from ac3es import compress_file, decompress_file


if __name__ == '__main__':
    parser = command_parser()
    args = parser.parse_args()

    if args.command == 'ulz':
        if args.decompress:
            decompress_file(
                args.decompress,
                args.output_file,
                args.parents,
                False,
                args.keep
            )
        elif args.compress:
            compress_file(
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
    else:
        parser.print_help()
