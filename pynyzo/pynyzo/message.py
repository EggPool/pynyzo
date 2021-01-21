"""
Message ancestor class for Nyzo messages
"""

import struct
from abc import ABC, abstractmethod
from pynyzo.helpers import base_app_log
from pynyzo.messagetype import MessageType
from pynyzo.messageobject import MessageObject, EmptyMessageObject
from pynyzo.fieldbytesize import FieldByteSize
from pynyzo.keyutil import KeyUtil
from pynyzo.byteutil import ByteUtil
import pynyzo.config as config
from pynyzo.messages.statusresponse import StatusResponse
from pynyzo.messages.blockresponse import BlockResponse

from time import time

__version__ = '0.0.1'


class Message(ABC):
    """Abstract Ancestor for all messages."""

    # slots for private vars, to spare ram
    __slots__ = ('_applog', '_timestamp', '_type', '_content', '_sourceNodeIdentifier', '_sourceNodeSignature',
                 '_valid', '_source_ip_address')

    # Static class variables
    maximumMessageLength = 4194304  # 4MB
    whitelist = dict()
    disallowedNonCycleTypes = (MessageType.NewBlock9, MessageType.BlockVote19, MessageType.NewVerifierVote21,
                               MessageType.MissingBlockVoteRequest23, MessageType.MissingBlockRequest25)

    # We do not broadcast any messages to the full mesh from the broadcast method. We do, however, use the full mesh
    # as a potential pool for random requests for the following types. This reduces strain on in-cycle verifiers.
    fullMeshMessageTypes = (MessageType.BlockRequest11, MessageType.BlockWithVotesRequest37)

    def __init__(self, a_type: MessageType, content: MessageObject, app_log:object=None,
                 sourceNodeIdentifier: bytes=None, sourceNodeSignature: bytes=None, source_ip_address: bytes=None,
                 timestamp: int=0):
        """This is the constructor for a new message originating from this system AND from the outside,
        depending on the params."""
        self.app_log = base_app_log(app_log)
        self._type = a_type
        self._content = content
        self._valid = True

        if sourceNodeIdentifier is None:
            # From our system
            self._timestamp = int(time()*1000)
            self._sourceNodeIdentifier = config.PUBLIC_KEY.to_bytes()
            self._sourceNodeSignature = KeyUtil.sign_bytes(self.get_bytes_for_signing(), config.PRIVATE_KEY)
            # As a test, we can verify our sig before sending
            """
            KeyUtil.signature_is_valid(self._sourceNodeSignature, self.get_bytes_for_signing(), 
                                       config.PUBLIC_KEY.to_bytes())
            """
        else:
            # From another system
            self._timestamp = timestamp
            self._sourceNodeIdentifier = sourceNodeIdentifier
            self._sourceNodeSignature = sourceNodeSignature
            self._sourceIpAddress = source_ip_address
            # self._valid = KeyUtil.signature_is_valid(sourceNodeSignature, self.get_bytes_for_signing(),
            # sourceNodeIdentifier)
            self.valid = True
            # TODO: needs all the chain of get_bytes to validate; let suppose for now it is valid.
            if config.VERBOSE:
                self.app_log.warning(f"TODO: Did NOT validate message from "
                                     f"{ByteUtil.bytes_as_string_with_dashes(sourceNodeIdentifier)} "
                                     f"of type {self._type.name}")
            if not self._valid:
                self.app_log.warning(f"message from {ByteUtil.bytes_as_string_with_dashes(sourceNodeIdentifier)} "
                                     f"of type {self._type.name} is not valid")  # Temp log

    def to_string(self) -> str:
        """String view of the message for log/print"""
        return f"[Message: {self._type.name} ({self.get_content()})]"

    def get_timestamp(self) -> int:
        return self._timestamp

    def get_type(self) -> MessageType:
        return self._type

    def get_content(self) -> MessageObject:
        return self._content

    def get_source_node_identifier(self) -> bytes:
        return self._sourceNodeIdentifier

    def get_source_node_signature(self) -> bytes:
        return self._sourceNodeSignature

    def is_valid(self) -> bool:
        return self._valid

    def get_source_ip_address(self) -> bytes:
        return self._sourceIpAddress

    def sign(self, private_seed: bytes) -> None:
        # TODO
        # self.app_log.error("TODO: Message.sign()")
        self._sourceNodeIdentifier = KeyUtil.private_to_public(private_seed.hex())
        self._sourceNodeSignature = KeyUtil.signBytes(self.get_bytes_for_signing(), private_seed)

    def get_bytes_for_transmission(self) -> bytes:
        """"""
        # Determine the size (timestamp, type, source-node identifier, source-node signature, content if present).
        size_bytes = FieldByteSize.messageLength + FieldByteSize.timestamp + FieldByteSize.messageType \
                     + FieldByteSize.identifier + FieldByteSize.signature
        size_bytes += self._content.get_byte_size()

        # Make the buffer.
        buffer = b''
        # Header is low level, added when sending
        # buffer += struct.pack('I', size_bytes)  # 4 bytes

        # Add the data.
        buffer += struct.pack('>Q', self._timestamp)   # unsigned long long, 8 bytes
        self.app_log.debug(f"get bytes for message {self._type.name}, {self._type.value}")
        buffer += struct.pack('>h', self._type.value)  # 2 bytes
        buffer += self._content.get_bytes()  # no need for test, see EmptyMessageObject
        buffer += self._sourceNodeIdentifier
        buffer += self._sourceNodeSignature
        self.app_log.debug(f"buffer ({len(buffer)}): {buffer.hex()}")
        return buffer

    def get_bytes_for_signing(self) -> bytes:
        """"""
        # Determine the size (timestamp, type, source-node identifier, content if present).
        size_bytes = FieldByteSize.timestamp + FieldByteSize.messageType + FieldByteSize.identifier
        size_bytes += self._content.get_byte_size()

        # Make the buffer.
        buffer = b''
        # Header is low level, added when sending
        # buffer += struct.pack('I', size_bytes)  # 4 bytes

        # Add the data.
        buffer += struct.pack('>Q', self._timestamp)   # unsigned long long, 8 bytes
        self.app_log.debug(f"get bytes for signing {self._type.name}, {self._type.value}")
        buffer += struct.pack('>h', self._type.value)  # 2 bytes
        buffer += self._content.get_bytes()  # no need for test, see EmptyMessageObject
        buffer += self._sourceNodeIdentifier
        self.app_log.debug(f"buffer to sign ({len(buffer)}): {buffer.hex()}")
        return buffer

    @staticmethod
    def from_bytes(buffer: bytes, source_ip_address: bytes) -> any:
        message = None
        message_type = None

        timestamp = struct.unpack('>Q', buffer[:8])[0]
        typeValue = struct.unpack('>h', buffer[8:10])[0]
        message_type = MessageType(typeValue)

        content = Message.process_content(message_type, buffer)

        # size = len(buffer)
        sourceNodeIdentifier = buffer[-64-32:-64]
        sourceNodeSignature = buffer[-64:]  # sig is last 64 bytes

        # print("id", sourceNodeIdentifier.hex(), "sig", sourceNodeSignature.hex() )

        message = Message(timestamp=timestamp, a_type=message_type, content=content,
                          sourceNodeIdentifier=sourceNodeIdentifier, sourceNodeSignature=sourceNodeSignature,
                          source_ip_address=source_ip_address)
        return message

    @staticmethod
    def process_content(message_type: MessageType, buffer: bytes) -> MessageObject:
        content = EmptyMessageObject()
        if message_type == MessageType.StatusResponse18:
            content = StatusResponse(buffer=buffer)
        if message_type == MessageType.BlockResponse12:
            content = BlockResponse(buffer=buffer)
        return content
