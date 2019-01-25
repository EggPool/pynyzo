import pytest
import sys

sys.path.append('../')
from pynyzo.messages.statusresponse import StatusResponse


def test_status_1(verbose=False):
    strings = ['line1', 'line2']
    message = StatusResponse(lines=strings)
    if verbose:
        print(message.get_bytes())
    assert message.get_bytes() == b'\x02\x05\x00line1\x05\x00line2'
    message2 = StatusResponse(buffer=message.get_bytes())
    if verbose:
        print(message2.get_lines())
    assert str(message2.get_lines()) == "['line1', 'line2']"


if __name__ == "__main__":
    test_status_1(True)
