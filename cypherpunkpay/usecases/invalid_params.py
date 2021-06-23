from typing import Dict


class InvalidParams(Exception):

    def __init__(self, errors: Dict[str, str]):
        self.errors = errors
