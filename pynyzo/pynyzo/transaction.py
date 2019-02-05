

from pynyzo.messageobject import MessageObject
from pynyzo.fieldbytesize import FieldByteSize
import json
import struct


class Transaction(MessageObject):
    """Transaction message"""

    nyzos_in_system = 100000000
    micronyzo_multiplier_ratio = 1000000
    micronyzos_in_system = nyzos_in_system * micronyzo_multiplier_ratio

    type_coin_generation = 0
    type_seed = 1
    type_standard = 2

    __slots__ = ('_type', '_timestamp', '_amount', '_receiver_identifier', '_previous_hash_height',
                 '_previous_block_hash', '_sender_identifier', '_sender_data', '_signature')

    """
    type;                   // 1 byte; 0=coin generation, 1=sender verification
    private long timestamp;              // 8 bytes; 64-bit Unix timestamp of the transaction initiation, in milliseconds
    private long amount;                 // 8 bytes; 64-bit amount in micronyzos
    private byte[] receiverIdentifier;   // 32 bytes (256-bit public key of the recipient)

    // Only included in type-1 and type-2 transactions
    private long previousHashHeight;     // 8 bytes; 64-bit index of the block height of the previous-block hash
    private byte[] previousBlockHash;    // 32 bytes (SHA-256 of a recent block in the chain)
    private byte[] senderIdentifier;     // 32 bytes (256-bit public key of the sender)
    private byte[] senderData;           // up to 32 bytes
    private byte[] signature; 
    """

    def __init__(self, buffer: bytes=None, type: int=0, timestamp: int=0, amount: int=0,
                 receiver_identifier: bytes=None, previous_hash_height: int=0, previous_block_hash: bytes=None,
                 sender_identifier: bytes=None, sender_data: bytes=None, signature: bytes=None, app_log=None):
        super().__init__(app_log=app_log)
        if buffer is None:
            self._type = type
            self._timestamp = timestamp
            self._amount = amount
            self._receiver_identifier = receiver_identifier
            self._previous_hash_height = previous_hash_height
            self._previous_block_hash = previous_block_hash
            self._sender_identifier = sender_identifier
            self._sender_data = sender_data
            self._signature = signature
        else:
            # fromByteBuffer constructor
            # These are the fields contained in all transactions.
            offset = 0
            self._type = struct.unpack(">B", buffer[offset:offset +1])[0]  # Byte
            offset += 1
            self._timestamp = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8
            self._amount = struct.unpack(">Q", buffer[offset:offset + 8])[0]  # Long, 8
            offset += 8
            self._receiver_identifier = buffer[offset:offset + FieldByteSize.identifier]
            offset += FieldByteSize.identifier
            self.app_log.debug(f"TX( {self._type}, {self._timestamp}, {self._amount}, "
                               f"{self._receiver_identifier.hex()}")
            if self._type == self.type_coin_generation:
                # self.app_log.error("TODO: Transaction.type_coin_generation")
                self._previous_hash_height = -1
                self._previous_block_hash = b''
                self._sender_identifier = b''
                self._sender_data = b''
                self._signature = b''
            elif self._type in [self.type_seed, self.type_standard]:
                self._previous_hash_height = struct.unpack(">Q", buffer[offset:offset + 8])[0]  # Long, 8
                offset += 8
                self._previous_block_hash = b''  # TODO: get from BlockManager
                self._sender_identifier = buffer[offset:offset + FieldByteSize.identifier]
                offset += FieldByteSize.identifier
                sender_data_length = min(32, struct.unpack(">B", buffer[offset:offset +1])[0])  # Byte
                offset += 1
                self._sender_data = buffer[offset:offset + sender_data_length]  # TODO: memoryview?
                offset += sender_data_length
                self._signature = buffer[offset:offset + FieldByteSize.signature]
                offset += FieldByteSize.signature
                self.app_log.debug(f"TX( {self._previous_hash_height}, {self._sender_identifier.hex()}, "
                                   f"{sender_data_length}, {self._signature.hex()}")
                # print("offset", offset)
            else:
                self.app_log.warning(f"Unknown Transaction type: {self._type}")

    def get_type(self):
        return self._type

    def get_timestamp(self):
        return self._timestamp

    def get_amount(self):
        return self._amount

    def get_amount_after_fee(self):
        return self._amount - self.get_fee()

    def get_receiver_identifier(self):
        return self._receiver_identifier

    def get_sender_identifier(self):
        return self._sender_identifier

    def get_sender_data(self):
        return self._sender_data

    def get_signature(self):
        return self._signature

    def get_fee(self):
        return (self.get_amount() + 399) / 400

    def get_byte_size(self, for_signing:bool=False):

        size = FieldByteSize.transactionType + FieldByteSize.timestamp + FieldByteSize.transactionAmount \
               + FieldByteSize.identifier

        if self._type in [self.type_seed, self.type_standard]:
            if for_signing:
                size += FieldByteSize.hash  # previous-block hash for signing
            else:
                size += FieldByteSize.blockHeight  # previous-hash height for storage and transmission
            size += FieldByteSize.identifier  # sender identifier
            if for_signing:
                size += FieldByteSize.hash  # sender data hash for signing
            else:
                size += 1 + len(self._sender_data) + FieldByteSize.signature  # length specifier + sender data + transaction signature
        return size

    def get_bytes(self, for_signing: bool=False):
        # TODO
        self.app_log.error('TODO: Transaction.get_bytes')

    def to_json(self) -> str:
        if self._type == self.type_coin_generation:
            return json.dumps({"message_type": "Transaction", 'value': {
                'type': self._type, 'timestamp': self._timestamp, 'amount': self._amount,
                'receiver_identifier': self._receiver_identifier.hex()}})

        return json.dumps({"message_type": "Transaction", 'value': {
            'type': self._type,'timestamp': self._timestamp, 'amount': self._amount,
            'receiver_identifier': self._receiver_identifier.hex(), 'previous_hash_height': self._previous_hash_height,
            'previous_block_hash': self._previous_block_hash.hex(), 'sender_identifier': self._sender_identifier.hex(),
            'sender_data': self._sender_data.hex(), 'signature': self._signature.hex()}})

