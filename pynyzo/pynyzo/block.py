

from pynyzo.messageobject import MessageObject
from pynyzo.fieldbytesize import FieldByteSize
from pynyzo.transaction import Transaction
from pynyzo.byteutil import ByteUtil
from pynyzo.balancelist import BalanceList
from pynyzo.hashutil import HashUtil

import json
import struct
# import sys
# from bs4 import BeautifulSoup

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
                 '_signature_state', '_cycle_information', '_blockchain_version')
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

    def __init__(self, height: int=0, previous_block_hash: bytes=None, start_timestamp: int=0,
                 verification_timestamp: int=0, transactions: list=None, balance_list_hash: bytes=None,
                 verifier_identifier: bytes=None, verifier_signature: bytes=None,
                 buffer: bytes=None, offset=0, app_log=None):
        super().__init__(app_log=app_log)
        if buffer is None:
            # TODO
            self._height = height
            self._previous_block_hash = previous_block_hash
            self._start_timestamp = start_timestamp
            self._verification_timestamp = verification_timestamp
            self._transactions = transactions
            self._balance_list_hash = balance_list_hash
            self._verifier_identifier = verifier_identifier
            self._verifier_signature = verifier_signature
        else:
            # Same as original fromByteBuffer constructor
            self._height =  struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            self._blockchain_version, self._height = (0xffff000000000000 & self._height) >> (6 * 8), 0x0000ffffffffffff & self._height
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
            balance_list_cycle_transaction = True if self._blockchain_version > 1 else False
            #print("chain version", self._blockchain_version)
            for i in range(number_of_transactions):
                transaction = Transaction(buffer=mv[offset:], balance_list_cycle_transaction=balance_list_cycle_transaction)
                added = transaction.get_byte_size()
                offset += added
                self._transactions.append(transaction)
            self._balance_list_hash = buffer[offset:offset + FieldByteSize.hash]
            offset += FieldByteSize.hash
            self._verifier_identifier = buffer[offset:offset + FieldByteSize.identifier]
            offset += FieldByteSize.identifier
            self._verifier_signature = buffer[offset:offset + FieldByteSize.signature]
            offset += FieldByteSize.signature
        #exit()

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

    def get_hash(self) -> bytes:
        return HashUtil.double_sha256(self._verifier_signature)

    def to_string(self) -> str:
        return f"[Block: height={self._height}, nb_tx={len(self._transactions)} hash={self.get_hash().hex()}]"

    def to_json(self) -> str:
        transactions = [json.loads(tx.to_json()) for tx in self._transactions]
        return json.dumps({"message_type": "Block", 'value': {
            'height': self._height, 'previous_block_hash': self._previous_block_hash.hex(),
            'start_timestamp': self._start_timestamp, 'verification_timestamp': self._verification_timestamp,
            'transactions': transactions, 'balance_list_hash': self._balance_list_hash.hex(),
            'verifier_identifier': self._verifier_identifier.hex(),
            'verifier_signature': self._verifier_signature.hex()}})

    @staticmethod
    def from_nyzo_html(html:str):
        """Decode html and returns a block object
        No more useful since nyzoblocks availability."""
        print("DEPRECATED: Block.from_nyzo_html(html)")
        """
        bs = BeautifulSoup(html, features="html.parser")

        height = int(bs.find('h1').text.replace('Nyzo block ', ''))

        test = bs.find_all('p')
        test = [item.text for item in test]

        hash = ByteUtil.string_to_bytes(test.pop(0))
        cycle_len = test.pop(0)  # unused
        previous_hash = ByteUtil.string_to_bytes(test.pop(0))
        start_ts = test.pop(0).split(' ')
        start_ts = int(float(start_ts[0])*1000)
        end_ts = test.pop(0).split(' ')
        end_ts = int(float(end_ts[0])*1000)  # not part of the signed data
        verif_ts = test.pop(0).split(' ')
        verif_ts = int(float(verif_ts[0])*1000)  # not part of the signed data
        verifier_signature = ByteUtil.string_to_bytes(test.pop().replace('signature: ', ''))
        verifier_id = ByteUtil.string_to_bytes(test.pop().replace('ID: ', ''))
        void = test.pop()
        balance_hash = ByteUtil.string_to_bytes(test.pop().replace('hash: ', ''))
        # only txs remain
        print(test)
        while len(test):
            tx_type = int(test.pop(0).split(' ')[0])
            tx_ts = test.pop(0).split(' ')
            tx_ts = int(float(tx_ts[1])*1000)
            tx_amount =  float(test.pop(0)[8:])* Transaction.micronyzo_multiplier_ratio
            receiver_id = ByteUtil.string_to_bytes(test.pop().replace('receiver ID: ', ''))
            if tx_type in [1, 2]:
                previous_height = 0
                # private long previousHashHeight;     // 8 bytes; 64-bit index of the block height of the previous-block hash
                # private byte[] previousBlockHash;    // 32 bytes (SHA-256 of a recent block in the chain)
                # private byte[] senderIdentifier;     // 32 bytes (256-bit public key of the sender)
                # private byte[] senderData;           // up to 32 bytes
                # private byte[] signature;
                pass
            else:
                pass

        transactions = []
        block = Block(height=height, previous_block_hash=previous_hash, start_timestamp=start_ts,
                 verification_timestamp=verif_ts, balance_list_hash=balance_hash,
                 verifier_identifier=verifier_id, verifier_signature=verifier_signature,transactions=transactions)
        return block
        """

    @staticmethod
    def from_nyzoblock(filename: str, verbose=False) -> list:
        """Read a nyzoblock and returns a list of blocks"""
        result = []
        with open(filename, 'rb') as file:
            buffer = memoryview(file.read())
        offset = 0
        num_blocks = struct.unpack(">H", buffer[offset:offset + 2])[0]  # Short, 2 bytes
        offset += 2
        if verbose:
            print(f"Num blocks {num_blocks}")
        last_block_height = None
        for i in range(num_blocks):
            block = Block(buffer=buffer[offset:])
            result.append(block)
            if last_block_height is None:
                last_block_height = block._height
            offset += block.get_byte_size(include_signature=True)
            if verbose:
                print(block.to_string())
            if i == 0 or last_block_height != block._height - 1:
                # We have a balance
                balance = BalanceList(buffer=buffer[offset:])
                offset += balance.get_byte_size()
                if verbose:
                    print(f"Balance {balance.to_string()}")
            last_block_height = block._height
        return result
