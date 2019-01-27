

from pynyzo.messageobject import MessageObject
from pynyzo.fieldbytesize import FieldByteSize
import json
import struct


class BalanceListItem(MessageObject):
    """BalanceList message"""

    __slots__ = ('_block_height', '_rollover_fees', '_previous_verifiers', '_items')

    """
    def __init__(self, block_height: int=0, rollover_fees: int=0, previous_verifiers: list=None, items: list=None,
                 buffer: bytes=None, app_log=None):
        # This replaces the various constructors from java, depending on the params
        super().__init__(app_log=app_log)
        if buffer:
            # buffer is the full buffer with timestamp and type, why the 10 offset.
            offset = 10
            self._block_height = struct.unpack(">Q", buffer[offset:offset + 8])[0]  # long, 8
            offset += 8
            self._rollover_fees = struct.unpack(">B", buffer[offset:offset + 1])[0]  # byte
            offset += 1
            number_of_previous_verifiers = min(block_height, 9)
            self._previous_verifiers = []
            for i in range(number_of_previous_verifiers):
                # We could use a memoryview if perf /ram was an issue
                self._previous_verifiers.append(buffer[offset:offset + FieldByteSize.identifier])
                offset += FieldByteSize.identifier
            number_of_pairs = struct.unpack(">I", buffer[offset:offset + 4])[0]  # int, 4
            offset += 8
            self._items = []
            for i in range(number_of_pairs):
                identifier = buffer[offset:offset + FieldByteSize.identifier]
                offset += FieldByteSize.identifier
                balance = struct.unpack(">Q", buffer[offset:offset + 8])[0]  # long, 8
                offset += 8
                blocks_until_fee = struct.unpack(">B", buffer[offset:offset + 1])[0]  # byte
                offset += 1
                self._items.append(BalanceListItem(identifier, balance, blocks_until_fee))
        else:
            self._block_height = block_height
            self._rollover_fees = rollover_fees
            self._previous_verifiers = previous_verifiers
            self._items = items

    def get_block_height(self) -> int:
        return self._block_height

    def get_rollover_fees(self) -> int:
        return self._rollover_fees

    def get_previous_verifiers(self) -> list:
        return self._previous_verifiers.copy()  # shallow copy is enough for that type.

    def get_items(self) -> list:
        return self._items

    """



