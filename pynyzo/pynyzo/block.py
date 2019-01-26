

from pynyzo.messageobject import MessageObject
from pynyzo.helpers import base_app_log
from pynyzo.messagetype import MessageType
from pynyzo.fieldbytesize import FieldByteSize
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

    __slots__ = ('_height', '_previousBlockHash', '_startTimestamp', '_verificationTimestamp', '_transactions',
                 '_balanceListHash', '_verifierIdentifier', '_verifierSignature', '_continuityState', '_SignatureState',
                 '_cycleInformation')
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
