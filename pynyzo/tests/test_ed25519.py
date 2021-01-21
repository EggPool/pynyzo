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


def test_sign_1(verbose=False):
    master = b'9444'  # Nyzo port as test seed
    seed = hashlib.sha256(master).digest()
    # NEVER USE THAT KEY IN REAL WORLD!!!
    signing_key = ed25519.SigningKey(seed)
    message = b'Message to sign'
    sig = signing_key.sign(message)
    if verbose:
        print("Signature", sig.hex())
    assert sig.hex() == 'df5cc085f0892837404525b9524089e4ecf703e050c0d42b798d687356c3984c9f86c0958353f861a17cf8d6a0019cc90a2c8414021fd64110ce0e6c5a923f00'


def test_verify_1(verbose=False):
    message = b'Message to sign'
    public = bytes.fromhex('a34abe2176eeb545735b25ff68c41d716db462e55c7c3a5d48db0ae4fc95ae9e')
    signature = bytes.fromhex('df5cc085f0892837404525b9524089e4ecf703e050c0d42b798d687356c3984c9f86c0958353f861a17cf8d6a0019cc90a2c8414021fd64110ce0e6c5a923f00')
    verifying_key = ed25519.VerifyingKey(public)
    try:
        verifying_key.verify(signature, message)
        if verbose:
            print("signature is good")
    except:
        raise


if __name__ == "__main__":
    # test_keys_2(True)
    # KeyUtil.main()
    test_sign_1(True)
    test_verify_1(True)
