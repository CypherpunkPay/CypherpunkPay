class CoinNetworkState(object):

    _currency: str
    _current_height: int

    def __init__(self, currency: str, current_height=0):
        self._currency = currency.casefold()
        self._current_height = current_height

    def set_current_height(self, value):
        self._current_height = value

    def get_current_height(self):
        return self._current_height

    def get_currency(self):
        return self._currency
