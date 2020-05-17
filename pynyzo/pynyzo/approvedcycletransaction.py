

from pynyzo.messageobject import MessageObject
from pynyzo.fieldbytesize import FieldByteSize
import json
import struct


class ApprovedCycleTransaction(MessageObject):
    """Transaction message"""


    __slots__ = ('_initiator_identifier', '_receiver_indentifier', '_approval_height', '_amount')

    def __init__(self, buffer: bytes=None, initiator_identifier: bytes=None, receiver_identifier: bytes=None, approval_height: int=0, amount: int=0, app_log=None):
        super().__init__(app_log=app_log)
        if buffer is None:
            self._approval_height = approval_height
            self._amount = amount
            self._receiver_identifier = receiver_identifier
            self._initiator_identifier = initiator_identifier
        else:
            # fromByteBuffer constructor
            # These are the fields contained in all transactions.
            offset = 0
            self._initiator_identifier = buffer[offset:offset + FieldByteSize.identifier]
            offset += FieldByteSize.identifier
            
            self._receiver_identifier = buffer[offset:offset + FieldByteSize.identifier]
            offset += FieldByteSize.identifier
            
            self._approval_height = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8
            
            self._amount = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8
            

    def get_amount(self):
        return self._amount

    def get_approval_height(self):
        return self._approval_height

    def get_receiver_identifier(self):
        return self._receiver_identifier

    def get_initiator_identifier(self):
        return self._initiator_identifier


    def get_byte_size(self):
        return FieldByteSize.identifier * 2 + FieldByteSize.blockHeight + FieldByteSize.transactionAmount

    def get_bytes(self, for_signing: bool=False):
        # TODO
        self.app_log.error('TODO: Transaction.get_bytes')

    def to_json(self) -> str:
        return json.dumps({"message_type": "Transaction", 'value': {'amount': self._amount, 'receiver_identifier': self._receiver_identifier.hex(), 'initiator_identifier': self._initiator_identifier.hex(), "approval_height": self._approval_height}})

