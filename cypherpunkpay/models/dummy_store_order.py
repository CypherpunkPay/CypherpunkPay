import logging as log
from decimal import Decimal


class DummyStoreOrder:

    uid: str = None

    item_id: int = None

    total: Decimal = 0
    currency: str = None

    cc_total: [Decimal, None] = None
    cc_currency: str = None

    def __init__(self, uid: str, item_id: int, total: [Decimal, str], currency: str):
        from cypherpunkpay.db.dev_examples import DevExamples
        assert item_id in range(0, len(DevExamples.DUMMY_STORE_ITEMS))
        self.uid = uid
        self.item_id = item_id
        self.total = Decimal(total)
        self.currency = currency.casefold()

    def payment_completed(self, cc_total: [Decimal, str], cc_currency: str):
        self.cc_total = Decimal(cc_total)
        self.cc_currency = cc_currency.casefold()

    def ship(self):
        log.info(f'Shipping order: {self.__dict__}')

    def dont_ship(self):
        log.info(f'Not shipping order because of failed payment: {self.__dict__}')

    def is_payment_completed(self):
        return self.cc_total and self.cc_currency

    @property
    def item(self):
        from cypherpunkpay.db.dev_examples import DevExamples
        return DevExamples.DUMMY_STORE_ITEMS[self.item_id]
