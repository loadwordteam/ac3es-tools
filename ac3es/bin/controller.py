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
import struct
import pathlib

from ac3es.exceptions import CliException


class BinController:

    def __init__(self):
        self.stream = None
        self.entries = None
        self.file_names = None
        self.file_size = None
        self.num_entries = None

    def split(self, stream, dest_path, list_path):
        self.stream = stream
        self.entries = []
        self.file_names = []
        self.stream.seek(0, 2)
        self.file_size = self.stream.tell()
        self.stream.seek(0)

        self.stream.seek(0)
        self.num_entries = int.from_bytes(
            self.stream.read(4),
            byteorder='little'
        )
        self.read_index()
        self.extract_all(dest_path, list_path)

    def read_index(self):
        for i in range(self.num_entries):
            self.entries.append({
                'number': i,
                'offset': int.from_bytes(
                    self.stream.read(4),
                    byteorder='little'
                )
            })

    def extract_all(self, dest_directory_path, list_path=None):
        dest_path = pathlib.Path(dest_directory_path)
        for idx, entry in enumerate(self.entries):
            try:
                size = self.entries[idx+1]['offset'] - entry['offset']
            except IndexError:
                size = self.file_size - entry['offset']

            self.stream.seek(entry['offset'])
            content = self.stream.read(size)
            extension = '.dat'
            if content[0:4] == b'\x10\x00\x00\x00':
                extension = '.tim'
            elif content[0:4] == b'Ulz\x1A':
                extension = '.ulz'

            dest_filename = str(entry['number']).zfill(len(str(self.num_entries))) + extension
            out_file_path = str(dest_path.joinpath(dest_filename))

            self.file_names.append(out_file_path)

            with open(out_file_path, 'wb') as dest_file:
                dest_file.write(content)

        if list_path:
            with open(list_path, 'w', newline='\n') as list_txt:
                for line in self.file_names:
                    list_txt.write(line+"\n")

    def merge_all(self, content_list, dest_path):
        chunks = []

        for filename in content_list:
            if os.sep == '/' and filename.find('\\') >= 0:
                real_path = str(pathlib.Path(pathlib.PureWindowsPath(filename)).resolve())
            else:
                real_path = str(pathlib.Path(filename).resolve())

            if not os.path.isfile(real_path):
                raise CliException('file {} does not exists'.format(real_path))
            with open(real_path, 'rb') as entry_file:
                entry = entry_file.read()
                entry = entry + b'\x00' * (len(entry) % 4)
                chunks.append(entry)

        header = struct.pack('<I', len(chunks))
        start_offset = 4 + len(chunks)*4
        offsets = []
        current_offset = 0
        for entry in chunks:
            offsets.append(
                struct.pack('<I', start_offset + current_offset)
            )
            current_offset += len(entry)

        data = header + b''.join(offsets) + b''.join(chunks)

        with open(dest_path, 'wb') as outfile:
            outfile.write(data)
