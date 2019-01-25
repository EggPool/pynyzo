"""
Helper Class and functions
"""

import logging
import struct


def base_app_log(app_log=None):
    """Returns the best possible log handler if none is provided"""
    if app_log:
        return app_log
    elif logging.getLogger("tornado.application"):
        return logging.getLogger("tornado.application")
    else:
        return logging


def strings_to_buffer(lines: list) -> bytes:
    result = b''
    result += struct.pack("B", len(lines))  # byte
    for line in lines:
        bin = line.encode('utf-8')
        result += struct.pack("h", len(bin))  # short
        result += bin
    return result


def buffer_to_strings(b: bytearray) -> list:
    number_of_lines = struct.unpack("B", b[:1])[0]
    result = list()
    pos = 1
    for i in range(number_of_lines):
        line_len = struct.unpack("h", b[pos:pos + 2])[0]
        result.append(b[pos+2:pos+2+line_len].decode('utf-8'))
        pos += line_len
    return result
