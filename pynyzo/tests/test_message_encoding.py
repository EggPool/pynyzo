import pytest
import sys

sys.path.append('../')
from pynyzo.messages.statusresponse import StatusResponse
from pynyzo.messages.blockrequest import BlockRequest


def test_status_1(verbose=False):
    strings = ['line1', 'line2']
    message = StatusResponse(lines=strings)
    if verbose:
        print(message.get_bytes())
    assert message.get_bytes() == b'\x02\x00\x05line1\x00\x05line2'
    message2 = StatusResponse(buffer=b'0000000000' + message.get_bytes())  # 10 more bytes to account for timestamp + type
    if verbose:
        print(message2.get_lines())
    assert str(message2.get_lines()) == "['line1', 'line2']"


def test_block_request(verbose=False):
    message = BlockRequest(start_height=10, end_height=20, include_balance_list=True)
    if verbose:
        print(message.get_bytes())
    assert message.get_bytes() == b'\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x00\x00\x00\x00\x14\x01'
    message2 = BlockRequest(buffer=b'0000000000' + message.get_bytes())  # 10 more bytes to account for timestamp + type
    if verbose:
        print(message2.to_string())
    assert str(message2.to_string()) == "[BlockRequest(10, 20, True)]"


if __name__ == "__main__":
    test_block_request(True)
