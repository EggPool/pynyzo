

from pynyzo.messageobject import MessageObject
from pynyzo.helpers import base_app_log
from pynyzo.messagetype import MessageType
from pynyzo.fieldbytesize import FieldByteSize
from pynyzo.balancelist import BalanceList
from pynyzo.block import Block
import json
import struct


class BlockResponse(MessageObject):
    """BlockResponse message"""

    __slots__ = ('_initial_balance_list', '_blocks')

    def __init__(self, start_height: int=0, end_height: int=0, include_balance_list: bool=False,
                 buffer: bytes = None, app_log=None):
        """This replaces the various constructors from java, depending on the params"""
        super().__init__(app_log=app_log)
        if buffer:
            # buffer is the full buffer with timestamp and type, why the 10 offset.
            self._initial_balance_list = None
            offset = 10
            has_balance = struct.unpack("?", buffer[offset:offset +1])[0]
            offset += 1
            if has_balance:
                self._initial_balance_list = BalanceList(buffer=memoryview(buffer)[offset:])
                offset += self._initial_balance_list.get_byte_size()
                # self.app_log.error("TODO: BlockResponse initialBalanceList")
            self._blocks = []

            number_of_blocks = struct.unpack(">H", buffer[offset:offset +2])[0]  # short = 2 bytes
            offset += 2
            print("number_of_blocks", number_of_blocks)
            mv = memoryview(buffer)
            for i in range(number_of_blocks):
                block = Block(buffer=mv[offset:])
                offset += block.get_byte_size(include_signature=True)
                self._blocks.append(block)
        else:
            # This is for the node to fill TODO
            self._initialBalanceList = None
            self._blocks = []

    def get_initial_balance_list(self):
        return self._initial_balance_list

    def get_blocks(self) -> list:
        return self._blocks

    def get_byte_size(self) -> int:
        byteSize = FieldByteSize.booleanField  # boolean value indicating whether a balance list is included
        if self._initialBalanceList:
            byteSize += self._initial_balance_list.getByteSize()

        byteSize += FieldByteSize.frozenBlockListLength
        for block in self._blocks:
            byteSize += block.get_byte_size()
        return byteSize

    def get_bytes(self) -> bytes:
        result = b''
        self.app_log.error("TODO: BlockResponse.get_bytes")
        """
        result += struct.pack(">Q", self._start_height)  # 8
        result += struct.pack(">Q", self._end_height)  # 8
        if self._include_balance_list:
            result += b'\x01'
        else:
            result += b'\x00'
        """
        return result

    def to_string(self) -> str:
        balance = True if self._initial_balance_list else False
        return f"[BlockResponse(balance={balance}, blocks={len(self._blocks)})]"

    def to_json(self) -> str:
        balance = True if self._initial_balance_list else False
        if balance:
            balance_list = json.loads(self._initial_balance_list.to_json())
        else:
            balance_list = None
        blocks = [json.loads(block.to_json()) for block in self._blocks]
        return json.dumps({"message_type": MessageType.BlockResponse12.name, 'value': {
            'balance': balance, 'blocks': blocks,
            'initial_balance_list': balance_list}})

    def print(self):
        """Create the status message and print it"""
        app_log = base_app_log()
        app_log.info(self.to_string())

