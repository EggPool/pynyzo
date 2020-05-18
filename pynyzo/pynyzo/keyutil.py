"""
Eddsa Ed25519 key handling
From
https://github.com/n-y-z-o/nyzoVerifier/blob/b73bc25ba3094abe3470ec070ce306885ad9a18f/src/main/java/co/nyzo/verifier/KeyUtil.java

plus
https://github.com/n-y-z-o/nyzoVerifier/blob/17509f03a7f530c0431ce85377db9b35688c078e/src/main/java/co/nyzo/verifier/util/SignatureUtil.java
"""

# Uses https://github.com/warner/python-ed25519 , c binding, fast


import ed25519
import hashlib
from pynyzo.byteutil import ByteUtil


class KeyUtil:

    @staticmethod
    def main():
        """Temp test, not to be used"""
        signing_key, verifying_key = ed25519.create_keypair()
        print("Original private key", ByteUtil.bytes_as_string_with_dashes(signing_key.to_bytes()[:32]))
        # signing key has signing + verifying, we keep the first 32 to only get the private part.
        print("Original public key", ByteUtil.bytes_as_string_with_dashes(verifying_key.to_bytes()))

    @staticmethod
    def generateSeed(hashable_keyword: str='') -> bytes:
        """Generate a private key, with optional keyword to get reproducible tests results or later HD Wallet."""
        if len(hashable_keyword):
            seed = hashlib.sha256(hashable_keyword).digest()
            signing_key = ed25519.SigningKey(seed)
        else:
            signing_key, _ = ed25519.create_keypair()
        return signing_key.to_bytes()[:32]

    @staticmethod
    def private_to_public(private: str) -> str:
        """Temp Test"""
        keydata = bytes.fromhex(private)
        signing_key = ed25519.SigningKey(keydata)
        verifying_key = signing_key.get_verifying_key()
        vkey_hex = verifying_key.to_ascii(encoding="hex")
        return vkey_hex.decode('utf-8')

    @staticmethod
    def get_from_private_seed_file(filename: str):
        """returns priv and pub key - as object - from the stored nyzo text id format"""
        with open(filename) as f:
            nyzo = f.read(80).replace('-', '').encode('utf-8').strip()
            signing_key = ed25519.SigningKey(nyzo, encoding="hex")
            verifying_key = signing_key.get_verifying_key()
        return signing_key, verifying_key

    @staticmethod
    def get_from_private_seed(seed: str):
        """returns priv and pub key - as object - from an hex seed"""
        seed = seed.replace('-', '').encode('utf-8').strip()
        signing_key = ed25519.SigningKey(seed, encoding="hex")
        verifying_key = signing_key.get_verifying_key()
        return signing_key, verifying_key


    @staticmethod
    def save_to_private_seed_file(filename: str, key: bytes) -> None:
        """Saves the privkey to the nyzo formatted file"""
        nyzo_format = ByteUtil.bytes_as_string_with_dashes(key)
        with open(filename, 'w') as f:
            f.write(nyzo_format)

    @staticmethod
    def sign_bytes(bytes_to_sign: bytes, private_key: ed25519.SigningKey) -> bytes:
        sig = private_key.sign(bytes_to_sign)
        return sig

    @staticmethod
    def signature_is_valid(signature: bytes, signed_bytes: bytes, public_id: bytes) -> bool:
        verifying_key = ed25519.VerifyingKey(public_id)
        # todo: cache key from id, see https://github.com/n-y-z-o/nyzoVerifier/blob/17509f03a7f530c0431ce85377db9b35688c078e/src/main/java/co/nyzo/verifier/util/SignatureUtil.java
        try:
            verifying_key.verify(signature, signed_bytes)
            # print("signature is good")
            return True
        except ed25519.BadSignatureError:
            # print("signature is bad!")
            return False


if __name__ == "__main__":
    KeyUtil.main()
    # KeyUtil.private_to_public('nyzo-formatted-private-key'.replace('-', ''))


