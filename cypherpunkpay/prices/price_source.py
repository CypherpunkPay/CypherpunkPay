from decimal import Decimal
from abc import ABC, abstractmethod

from cypherpunkpay.net.http_client.tor_http_client import BaseHttpClient


class PriceSource(ABC):

    _http_client: BaseHttpClient

    def __init__(self, http_client):
        self._http_client = http_client

    @abstractmethod
    def get(self, coin: str, fiat: str) -> [Decimal, None]:
        pass
