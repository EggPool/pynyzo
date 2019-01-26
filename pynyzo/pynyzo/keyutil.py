"""
Eddsa Ed25519 key handling
From
https://github.com/n-y-z-o/nyzoVerifier/blob/b73bc25ba3094abe3470ec070ce306885ad9a18f/src/main/java/co/nyzo/verifier/KeyUtil.java
"""

# Uses https://github.com/warner/python-ed25519 , c binding, fast


import ed25519
from pynyzo.byteutil import ByteUtil


class KeyUtil:

    @staticmethod
    def main():
        """Temp test"""
        signing_key, verifying_key = ed25519.create_keypair()
        print("Original private key", ByteUtil.bytes_as_string_with_dashes(signing_key.to_bytes()[:32]))
        # signing key has signing + verifying, we keep the first 32 to only get the private part.
        print("Original public key", ByteUtil.bytes_as_string_with_dashes(verifying_key.to_bytes()))

    @staticmethod
    def private_to_public(private: str):
        """Temp Test"""
        keydata = bytes.fromhex(private)
        signing_key = ed25519.SigningKey(keydata)
        verifying_key = signing_key.get_verifying_key()
        vkey_hex = verifying_key.to_ascii(encoding="hex")
        print("the public key is", vkey_hex)
        return vkey_hex.decode('utf-8')


if __name__ == "__main__":
    KeyUtil.main()
    # KeyUtil.private_to_public('nyzo-formatted-private-key'.replace('-', ''))

