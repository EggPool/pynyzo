

from pynyzo.messageobject import MessageObject
from pynyzo.helpers import base_app_log
from pynyzo.balancelistitem import BalanceListItem
from pynyzo.fieldbytesize import FieldByteSize
from pynyzo.hashutil import HashUtil
import json
import struct
import sys


class BalanceList(MessageObject):
    """BalanceList message"""

    __slots__ = ('_block_height', '_rollover_fees', '_previous_verifiers', '_items')

    def __init__(self, block_height: int=0, rollover_fees: int=0, previous_verifiers: list=None, items: list=None,
                 buffer: bytes=None, app_log=None):
        # This replaces the various constructors from java, depending on the params
        super().__init__(app_log=app_log)
        if buffer:
            # buffer is the full buffer with timestamp and type, why the 10 offset.
            offset = 0
            self._block_height = struct.unpack(">Q", buffer[offset:offset + 8])[0]  # long, 8
            offset += 8
            self._rollover_fees = struct.unpack(">B", buffer[offset:offset + 1])[0]  # byte
            offset += 1
            number_of_previous_verifiers = min(self._block_height, 9)
            self.app_log.debug(f"BalanceList({self._block_height}, {self._rollover_fees}, {number_of_previous_verifiers})")
            self._previous_verifiers = []
            for i in range(number_of_previous_verifiers):
                # We could use a memoryview if perf /ram was an issue
                self._previous_verifiers.append(buffer[offset:offset + FieldByteSize.identifier])
                offset += FieldByteSize.identifier
            number_of_pairs = struct.unpack(">I", buffer[offset:offset + 4])[0]  # int, 4
            offset += 4
            # print("number_of_pairs", number_of_pairs)
            self._items = []
            for i in range(number_of_pairs):
                identifier = buffer[offset:offset + FieldByteSize.identifier]
                offset += FieldByteSize.identifier
                balance = struct.unpack(">Q", buffer[offset:offset + 8])[0]  # long, 8
                offset += 8
                blocks_until_fee = struct.unpack(">H", buffer[offset:offset + 2])[0]  # Short, 2 bytes
                offset += 2
                item = BalanceListItem(identifier, balance, blocks_until_fee)
                # print(item.to_json())
                self._items.append(item)
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

    def get_byte_size(self) -> int:
        number_of_previous_verifiers = min(self._block_height, 9)
        bytes_per_item = FieldByteSize.identifier + FieldByteSize.transactionAmount + FieldByteSize.blocksUntilFee

        return FieldByteSize.blockHeight + FieldByteSize.rolloverTransactionFees \
               + FieldByteSize.identifier * number_of_previous_verifiers + FieldByteSize.balanceListLength \
               + bytes_per_item * len(self._items)

    def get_bytes(self) -> bytes:
        result = []
        result.append(struct.pack(">Q", self._block_height))  # Long
        result.append(struct.pack(">B", self._rollover_fees))  # byte
        for verifier in self._previous_verifiers:
            result.append(verifier)
        result.append(struct.pack(">I", len(self._items)))  # int, 4
        for item in self._items:
            result.append(item.get_identifier())
            result.append(struct.pack(">Q", item.get_balance()))  # Long
            result.append(struct.pack(">H", item.get_blocks_until_fee()))  # short
        return b''.join(result)

    def get_hash(self) -> bytes:
        return HashUtil.double_sha256(self.get_bytes())

    def to_string(self) -> str:
        return f"[BalanceList: height={self._block_height}, count={len(self._items)} hash={self.get_hash().hex()}]"

    def to_json(self) -> str:
        # Do not add explicit keys for balance items, too verbose.
        items = {item.get_identifier().hex(): [item.get_balance(), item.get_blocks_until_fee()] for item in self._items}
        previous_verifiers = [verifier.hex() for verifier in self._previous_verifiers]
        return json.dumps({"message_type": "BalanceList", 'value': {
            'height': self._block_height, 'rollover_fees': self._rollover_fees,
            'previous_verifiers': previous_verifiers, "items": items}})




