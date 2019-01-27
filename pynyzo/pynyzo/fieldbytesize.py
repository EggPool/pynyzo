"""
From https://github.com/n-y-z-o/nyzoVerifier/blob/master/src/main/java/co/nyzo/verifier/FieldByteSize.java
"""


class FieldByteSize:

    balanceListLength = 4
    blockHeight = 8
    blocksUntilFee = 2
    booleanField = 1
    cycleLength = 4
    frozenBlockListLength = 2
    hash = 32
    hashListLength = 1
    ipAddress = 4
    messageLength = 4
    port = 4
    rolloverTransactionFees = 1
    seed = 32
    timestamp = 8
    transactionAmount = 8
    transactionType = 1
    messageType = 2
    identifier = 32
    nodeListLength = 4
    signature = 64
    stringLength = 2
    transactionPoolLength = 4
    unfrozenBlockPoolLength = 2
    unnamedDouble = 8
    unnamedInteger = 4
    unnamedShort = 2
    voteListLength = 1

    @staticmethod
    def string(value: str) -> int:
        return FieldByteSize.stringLength + len(value.encode('utf-8'))
