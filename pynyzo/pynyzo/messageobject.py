"""
Mostly transcripted from
https://github.com/n-y-z-o/nyzoVerifier/blob/master/src/main/java/co/nyzo/verifier/MessageObject.java
"""

from abc import ABC, abstractmethod
from pynyzo.helpers import base_app_log
import json


class MessageObject(ABC):

    __slots__ = ('app_log', )

    def __init__(self, app_log: object=None):
        self.app_log = base_app_log(app_log)

    @abstractmethod
    def get_byte_size(self) -> int:
        pass

    @abstractmethod
    def get_bytes(self) -> bytes:
        pass

    def to_json(self) -> str:
        return json.dumps({"Error": "Not implemented"})


class EmptyMessageObject(MessageObject):
    """This one was added for convenience and avoid extra tests, not present in the java impl."""

    def get_byte_size(self) -> int:
        return 0

    def get_bytes(self) -> bytes:
        return b''
