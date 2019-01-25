
from pynyzo.messageobject import MessageObject
from pynyzo.helpers import strings_to_buffer, buffer_to_strings


class StatusResponse(MessageObject):
    """"""

    __slots__ = ('_lines', )

    def __init__(self, lines: list=None, requesterIdentifier: bytes=None, buffer: bytes=None):
        self._lines = list() if list is None else lines
        if buffer:
            # decode from bin buffer
            self._lines = buffer_to_strings(bytearray(buffer))

    def get_lines(self) -> list:
        return self._lines

    def get_byte_size(self) -> int:
        byte_size = 1  # list size
        for line in self._lines:
            byte_size += 2 + len(line.encode('utf-8'))
        return byte_size

    # @abstractmethod
    def get_bytes(self) -> bytes:
        return strings_to_buffer(self._lines)

