"""

"""


def split_by_len(item, maxlen):
    return (item[ind:ind+maxlen] for ind in range(0, len(item), maxlen))


class ByteUtil:

    @staticmethod
    def bytes_as_string_with_dashes(buffer: bytes) -> str:
        hexa = buffer.hex()
        return '-'.join(split_by_len(hexa, 8))

    @staticmethod
    def string_to_bytes(string: str) -> bytes:
        string = string.replace('-', '')
        return bytes.fromhex(string)
