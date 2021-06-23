from typing import List

from cypherpunkpay.exceptions import UnsupportedCoin
from cypherpunkpay.models.coin_network_state import CoinNetworkState


class CoinNetworks(object):

    _coin_network_states: List[CoinNetworkState]

    def __init__(self):
        self._coin_network_states = [
            CoinNetworkState('btc'),
            CoinNetworkState('xmr')
        ]

    def get_state(self, currency: str) -> CoinNetworkState:
        for coin_network_state in self._coin_network_states:
            if coin_network_state.get_currency() == currency.casefold():
                return coin_network_state
        raise UnsupportedCoin(currency)
