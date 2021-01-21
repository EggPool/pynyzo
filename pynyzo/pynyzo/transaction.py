
from pynyzo.hashutil import HashUtil
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
    type_cycle = 3
    type_cycle_signature = 4

    __slots__ = ('_type', '_timestamp', '_amount', '_receiver_identifier', '_previous_hash_height',
                 '_previous_block_hash', '_sender_identifier', '_sender_data', '_signature',
                 '_cycle_signatures', '_cycle_signature_transactions', '_cycle_transaction_vote', '_cycle_transaction_signature')

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
                 sender_identifier: bytes=None, sender_data: bytes=None, signature: bytes=None, cycle_transaction_vote: int=0, cycle_transaction_signature: bytes=None, balance_list_cycle_transaction: bool=False, app_log=None):
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
            self._cycle_transaction_vote = cycle_transaction_vote
            self._cycle_transaction_signature = cycle_transaction_signature
            self._signature = signature
        else:
            # fromByteBuffer constructor
            # These are the fields contained in all transactions.
            offset = 0
            self._type = struct.unpack(">B", buffer[offset:offset +1])[0]  # Byte
            offset += 1
            self._timestamp = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
            offset += 8

            if self._type == self.type_coin_generation:
                # self.app_log.error("TODO: Transaction.type_coin_generation")
                self._previous_hash_height = -1
                self._previous_block_hash = b''
                self._sender_identifier = b''
                self._sender_data = b''
                self._signature = b''
            elif self._type in [self.type_seed, self.type_standard, self.type_cycle]:
                self._amount = struct.unpack(">Q", buffer[offset:offset + 8])[0]  # Long, 8
                offset += 8
                self._receiver_identifier = buffer[offset:offset + FieldByteSize.identifier]
                offset += FieldByteSize.identifier
                self.app_log.debug(f"TX( {self._type}, {self._timestamp}, {self._amount}, "
                                   f"{self._receiver_identifier.hex()}")
                self._previous_hash_height = 0x0000ffffffffffff & struct.unpack(">Q", buffer[offset:offset + 8])[0]  # Long, 8
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
                if self._type == self.type_cycle:
                    self._cycle_signatures = []
                    self._cycle_signature_transactions = []
                    number_of_cycle_signatures = struct.unpack(">I", buffer[offset:offset +4])[0]  # Int, 4
                    offset += 4
                    # print("number_of_cycle_signatures", number_of_cycle_signatures)

                    if not balance_list_cycle_transaction:
                        for i in range(number_of_cycle_signatures):
                            identifier = buffer[offset:offset + FieldByteSize.identifier]
                            offset += FieldByteSize.identifier
                            cycle_signature = buffer[offset:offset + FieldByteSize.signature]
                            offset += FieldByteSize.signature

                            if identifier != self._sender_identifier:
                                self._cycle_signatures.append((identifier, cycle_signature))


                    else:
                        # When the explicitly marked as a balance list cycle transaction, read the additional fields for
                        # cycle transaction signatures.

                        for i in range(number_of_cycle_signatures):
                            child_timestamp = struct.unpack(">Q", buffer[offset:offset +8])[0]  # Long, 8
                            offset += 8

                            child_sender_identifier = buffer[offset:offset + FieldByteSize.identifier]
                            offset += FieldByteSize.identifier

                            child_cycle_transaction_vote = 1 if struct.unpack(">B", buffer[offset:offset +1])[0] == 1 else 0
                            offset += 1
                            child_signature =buffer[offset:offset + FieldByteSize.signature]
                            offset += FieldByteSize.signature
                            self._cycle_signature_transactions.append((child_sender_identifier, Transaction(timestamp=child_timestamp, sender_identifier=child_sender_identifier, sender_data=bytes(self._signature) + b':' + bytes(child_cycle_transaction_vote), signature=child_signature, balance_list_cycle_transaction=balance_list_cycle_transaction)))

            elif self._type == self.type_cycle_signature:
                self._amount = 0
                self._receiver_identifier = b'\0'
                self._previous_hash_height = 0
                self._previous_block_hash = b'\0'
                self._sender_data = b''
                self._sender_identifier = buffer[offset:offset + FieldByteSize.identifier]
                offset += FieldByteSize.identifier
                self._cycle_transaction_vote = 1 if struct.unpack(">B", buffer[offset:offset +1])[0] == 1 else 0
                offset += 1
                #print("tx cycle sign",bytes(self._sender_identifier).hex(), self._cycle_transaction_vote)
                self._cycle_transaction_signature = buffer[offset:offset + FieldByteSize.signature]
                offset += FieldByteSize.signature
                #print("cycle sign",bytes(self._cycle_transaction_signature).hex())
                self._signature = buffer[offset:offset + FieldByteSize.signature]
                #print("sign",bytes(self._signature).hex())
                offset += FieldByteSize.signature
            else:
                self.app_log.warning(f"Unknown Transaction type: {self._type}")
                exit()

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

    def get_cycle_transaction_vote(self):
        return self._cycle_transaction_vote

    def cycle_transaction_signature(self):
        return self._cycle_transaction_signature

    def get_fee(self):
        if self._type in [self.type_cycle, self.type_cycle_signature]:
            return 0
        return (self.get_amount() + 399) / 400

    def get_byte_size(self, for_signing:bool=False):

        size = FieldByteSize.transactionType + FieldByteSize.timestamp

        if self._type == self.type_cycle_signature:
            size += FieldByteSize.identifier + FieldByteSize.booleanField + FieldByteSize.signature
            if not for_signing:
                size += FieldByteSize.signature

        else:
            size += FieldByteSize.transactionAmount + FieldByteSize.identifier

        if self._type in [self.type_seed, self.type_standard, self.type_cycle]:
            if for_signing:
                size += FieldByteSize.hash  # previous-block hash for signing
            else:
                size += FieldByteSize.blockHeight  # previous-hash height for storage and transmission
            size += FieldByteSize.identifier  # sender identifier
            if for_signing:
                size += FieldByteSize.hash  # sender data hash for signing
            else:
                size += 1 + len(self._sender_data) + FieldByteSize.signature  # length specifier + sender data + transaction signature
            if self._type == self.type_cycle:
                # These are stored differently in the v1 and v2 blockchains. The cycleSignatures field is used for
                # the v1 blockchain, and the cycleSignatureTransactions field is used for the v2 blockchain.
                if self._cycle_signatures:
                    # The v1 blockchain stores identifier and signature for each.
                    #print("V1 cycle signature transaction")
                    size += FieldByteSize.unnamedInteger + len(self._cycle_signatures) * (FieldByteSize.identifier + FieldByteSize.signature)
                else:
                    # The v2 blockchain stores timestamp, identifier, vote, and signature for each.
                    size += FieldByteSize.unnamedInteger + len(self._cycle_signature_transactions) * (FieldByteSize.timestamp + FieldByteSize.identifier + FieldByteSize.booleanField + FieldByteSize.signature)
                    #print("V2 cycle signature transaction")
                    #exit()

        return size

    def get_bytes(self, for_signing: bool=False):
        result = list()
        result.append(struct.pack(">B", self._type))  # byte
        result.append(struct.pack(">Q", self._timestamp))  # Long

        if self._type in [self.type_coin_generation, self.type_seed, self.type_standard, self.type_cycle]:
            result.append(struct.pack(">Q", self._amount))  # Long
            result.append(self._receiver_identifier)
        elif self._type == self.type_cycle_signature:
            result.append(self._sender_identifier)
            result.append(struct.pack(">B", self._cycle_transaction_vote))  # byte
            result.append(self._cycle_transaction_signature)
            if not for_signing:
                result.append(self._signature)

        if self._type in [self.type_seed, self.type_standard, self.type_cycle]:
            if for_signing:
                result.append(self._previous_block_hash)
            else:
                result.append(struct.pack(">Q", self._previous_hash_height))  # Long

            result.append(self._sender_identifier)

            # For serializing, we use the raw sender data with a length specifier. For signing, we use the double-
            # SHA-256 of the user data. This will allow us to remove inappropriate or illegal metadata from the
            # blockchain at a later date by replacing it with its double-SHA-256 without compromising the signature
            # integrity.
            if for_signing:
                # print("double sha", HashUtil.double_sha256(self._sender_data).hex())
                result.append(HashUtil.double_sha256(self._sender_data))
            else:
                result.append(struct.pack(">B", len(self._sender_data)))  # byte
                result.append(self._sender_data)

            if not for_signing:
                result.append(self._signature)

                # For cycle transactions, order the signatures by verifier identifier. In the v1 blockchain, the
                # cycleSignatures field is used. In the v2 blockchain, the cycleSignatureTransactions field is used.
                if self._type == self.type_cycle:
                    if self._cycle_signatures:
                        result.append(struct.pack(">I", len(self._cycle_signatures)))  # int, 4
                        for identifier, signature in sorted(self._cycle_signatures, key=lambda x: x[0]):
                            result.append(identifier)
                            result.append(signature)
                    else:
                        result.append(struct.pack(">I", len(self._cycle_signature_transactions)))  # int, 4
                        for identifier, transaction in sorted(self._cycle_signature_transactions, key=lambda x: x[0]):
                            result.append(struct.pack(">Q", transaction.get_timestamp()))  # Long
                            result.append(transaction.get_sender_identifier())
                            result.append(transaction.get_cycle_transaction_vote())
                            result.append(transaction.get_signature())

        return b''.join(result)

    def to_json(self) -> str:
        signature = self._signature.hex() if self._signature else None
        if self._type == self.type_coin_generation:
            return json.dumps({"message_type": "Transaction", 'value': {
                'type': self._type, 'timestamp': self._timestamp, 'amount': self._amount,
                'receiver_identifier': self._receiver_identifier.hex()}})
        elif self._type == self.type_cycle_signature:
            return json.dumps({"message_type": "Transaction", 'value': {
                'type': self._type,'timestamp': self._timestamp,
                # 'amount': self._amount,
                # 'receiver_identifier': self._receiver_identifier.hex(), 'previous_hash_height': self._previous_hash_height,
                # 'previous_block_hash': self._previous_block_hash.hex(),
                'sender_identifier': self._sender_identifier.hex(),
                # 'sender_data': self._sender_data.hex(),
                'vote': self._cycle_transaction_vote, 'cycle_transaction_signature': self._cycle_transaction_signature.hex(),
                'signature': signature}})

        return json.dumps({"message_type": "Transaction", 'value': {
            'type': self._type,'timestamp': self._timestamp, 'amount': self._amount,
            'receiver_identifier': self._receiver_identifier.hex(), 'previous_hash_height': self._previous_hash_height,
            'previous_block_hash': self._previous_block_hash.hex(), 'sender_identifier': self._sender_identifier.hex(),
            'sender_data': self._sender_data.hex(), 'signature': signature}})

    @classmethod
    def from_vote_data(cls, timestamp: int, sender_identifier: bytes, vote: int, transaction_signature: bytes, signature: bytes=None):
        return Transaction(buffer=None, type=cls.type_cycle_signature, timestamp=timestamp,
                           sender_identifier=sender_identifier, cycle_transaction_vote=vote,
                           cycle_transaction_signature=transaction_signature, signature=signature)
