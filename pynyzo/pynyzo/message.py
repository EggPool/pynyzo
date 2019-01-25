"""
Message ancestor class for Nyzo messages
"""

from abc import ABC, abstractmethod


__version__ = '0.0.1'


class Message(ABC):
    """Abstract Ancestor for all messages."""

    __slots__ = ('_timestamp', '_type', '_content', '_sourceNodeIdentifier', '_sourceNodeSignature', '_valid',
                 '_sourceIpAddress')

    def __init__(self):
        pass
        # Todo

    @abstractmethod
    def to_string(self) -> str:
        """String view of the message for log/print"""
        pass
