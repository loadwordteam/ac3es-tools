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
import struct
from ac3es.exceptions import BinDetectException
from ac3es.bpb.types import BPBChunk

class BpbController:
    def __init__(self, bpb=None, bph=None):
        self.bpb = pathlib.Path(bpb)
        self.bph = pathlib.Path(bph)

    def pack_all(self, root_dir):
        chunks = []
        for entry in sorted(root_dir.iterdir()):
            if entry.name.startswith('.'):
                continue

            if entry.is_dir():
                piece = self.pack_all(entry)
                chunks.append(
                    piece.header + b''.join(piece.offsets) + b''.join(piece.chunks)
                )
            else:
                with entry.open('rb') as f:
                    chunks.append(f.read())

        header = struct.pack('<I', len(chunks))
        start_offset = 4 + len(chunks) * 4
        offsets = []
        current_offset = 0
        for entry in chunks:
            offsets.append(
                struct.pack('<I', start_offset + current_offset)
            )
            current_offset += len(entry)

        return BPBChunk(header, offsets, chunks)

    def pack(self, source_path):
        directory = pathlib.Path(source_path)
        if not directory.is_dir():
            raise Exception('{} is not a directory'.format(source_path))

        with self.bpb.open('wb') as bpb, self.bph.open('wb') as bph:
            bph.write(b'AC3E\x03\x00\x00\x00\x27\x04\x00\x00\x84\x14\x00\x00')
            pieces = self.pack_all(directory)
            bph.write(struct.pack('<I', len(pieces.chunks)))
            for chunk in pieces.chunks:
                bph.write(struct.pack('<I', len(chunk) >> 2 | 0xE0000000))
                bph.write(struct.pack('<I', int(bpb.tell() / 0x800)))

                bpb.write(chunk)
                if len(chunk) % 0x800 > 0:
                    bpb.write(b'\x00' * (0x800 - (len(chunk) % 0x800)))

    def unpack_all(self, dest_dir, bpb, start_offset, size, level=' '):

        bpb.seek(start_offset)
        num_entries = int.from_bytes(bpb.read(4), byteorder='little')

        try:
            if 0 < num_entries < 512:
                offsets = []
                for i in range(num_entries):
                    offsets.append(int.from_bytes(bpb.read(4), byteorder='little'))
                is_sorted = all(offsets[i] < offsets[i + 1] for i in range(len(offsets) - 1))
                if not is_sorted:
                    raise BinDetectException('the list is not ordered ')
                if start_offset + offsets[-1] > start_offset + size:
                    raise BinDetectException('chunk too big')

                for idx, chunk_offset in enumerate(offsets):
                    chunk_size = None
                    try:
                        chunk_size = offsets[idx + 1] - chunk_offset
                    except IndexError:
                        chunk_size = size - chunk_offset

                    self.unpack_all(
                        dest_dir / pathlib.Path(str(idx).zfill(4)),
                        bpb,
                        chunk_offset + start_offset,
                        chunk_size
                    )

                return
        except BinDetectException:
            pass

        bpb.seek(start_offset)
        content = bpb.read(size)

        extension = '.bin'
        if content[0:4] == b'\x10\x00\x00\x00':
            extension = '.tim'
        elif content[0:4] == b'Ulz\x1A':
            extension = '.ulz'

        filename = dest_dir.with_suffix(extension)

        filename.parent.mkdir(parents=True, exist_ok=True)

        with filename.open('wb') as part:
            part.write(content)

        print("\tBPB UNPACK {} {}".format(start_offset, filename))

    def unpack(self, dest_path):
        if not self.bpb.is_file():
            raise Exception('BPB {} is not a file or is inaccessible'.format(self.bpb.resolve()))

        if not self.bph.is_file():
            raise Exception('BPH {} is not a file or is inaccessible'.format(self.bpb.resolve()))

        dest_path = pathlib.Path(dest_path)

        with self.bpb.open('rb') as bpb, self.bph.open('rb') as bph:

            bph.read(16)
            num_entries = int.from_bytes(bph.read(4), byteorder='little')

            print(num_entries)
            for idx in range(num_entries):
                raw_entry = bph.read(8)
                size = int.from_bytes(raw_entry[:3], byteorder='little') << 2
                position = int.from_bytes(raw_entry[4:], byteorder='little') * 0x800
                print("CHUNK {}".format(position))
                current_entry = dest_path / pathlib.Path(str(idx).zfill(4))
                self.unpack_all(current_entry, bpb, position, size, '')
