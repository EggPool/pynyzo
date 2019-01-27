"""
Helper Class and functions
"""

import logging
import struct
# Using tornado.log for pretty printing. async client could follow.
import tornado.log
from os import path
from logging.handlers import RotatingFileHandler


LOG_LEVEL = 'DEBUG'


def base_app_log(app_log=None):
    """Returns the best possible log handler if none is provided"""
    if app_log:
        return app_log
    elif logging.getLogger("tornado.application"):
        return logging.getLogger("tornado.application")
    else:
        return logging


def tornado_logger():
    """Define a tornado logger"""
    app_log = logging.getLogger("tornado.application")
    app_log.setLevel(LOG_LEVEL)
    tornado.log.enable_pretty_logging()
    logfile = path.abspath("nyzo.log")
    # Rotate log after reaching 512K, keep 5 old copies.
    rotate_handler = RotatingFileHandler(logfile, "a", 512 * 1024, 5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    rotate_handler.setFormatter(formatter)
    app_log.addHandler(rotate_handler)
    return app_log


def strings_to_buffer(lines: list) -> bytes:
    """Diverges from Nyzo arch"""
    result = []
    result.append(struct.pack(">B", len(lines)))  # byte
    for line in lines:
        bin = line.encode('utf-8')
        result.append(struct.pack(">h", len(bin)))  # short
        result.append(bin)
    return b''.join(result)


def buffer_to_strings(b: memoryview) -> list:
    number_of_lines = struct.unpack(">B", b[:1])[0]
    result = list()
    pos = 1
    for i in range(number_of_lines):
        line_len = struct.unpack(">h", b[pos:pos + 2])[0]
        result.append(bytes(b[pos+2:pos+2+line_len]).decode('utf-8'))
        pos += line_len + 2
    return result
