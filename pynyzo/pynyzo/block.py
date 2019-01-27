

from pynyzo.messageobject import MessageObject
from pynyzo.helpers import base_app_log
from pynyzo.messagetype import MessageType
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
            self._previous_block_hash = buffer[offset:offset +32]  # struct.unpack(">IIIIIIII", buffer[offset:offset +32])  # 32 bytes, 8 int
            offset += 32
            self._start_timestamp = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8
            self._verification_timestamp = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8
            number_of_transactions = struct.unpack(">I", buffer[offset:offset +4])[0]  # Int, 4
            offset += 4
            self._transactions = []
            self.app_log.debug(f"Block {self._height}, {self._previous_block_hash.hex()}, {self._start_timestamp}, {self._verification_timestamp}, {number_of_transactions}")
            mv = memoryview(buffer)
            for i in range(number_of_transactions):
                transaction = Transaction(buffer=mv[offset:])
                offset += transaction.get_byte_size()
                self._transactions.append(transaction)

    """
        -long blockHeight = buffer.getLong();
        -byte[] previousBlockHash = new byte[FieldByteSize.hash];
        -buffer.get(previousBlockHash);
        -long startTimestamp = buffer.getLong();
        -long verificationTimestamp = buffer.getLong();
        -int numberOfTransactions = buffer.getInt();
        List<Transaction> transactions = new ArrayList<>();
        for (int i = 0; i < numberOfTransactions; i++) {
            transactions.add(Transaction.fromByteBuffer(buffer));
        }

        byte[] balanceListHash = new byte[FieldByteSize.hash];
        buffer.get(balanceListHash);
        byte[] verifierIdentifier = new byte[FieldByteSize.identifier];
        buffer.get(verifierIdentifier);
        byte[] verifierSignature = new byte[FieldByteSize.signature];
        buffer.get(verifierSignature);

        return new Block(blockHeight, previousBlockHash, startTimestamp, verificationTimestamp, transactions,
balanceListHash, verifierIdentifier, verifierSignature);
    """

    def get_bytes(self, include_signature: bool=False) -> bytes:
        pass
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
        pass
        """
        int size = FieldByteSize.blockHeight +           // height
                FieldByteSize.hash +                     // previous-block hash
                FieldByteSize.timestamp +                // start timestamp
                FieldByteSize.timestamp +                // verification timestamp
                4 +                                      // number of transactions
                FieldByteSize.hash;                      // balance-list hash
        for (Transaction transaction : transactions) {
            size += transaction.getByteSize();
        }
        if (includeSignature) {
            size += FieldByteSize.identifier + FieldByteSize.signature;
        }

        return size;
        """
