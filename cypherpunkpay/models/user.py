from cypherpunkpay.common import *


class User:

    id: [int, None]
    username: str
    password_hash: str
    created_at: datetime
    updated_at: datetime

    def __init__(self, username: str, password_hash: str):
        self.id = None
        self.username = username
        self.password_hash = password_hash
        self.created_at = utc_now()
        self.updated_at = self.created_at
