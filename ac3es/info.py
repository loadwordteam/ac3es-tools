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


import hashlib
import io
import os.path
import ac3es
from .ulz import UlzReader
from .database_md5 import DatabaseMD5
from ac3es.exceptions import NotTimException


class InfoFile():
    """
    Check the hash of files or analyze the ulz
    """
    db_md5 = DatabaseMD5()

    def md5_for_file(self, path, block_size=256*128):
        '''
        Block size directly depends on the block size of your filesystem
        to avoid performances issues
        Here I have blocks of 4096 octets (Default NTFS)
        '''
        md5 = hashlib.md5()
        try:
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(block_size), b''):
                    md5.update(chunk)
        except IOError:
            print("cannot read file {}".format(path))
            exit()

        return md5.hexdigest()

    def get_tim_info(self, tim_path):
        with open(tim_path, 'rb') as tim:
            tim_file = ac3es.Tim(tim)
            stats = tim_file.info(tim_path)
            keys = stats.keys()
            for key in sorted(keys):
                print(key, stats[key], sep='\t')

    def get_ulz_info(self, ulz_path):
        try:
            with open(ulz_path, 'rb') as ulz_file:
                ulz_stream = io.BytesIO(ulz_file.read())
        except IOError as err:
            print("Error reading the file {0}: {1}".format(ulz_file, err))
            exit()

        ulz = UlzReader(ulz_stream)
        ulz.decompress()

        levels = {
            10: 1,
            11: 2,
            12: 4,
            13: 8
        }

        stats = (
            ('File', ulz_path),
            ('ulz type', ulz.u_type),
            ('compr. level', levels.get(ulz.nbits, 'ERROR')),
            ('nbits', ulz.nbits),
            ('longest_jump', ulz.longest_jump),
            ('longest_run', ulz.longest_run),
            ('ulz filesize', os.path.getsize(ulz_path)),
            ('decompressed filesize', ulz.uncompressed_size),
            ('hash md5', self.md5_for_file(ulz_path))
        )

        for key, value in stats:
            print(key, value, sep='\t')
        print()

    def detect(self, path):
        if path[-3:] == 'ulz':
            self.get_ulz_info(path)
            exit()

        try:
            self.get_tim_info(path)
            exit()
        except NotTimException as e:
            pass
        
        hash_value = self.md5_for_file(path)
        report = self.db_md5.find(hash_value)
        if report:
            print(path, hash_value, sep='\t')
            print('-' * 64)
            for key, value in report:
                print(key, value, sep='\t')
