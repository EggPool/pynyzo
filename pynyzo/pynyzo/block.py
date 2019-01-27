

from pynyzo.messageobject import MessageObject
from pynyzo.fieldbytesize import FieldByteSize
from pynyzo.transaction import Transaction
import json
import struct

from enum import Enum


class Block(MessageObject):
    """Block message"""

    class ContinuityState(Enum):
        Undetermined = 0
        Discontinuous = 1
        Continuous = 2

    class SignatureState(Enum):
        Undetermined = 0
        Valid = 1
        Invalid = 2

    __slots__ = ('_height', '_previous_block_hash', '_start_timestamp', '_verification_timestamp', '_transactions',
                 '_balance_list_hash', '_verifier_identifier', '_verifier_signature', '_continuity_state',
                 '_signature_state', '_cycle_information')
    """
    private long height;                           // 8 bytes; 64-bit integer block height from the Genesis block,
                                                   // which has a height of 0
    private byte[] previousBlockHash;              // 32 bytes (this is the double-SHA-256 of the previous block
                                                   // signature)
    private long startTimestamp;                   // 8 bytes; 64-bit Unix timestamp of the start of the block, in
                                                   // milliseconds
    private long verificationTimestamp;            // 8 bytes; 64-bit Unix timestamp of when the verifier creates the
                                                   // block, in milliseconds
    private List<Transaction> transactions;        // 4 bytes for number + variable
    private byte[] balanceListHash;                // 32 bytes (this is the double-SHA-256 of the account balance list)
    private byte[] verifierIdentifier;             // 32 bytes
    private byte[] verifierSignature;              // 64 bytes

    private ContinuityState continuityState = ContinuityState.Undetermined;
    private SignatureState signatureState = SignatureState.Undetermined;
    private CycleInformation cycleInformation = null;
    """

    def __init__(self, height: int=0, previous_block_hash: bytes=None, start_timestamp: int=0, transactions:list=None,
                 balance_list_hash:bytes=None, buffer: bytes=None, offset=0, app_log=None):
        super().__init__(app_log=app_log)
        if buffer is None:
            # TODO
            pass
        else:
            # Same as original fromByteBuffer constructor
            self._height = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8
            self._previous_block_hash = buffer[offset:offset +32]
            offset += 32
            self._start_timestamp = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8
            self._verification_timestamp = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8
            number_of_transactions = struct.unpack(">I", buffer[offset:offset +4])[0]  # Int, 4
            offset += 4
            self._transactions = []
            self.app_log.debug(f"Block {self._height}, {self._previous_block_hash.hex()}, {self._start_timestamp}, "
                               f"{self._verification_timestamp}, {number_of_transactions}")
            mv = memoryview(buffer)
            for i in range(number_of_transactions):
                transaction = Transaction(buffer=mv[offset:])
                added = transaction.get_byte_size()
                offset += added
                self._transactions.append(transaction)
            self._balance_list_hash = buffer[offset:offset + FieldByteSize.hash]
            offset += FieldByteSize.hash
            self._verifier_identifier = buffer[offset:offset + FieldByteSize.identifier]
            offset += FieldByteSize.identifier
            self._verifier_signature = buffer[offset:offset + FieldByteSize.signature]
            offset += FieldByteSize.signature
            # print("block offset", offset)

    def get_bytes(self, include_signature: bool=False) -> bytes:
        # TODO
        self.app_log.error('TODO: Block.get_bytes')
        """
        int size = getByteSize();

        // Assemble the buffer.
        byte[] array = new byte[size];
        ByteBuffer buffer = ByteBuffer.wrap(array);
        buffer.putLong(height);
        buffer.put(previousBlockHash);
        buffer.putLong(startTimestamp);
        buffer.putLong(verificationTimestamp);
        buffer.putInt(transactions.size());
        for (Transaction transaction : transactions) {
            buffer.put(transaction.getBytes());
        }
        buffer.put(balanceListHash);
        if (includeSignature) {
            buffer.put(verifierIdentifier);
            buffer.put(verifierSignature);
        }

        return array;
        """

    def get_byte_size(self, include_signature: bool=False) -> int:
        size = FieldByteSize.blockHeight + FieldByteSize.hash + FieldByteSize.timestamp  + FieldByteSize.timestamp \
               + 4 + FieldByteSize.hash
        for transaction in self._transactions:
            size += transaction.get_byte_size()
        if include_signature:
            size += FieldByteSize.identifier + FieldByteSize.signature
        # print("block size", size)
        return size

    def to_json(self) -> str:
        transactions = [json.loads(tx.to_json()) for tx in self._transactions]
        return json.dumps({"message_type": "Block", 'value': {
            'height': self._height, 'previous_block_hash': self._previous_block_hash.hex(),
            'start_timestamp': self._start_timestamp, 'verification_timestamp': self._verification_timestamp,
            'transactions': transactions, 'balance_list_hash': self._balance_list_hash.hex(),
            'verifier_identifier': self._verifier_identifier.hex(),
            'verifier_signature': self._verifier_signature.hex()}})
