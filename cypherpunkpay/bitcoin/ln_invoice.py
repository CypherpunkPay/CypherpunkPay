class LnInvoice(object):

    is_settled: bool = False
    amt_paid_msat: int = 0

    @property
    def amt_paid_sat(self) -> int:
        return int(self.amt_paid_msat / 1000)
