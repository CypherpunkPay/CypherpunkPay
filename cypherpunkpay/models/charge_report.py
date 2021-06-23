from cypherpunkpay.common import *


class ChargeReport(object):

    completed: int = 0
    expired: int = 0
    cancelled: int = 0

    awaiting: int = 0
    awaiting_payment: int = 0
    awaiting_confirmation: int = 0

    completed_usd: Decimal = Decimal(0)

    @property
    def total(self) -> int:
        return self.final + self.awaiting

    @property
    def final(self) -> int:
        return self.completed + self.expired + self.cancelled

    @property
    def completed_percent(self) -> float:
        if self.final == 0:
            return 0
        else:
            return round(100 * self.completed / self.final)

    @property
    def expired_percent(self) -> float:
        if self.final == 0:
            return 0
        else:
            return round(100 * self.expired / self.final)

    @property
    def cancelled_percent(self) -> float:
        if self.final == 0:
            return 0
        else:
            return round(100 * self.cancelled / self.final)

    @property
    def awaiting_payment_percent(self) -> float:
        if self.awaiting == 0:
            return 0
        else:
            return round(100 * self.awaiting_payment / self.awaiting)

    @property
    def awaiting_confirmation_percent(self) -> float:
        if self.awaiting == 0:
            return 0
        else:
            return round(100 * self.awaiting_confirmation / self.awaiting)
