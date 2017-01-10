# -*- coding: utf-8 -*-


def b2uint(number):
    """Simple function for convert the bytes in little edian to
    integer"""

    return int.from_bytes(number, byteorder='little', signed=False)
