from cypherpunkpay.common import *


class Credit:

    _value: Decimal
    _has_replaceable_flag: bool
    _confirmed_height: [None, int]

    def __init__(self, value: [Decimal, int], confirmed_height: [None, int], has_replaceable_flag: bool):
        assert(isinstance(value, int) or isinstance(value, Decimal))
        assert(value > 0)
        self._value = Decimal(value)
        self._has_replaceable_flag = has_replaceable_flag  # For Bitcoin that means RBF
        self._confirmed_height = confirmed_height          # None if unconfirmed

    @staticmethod
    def unconfirmed(value: [Decimal, int]):
        return Credit(value, confirmed_height=None, has_replaceable_flag=False)

    @staticmethod
    def unconfirmed_replaceable(value: [Decimal, int]):
        return Credit(value, confirmed_height=None, has_replaceable_flag=True)

    @staticmethod
    def confirmed(value: [Decimal, int], height: int):
        return Credit(value, height, has_replaceable_flag=False)

    def value(self):
        return self._value

    def is_unconfirmed_replaceable(self):
        return self.is_unconfirmed() and self._has_replaceable_flag

    def is_unconfirmed_non_replaceable(self):
        return self.is_unconfirmed() and not self._has_replaceable_flag

    def is_unconfirmed(self):
        return self._confirmed_height is None

    def is_confirmed(self):
        return self._confirmed_height is not None

    def confirmed_height(self):
        return self._confirmed_height

    def __eq__(self, other):
        if isinstance(other, Credit):
            return self._value == other._value and \
                   self._confirmed_height == other._confirmed_height
        return False

    def __repr__(self):
        return f'{self.__dict__}'

    # We only aim here at sorting stability (not sorting meaning), so the two lists of same Credits could compare equal
    def sorting_key(self) -> str:
        return f'{self._value} {self._confirmed_height} {self._has_replaceable_flag}'
