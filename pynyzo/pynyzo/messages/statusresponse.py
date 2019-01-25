
from pynyzo.messageobject import MessageObject
from pynyzo.helpers import strings_to_buffer, buffer_to_strings
from pynyzo.helpers import base_app_log


class StatusResponse(MessageObject):
    """"""

    __slots__ = ('_lines', )

    def __init__(self, lines: list=None, requesterIdentifier: bytes=None, buffer: bytes=None, app_log=None):
        """This replaces the various constructors from java, depending on the params"""
        super().__init__(app_log=app_log)
        self._lines = list() if list is None else lines
        if buffer:
            # decode from bin buffer, same as fromByteBuffer of original code.
            self._lines = buffer_to_strings(bytearray(buffer))

    def get_lines(self) -> list:
        return self._lines

    def get_byte_size(self) -> int:
        byte_size = 1  # list size
        for line in self._lines:
            byte_size += 2 + len(line.encode('utf-8'))
        return byte_size

    def get_bytes(self) -> bytes:
        return strings_to_buffer(self._lines)

    def to_string(self) -> str:
        return f"[StatusResponse(n={len(self._lines)})]"

    @staticmethod
    def print():
        """Create the status message and print it"""
        app_log = base_app_log()
        app_log.error("TODO StatusResponse.print()")
        #response = StatusResponse(Verifier.getIdentifier())  # TODO
        response = None
        for line in response.get_lines():
            app_log.info(line)



