from cypherpunkpay.globals import *
from typing import List

import monero.transaction


class MoneroTxDb(object):

    confirmed_txs: List[monero.transaction.Transaction] = []
    mempool_txs: List[monero.transaction.Transaction] = []

    # def get_after(self, since: datetime.datetime) -> List[monero.transaction.Transaction]:
    #     self.txs[0].timestamp
