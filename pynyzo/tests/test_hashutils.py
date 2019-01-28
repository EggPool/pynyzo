import pytest
import sys
import ed25519
import hashlib

sys.path.append('../')
from pynyzo.hashutil import HashUtil

# See https://github.com/n-y-z-o/nyzoVerifier/blob/master/src/main/java/co/nyzo/verifier/HashUtil.java


def test_single_1(verbose=False):
    hello = b"hello"
    hex = HashUtil.single_sha256(hello).hex()
    if verbose:
        print("hex", hex)
    assert hex == '2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824'


def test_single_2(verbose=False):
    hello = b''
    hex = HashUtil.single_sha256(hello).hex()
    if verbose:
        print("hex", hex)
    assert hex == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'


def test_double_1(verbose=False):
    hello = b"hello"
    hex = HashUtil.double_sha256(hello).hex()
    if verbose:
        print("hex", hex)
    assert hex == '9595c9df90075148eb06860365df33584b75bff782a510c6cd4883a419833d50'


def test_double_2(verbose=False):
    hello = b''
    hex = HashUtil.double_sha256(hello).hex()
    if verbose:
        print("hex", hex)
    assert hex == '5df6e0e2761359d30a8275058e299fcc0381534545f55cf43e41983f5d4c9456'


if __name__ == "__main__":
    test_single_1(True)
    test_single_2(True)
    test_double_1(True)
    test_double_2(True)
