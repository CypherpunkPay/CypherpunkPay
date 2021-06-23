import os
from hashlib import pbkdf2_hmac
import binascii


class PBKDF2(object):

    ITERATIONS = int(200_000)

    @staticmethod
    def hash(password: str) -> str:
        salt_bytes = os.urandom(32)  # DO NOT CHANGE
        password_bytes = password.encode('utf8')
        hash_bytes = pbkdf2_hmac('sha256', password_bytes, salt_bytes, PBKDF2.ITERATIONS)
        iterations_bytes = PBKDF2.ITERATIONS.to_bytes(4, 'big', signed=False)
        full_bytes = iterations_bytes + salt_bytes + hash_bytes
        full_str = binascii.hexlify(full_bytes).decode('ascii')
        return full_str

    @staticmethod
    def password_is_correct(candidate_password: str, hashed_password: str) -> bool:
        candidate_password_bytes = candidate_password.encode('utf8')
        full_bytes = binascii.unhexlify(hashed_password)
        iterations = int.from_bytes(full_bytes[:4], 'big', signed=False)
        salt_bytes = full_bytes[4:36]
        hash_bytes = full_bytes[36:]
        candidate_hash_bytes = pbkdf2_hmac('sha256', candidate_password_bytes, salt_bytes, iterations)
        return candidate_hash_bytes == hash_bytes
