from cypherpunkpay.common import *

from cypherpunkpay.models.credit import Credit


class AddressCredits:

    _credits: List[Credit]

    def __init__(self, credits: List[Credit], blockchain_height: int):
        assert(isinstance(credits, List))
        assert(isinstance(blockchain_height, int))
        assert(blockchain_height >= 0)
        self._credits = sorted(credits, key=Credit.sorting_key)
        self._blockchain_height = blockchain_height

    def any(self) -> List[Credit]:
        return self._credits

    def unconfirmed_replaceable(self):
        return list(filter(lambda c: c.is_unconfirmed_replaceable(), self._credits))

    def unconfirmed_non_replaceable(self):
        return list(filter(lambda c: c.is_unconfirmed_non_replaceable(), self._credits))

    def confirmed_1(self):
        return self.confirmed_n(1)

    def confirmed_n(self, required):
        return \
            list(
                filter(
                    lambda c: c.is_confirmed() and self._blockchain_height - c.confirmed_height() + 1 >= required,
                    self._credits
                )
            )

    def blockchain_height(self):
        return self._blockchain_height

    def __eq__(self, other):
        if isinstance(other, AddressCredits):
            if self._blockchain_height == other._blockchain_height:
                if len(self._credits) == len(other._credits):
                    for i in range(len(self._credits)):
                        if self._credits[i] != other._credits[i]:
                            return False
                    return True
        return False
