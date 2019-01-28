

from pynyzo.messageobject import MessageObject
from pynyzo.fieldbytesize import FieldByteSize
import json
import struct


class BalanceListItem(MessageObject):
    """BalanceListItem message"""

    transfer_identifier = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000001")

    __slots__ = ('_blocks_betweenfee', '_identifier', '_balance', '_blocks_until_fee')

    def __init__(self, identifier: bytes=None, balance: int=0, blocks_until_fee: int=None, buffer: bytes = None,
                 app_log=None):
        # This replaces the various constructors from java, depending on the params
        super().__init__(app_log=app_log)
        self._blocks_betweenfee = 500
        if buffer is None:
            self._identifier = identifier
            self._balance = balance
            if blocks_until_fee == None:
                self._blocks_until_fee = 0 if identifier == self.transfer_identifier else self._blocks_betweenfee
            else:
                self._blocks_until_fee = blocks_until_fee
        else:
            pass

    def get_identifier(self) -> bytes:
        return self._identifier

    def get_balance(self) -> int:
        return self._balance

    def get_blocks_until_fee(self) -> int:
        return self._blocks_until_fee

    def get_byte_size(self) -> int:
        return FieldByteSize.identifier + 8 + 2

    def get_bytes(self) -> bytes:
        self.app_log.error("TODO: BalanceListItem.get_bytes")
        return b''

    def to_json(self) -> str:
        # I stripped one level, type and value
        return json.dumps({'identifier': self._identifier.hex(), 'balance': self._balance,
                           'blocks_until_fee': self._blocks_until_fee})

