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


import os.path
import errno
import io
import ac3es.archive


def decompress_file(ulz_path):

    with open(ulz_path, 'rb') as ulz_file:
        ulz_stream = io.BytesIO(ulz_file.read())

    ulz = ac3es.archive.Ulz(ulz_stream)
    data = ulz.decompress()

    tim_signature = b'\x10\x00\x00\x00'

    dest_filename = os.path.basename(ulz_path)

    if data[0:4] == tim_signature:
        dest_filename = dest_filename.replace('ulz', 'tim')
    else:
        dest_filename = dest_filename.replace('ulz', 'bin')

    base_path = []
    if os.path.dirname(ulz_path):
        base_path.append(os.path.dirname(ulz_path))

    base_path.append('ulz_data')
    dest_dir = os.path.join(*base_path)

    try:
        os.makedirs(dest_dir)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    dest_path = os.path.join(dest_dir, dest_filename)

    with open(dest_path, 'wb') as out_file:
        out_file.write(data)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", help="A path for the archive to decompress")

    args = parser.parse_args()
    decompress_file(args.archive)
