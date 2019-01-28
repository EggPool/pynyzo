"""
Partial transcript from
https://github.com/n-y-z-o/nyzoVerifier/blob/master/src/main/java/co/nyzo/verifier/HashUtil.java
"""


from hashlib import sha256


class HashUtil:

    @staticmethod
    def double_sha256(data: bytes) -> bytes:
        return sha256(sha256(data).digest()).digest()

    @staticmethod
    def single_sha256(data: bytes) -> bytes:
        if data is None:
            data = b''
        return sha256(data).digest()
