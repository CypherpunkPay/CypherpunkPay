import monero.backends.offline
import monero.transaction
from monero.wallet import Wallet as MoneroWallet
from monero.account import Account
from monero.address import address

from cypherpunkpay.globals import *
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit
from cypherpunkpay.monero.monero_tx_db import MoneroTxDb
from cypherpunkpay.usecases.use_case import UseCase


class CalcMoneroAddressCreditsUC(UseCase):

    def __init__(self, monero_tx_db: MoneroTxDb, since: datetime.datetime, subaddress: str, secret_view_key: str, current_height: int):
        self.monero_tx_db = monero_tx_db
        self.since = since
        self.address = subaddress
        self.secret_view_key = secret_view_key
        self.current_height = current_height

    def exec(self) -> [AddressCredits, None]:
        view_wallet = self.monero_view_wallet()
        since = self.decentralization_adjusted_since()
        credits = []

        confirmed_txs = self.monero_tx_db.confirmed_txs[:]  # clone as source list is subject to change by other thread
        for tx in confirmed_txs:
            if tx.timestamp >= since:
                outputs: List[monero.transaction.Output] = tx.outputs(wallet=view_wallet)
                for output in outputs:
                    if output.amount:
                        credit = Credit(value=output.amount, confirmed_height=tx.height, has_replaceable_flag=False)
                        credits.append(credit)

        mempool_txs = self.monero_tx_db.mempool_txs[:]      # clone as source list is subject to change by other thread
        for tx in mempool_txs:
            outputs: List[monero.transaction.Output] = tx.outputs(wallet=view_wallet)
            for output in outputs:
                if output.amount:
                    credit = Credit(value=output.amount, confirmed_height=None, has_replaceable_flag=False)
                    credits.append(credit)

        return AddressCredits(credits, blockchain_height=self.current_height)

    def monero_view_wallet(self):

        class SubaddressViewWallet(object):
            """Adapter class to satisfy emesik Monero library Transaction#outputs() call"""
            _address = None
            _svk = None

            def __init__(self, subaddress, view_key=None):
                self._address = address(subaddress)
                self._svk = view_key or self._svk

            def view_key(self):
                return self._svk

            def accounts(self):
                return [Account(self, 0)]

            def addresses(self, account=0, addr_indices=None):
                return [self._address]

        return MoneroWallet(
            backend=SubaddressViewWallet(
                subaddress=self.address,
                view_key=self.secret_view_key
            )
        )

    def decentralization_adjusted_since(self):
        # Future transactions (blocks) may have past timestamps due to decentralized, permissionless mining:
        # https://monero.stackexchange.com/questions/3300/timestamp-question/3377#3377
        #
        # Assuming most miners use honest time, we believe the difference between block timestamp and honest clock
        # shouldn't be more than 60 blocks worth of time or 120 minutes.
        return self.since - timedelta(minutes=120)
