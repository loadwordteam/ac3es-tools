import collections
import os
from ac3es.exceptions import NotTimException


class Tim:
    signature = b'\x10\x00\x00\x00'

    BPP_TYPES = {
        b'\x08\x00\x00\x00': 4,
        b'\x09\x00\x00\x00': 8,
        b'\x02\x00\x00\x00': 16,
        b'\x03\x00\x00\x00': 24,
    }

    def __init__(self, tim_stream, original_path=''):
        self.vram_x = None
        self.vram_y = None
        self.img_height = None
        self.img_width = None
        self.n_clut = None
        self.n_colors = None
        self.clut_data = None
        self.palette_x = None
        self.palette_y = None
        self.stream = tim_stream
        self.offsets = {}
        self.clut_size = None
        self.clut_colors = None

        self.original_path = original_path

        self.read_tim()

    def info(self, file_location=''):
        self.read_tim()

        bpb_location = ''
        if file_location:
            file_location = os.path.abspath(file_location)
            if file_location.find('bpb') > -1:
                ext_pos = file_location.rfind('.')
                if ext_pos == -1:
                    ext_pos = len(file_location)
                bpb_location = file_location[file_location.find('bpb')+3:ext_pos]

        return collections.OrderedDict({
            'file_location': file_location.lower(),
            'bpb_location': bpb_location,
            'filetype': 'tim',
            # 'size': os.path.getsize(path),
            'bpp': self.bpp,
            # 'md5': utils.md5_for_file(path),
            'vram_x': self.vram_x,
            'vram_y': self.vram_y,
            'img_height': self.img_height,
            'img_width': self.img_width,
            'n_clut': self.n_clut,
            'n_colors': self.n_colors,
            'palette_x': self.palette_x,
            'palette_y': self.palette_y,
        })

    def read_tim(self):
        self.stream.seek(0)
        header = self.stream.read(4)
        if header != self.signature:
            raise NotTimException(
                '{} Signature does not match {}'.format(
                    self.original_path,
                    str(header)
                )
            )

        self.bpp = self.BPP_TYPES.get(
            self.stream.read(4),
            None
        )

        if self.bpp is None:
            raise NotTimException('{} Invalid BPP {}'.format(self.original_path, str(self.bpp)))

        self.clut_size = int.from_bytes(self.stream.read(4), byteorder='little')

        if self.bpp == 4 or self.bpp == 8:
            self.offsets['clut_header_start'] = self.stream.tell()
            self.offsets['palette_x'] = self.stream.tell()
            self.palette_x = int.from_bytes(self.stream.read(2), byteorder='little')
            self.offsets['palette_y'] = self.stream.tell()
            self.palette_y = int.from_bytes(self.stream.read(2), byteorder='little')

            self.offsets['clut_colors'] = self.stream.tell()
            self.clut_colors = int.from_bytes(self.stream.read(2), byteorder='little')

            self.offsets['n_clut'] = self.stream.tell()
            self.n_clut = int.from_bytes(self.stream.read(2), byteorder='little')

            self.offsets['clut_data'] = self.stream.tell()
            
            if self.bpp == 4:
                self.n_colors = self.n_clut * 16
                self.clut_data = self.stream.read(self.n_clut*32+4)
            else:
                self.n_colors = self.n_clut * 256
                self.clut_data = self.stream.read(self.n_clut*64+4)

            self.offsets['clut_header_end'] = self.stream.tell()

            self.offsets['vram_x'] = self.stream.tell()
            self.vram_x = int.from_bytes(self.stream.read(2), byteorder='little')
            self.offsets['vram_y'] = self.stream.tell()
            self.vram_y = int.from_bytes(self.stream.read(2), byteorder='little')

            self.offsets['img_width'] = self.stream.tell()
            self.img_width = int.from_bytes(self.stream.read(2), byteorder='little')
            self.offsets['img_height'] = self.stream.tell()
            self.img_height = int.from_bytes(self.stream.read(2), byteorder='little')

            if self.bpp == 4:
                self.img_width *= 4
            else:
                self.img_width *= 2

        elif self.bpp == 16 or self.bpp == 24:

            self.offsets['vram_x'] = self.stream.tell()
            self.vram_x = int.from_bytes(self.stream.read(2), byteorder='little')
            self.offsets['vram_y'] = self.stream.tell()
            self.vram_y = int.from_bytes(self.stream.read(2), byteorder='little')

            self.offsets['img_width'] = self.stream.tell()
            self.img_width = int.from_bytes(self.stream.read(2), byteorder='little')
            self.offsets['img_height'] = self.stream.tell()
            self.img_height = int.from_bytes(self.stream.read(2), byteorder='little')

            if self.bpp == 24:
                self.img_width *= 1.5
