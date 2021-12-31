import hashlib
from abc import ABC

from monero.backends.offline import OfflineWallet
from monero.wallet import Wallet

from cypherpunkpay import bitcoin
from cypherpunkpay.bitcoin import Bip32
from cypherpunkpay.exceptions import UnsupportedCoin
from cypherpunkpay.usecases import UseCase


class BaseChargeUC(UseCase, ABC):

    def next_unused_address(self, cc_currency):
        if cc_currency == 'btc':
            xpub = self.config.btc_account_xpub()
            wallet_fingerprint = Bip32.wallet_fingerprint(xpub)
            address_index = self.db.count_charges_where_wallet_fingerprint_is(wallet_fingerprint)
            address = bitcoin.Bip32.p2wpkh_address_at(self.config.btc_network(), xpub, [0, address_index])
        elif cc_currency == 'xmr':
            main_address = self.config.xmr_main_address()
            secret_view_key = self.config.xmr_secret_view_key()
            wallet_fingerprint = self._hash_as_hex(secret_view_key.encode())
            address_index = self.db.count_charges_where_wallet_fingerprint_is(wallet_fingerprint)
            address = str(Wallet(OfflineWallet(main_address, view_key=secret_view_key)).get_address(0, address_index))
        else:
            raise UnsupportedCoin(cc_currency)

        return wallet_fingerprint, address_index, address

    def _hash_as_hex(self, source_bytes: bytes):
        return hashlib.sha256(source_bytes).hexdigest()
