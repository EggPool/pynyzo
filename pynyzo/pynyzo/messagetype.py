"""Nyzo Message types"""

from enum import Enum
# see https:#docs.python.org/3/library/enum.html

"""
MessageType(5) will return a <MessageType.Transaction5: 5>
message_type.name will return a str with the MessageType name, like 'Transaction5'
message_type.value will return an int with the MessageType value, like 5 - same a nyzo getValue()
"""


class MessageType(Enum):

    Invalid0 = 0
    _BootstrapRequest1 = 1  # replaced with BootstrapRequestV2_35
    _BootstrapResponse2 = 2  # replaced with BootstrapResponseV2_36
    NodeJoin3 = 3
    NodeJoinResponse4 = 4
    Transaction5 = 5
    TransactionResponse6 = 6
    PreviousHashRequest7 = 7
    PreviousHashResponse8 = 8
    NewBlock9 = 9
    NewBlockResponse10 = 10
    BlockRequest11 = 11
    BlockResponse12 = 12
    TransactionPoolRequest13 = 13
    TransactionPoolResponse14 = 14
    MeshRequest15 = 15
    MeshResponse16 = 16
    StatusRequest17 = 17
    StatusResponse18 = 18
    BlockVote19 = 19
    BlockVoteResponse20 = 20
    NewVerifierVote21 = 21
    NewVerifierVoteResponse22 = 22
    MissingBlockVoteRequest23 = 23
    MissingBlockVoteResponse24 = 24
    MissingBlockRequest25 = 25
    MissingBlockResponse26 = 26
    TimestampRequest27 = 27
    TimestampResponse28 = 28
    HashVoteOverrideRequest29 = 29
    HashVoteOverrideResponse30 = 30
    ConsensusThresholdOverrideRequest31 = 31
    ConsensusThresholdOverrideResponse32 = 32
    NewVerifierVoteOverrideRequest33 = 33
    NewVerifierVoteOverrideResponse34 = 34
    BootstrapRequestV2_35 = 35
    BootstrapResponseV2_36 = 36
    BlockWithVotesRequest37 = 37
    BlockWithVotesResponse38 = 38

    # test messages
    Ping200 = 200
    PingResponse201 = 201

    # maintenance messages
    UpdateRequest300 = 300  # updates the verifier with the latest code from the Git repository, rebuilds, and restarts
    UpdateResponse301 = 301

    # debugging messages -- these are meant to cause problems to test resiliency or to provide information that is not
    # necessary for normal operation
    BlockRejectionRequest400 = 400  # discards all blocks received for the next 10 seconds
    BlockRejectionResponse401 = 401
    DetachmentRequest402 = 402  # stops producing blocks for two verifier cycles
    DetachmentResponse403 = 403
    UnfrozenBlockPoolPurgeRequest404 = 404  # clears the unfrozen block pool
    UnfrozenBlockPoolPurgeResponse405 = 405
    UnfrozenBlockPoolStatusRequest406 = 406  # gets textual information about the unfrozen block pool
    UnfrozenBlockPoolStatusResponse407 = 407
    MeshStatusRequest408 = 408  # gets textual information about the mesh
    MeshStatusResponse409 = 409
    TogglePauseRequest410 = 410  # pauses/un-pauses verifier
    TogglePauseResponse411 = 411
    ConsensusTallyStatusRequest412 = 412
    ConsensusTallyStatusResponse413 = 413
    NewVerifierTallyStatusRequest414 = 414
    NewVerifierTallyStatusResponse415 = 415
    BlacklistStatusRequest416 = 416
    BlacklistStatusResponse417 = 417

    # bootstrapping messages
    ResetRequest500 = 500   # resets the blockchain   TODO: key this to the local verifier before release
    ResetResponse501 = 501

    # the highest allowable message number is 65535
    IncomingRequest65533 = 65533  # for debugging -- passed to readFromStream by meshListener/meshListenerController
    Error65534 = 65534
    Unknown65535 = 65535
