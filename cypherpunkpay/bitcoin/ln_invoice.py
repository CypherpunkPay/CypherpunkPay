class LnInvoice(object):

    amt_paid_msat: [int, None] = None

    @property
    def amt_paid_sat(self) -> [int, None]:
        if self.amt_paid_msat is None:
            return None
        return int(self.amt_paid_msat / 1000)
