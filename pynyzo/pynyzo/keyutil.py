"""
Eddsa Ed25519 key handling
From
https://github.com/n-y-z-o/nyzoVerifier/blob/b73bc25ba3094abe3470ec070ce306885ad9a18f/src/main/java/co/nyzo/verifier/KeyUtil.java
"""

# Uses https://github.com/warner/python-ed25519 , c binding, fast


import ed25519


class KeyUtil:

    @staticmethod
    def main():
        signing_key, verifying_key = ed25519.create_keypair()
        print("my-secret-key", signing_key.to_ascii(encoding="hex"))
        vkey_hex = verifying_key.to_ascii(encoding="hex")
        print("the public key is", vkey_hex)


if __name__ == "__main__":
    KeyUtil.main()

