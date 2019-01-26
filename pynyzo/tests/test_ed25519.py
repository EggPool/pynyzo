import pytest
import sys
import ed25519
import hashlib

sys.path.append('../')
from pynyzo.keyutil import KeyUtil
from pynyzo.byteutil import ByteUtil


def test_keys_1(verbose=False):
    master = b'9444'  # Nyzo port as test seed
    seed = hashlib.sha256(master).digest()
    assert seed == b',V@?\xcf\xfb\xd14M\xfbw&\x89\xf6\x0eDoDq\xd2\xca\x17\xf3\xa5\xea\xa6)\xf6\xc52<l'
    # NEVER USE THAT KEY IN REAL WORLD!!!
    signing_key = ed25519.SigningKey(seed)
    hex = signing_key.to_ascii(encoding="hex").decode('utf-8')
    if verbose:
        print("private", hex)
    assert hex == '2c56403fcffbd1344dfb772689f60e446f4471d2ca17f3a5eaa629f6c5323c6c'
    public = KeyUtil.private_to_public(hex)
    if verbose:
        print("public", public)
    assert public == 'a34abe2176eeb545735b25ff68c41d716db462e55c7c3a5d48db0ae4fc95ae9e'


def test_keys_2(verbose=False):
    master = b'9444'  # Nyzo port as test seed
    seed = hashlib.sha256(master).digest()
    # NEVER USE THAT KEY IN REAL WORLD!!!
    signing_key = ed25519.SigningKey(seed)
    nyzo_format = ByteUtil.bytes_as_string_with_dashes(signing_key.to_bytes()[:32])
    if verbose:
        print("private nyzo format", nyzo_format)
    assert nyzo_format == '2c56403f-cffbd134-4dfb7726-89f60e44-6f4471d2-ca17f3a5-eaa629f6-c5323c6c'


if __name__ == "__main__":
    # test_keys_2(True)
    KeyUtil.main()
