import base64
import secrets


class SafeUid(object):

    @staticmethod
    def gen(nbytes=16) -> str:
        entropy = secrets.token_bytes(nbytes)    # 16 bytes == 128 bits
        base32_bytes = base64.b32encode(entropy)
        base32_text = base32_bytes.decode("ascii")
        base32_lowercase = base32_text.casefold()
        base32_lowercase_no_padding = base32_lowercase.replace('=', '')
        return base32_lowercase_no_padding
