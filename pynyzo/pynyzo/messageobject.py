"""
Transcripted from https://github.com/n-y-z-o/nyzoVerifier/blob/master/src/main/java/co/nyzo/verifier/MessageObject.java
"""

from abc import ABC, abstractmethod


class MessageObject(ABC):

    __slot__ = ('_bytes', )

    def __init__(self, payload: bytes):
        self._bytes = payload

    # @abstractmethod
    def get_byte_size(self) -> int:
        # return len(self._bytes)
        pass

    # @abstractmethod
    def get_bytes(self) -> bytes:
        #return self._bytes
        pass
