import importlib

from cypherpunkpay.app import App
from cypherpunkpay.common import *
from cypherpunkpay.exceptions import UnsupportedCoin
from cypherpunkpay.explorers.bitcoin.abs_block_explorer import AbsBlockExplorer
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.usecases import UseCase


class FetchAddressCreditsFromExplorersUC(UseCase):

    def __init__(self, cc_currency: str, address: str, block_explorer_1: str, block_explorer_2: str, current_height=None, http_client=None, config=None, charge_short_uid=None):
        self.cc_currency = cc_currency
        self.address = address
        self.block_explorer_1_s = block_explorer_1
        self.block_explorer_2_s = block_explorer_2
        self.block_explorer_1 = None
        self.block_explorer_2 = None
        self.current_height = current_height if current_height is not None else App().current_blockchain_height('btc')
        self.http_client = http_client if http_client else App().http_client()
        self.config = config if config else App().config()
        self.charge_short_uid = charge_short_uid  # for logging only

    def exec(self) -> [AddressCredits, None]:
        if self.cc_currency == 'btc':
            self._instantiate_block_explorers()

            address_credits_1 = self.block_explorer_1.get_address_credits(address=self.address, current_height=self.current_height)
            address_credits_2 = self.block_explorer_2.get_address_credits(address=self.address, current_height=self.current_height)

            # Both explorers must give exactly the same answer
            if address_credits_1 == address_credits_2:
                return address_credits_1

            # Discrepancy between block explorers. This is natural temporarily.
            self._log_discrepancy(address_credits_1, address_credits_2)
            return None

        elif self.cc_currency == 'xmr':
            # TODO: implement
            # self._instantiate_block_explorers()
            return AddressCredits([], 0)
        else:
            raise UnsupportedCoin(self.cc_currency)

    def _instantiate_block_explorers(self):
        self.block_explorer_1 = self._instantiate_explorer(self.block_explorer_1_s)
        self.block_explorer_2 = self._instantiate_explorer(self.block_explorer_2_s)

    def _instantiate_explorer(self, module_klass: str) -> AbsBlockExplorer:
        module_name, klass_name = module_klass.split()
        module = importlib.import_module(module_name)
        klass: AbsBlockExplorer = getattr(module, klass_name)
        # noinspection PyCallingNonCallable
        return klass(http_client=self.http_client, btc_network=self.config.btc_network(), use_tor=self.config.use_tor())

    def _log_discrepancy(self, address_credits_1, address_credits_2):
        address_credits_1_s = f'{address_credits_1.__dict__}' if address_credits_1 else 'None'
        address_credits_2_s = f'{address_credits_2.__dict__}' if address_credits_2 else 'None'
        msg = 'D'
        if self.charge_short_uid:
            msg = f'Charge {self.charge_short_uid} d'
        msg += f'iscrepancy between block explorers (likely temporary)   {self._be1_name()} => {address_credits_1_s}   {self._be2_name()} => {address_credits_2_s}'
        log.info(msg)

    def _be1_name(self):
        return self.block_explorer_1_s.split()[-1]

    def _be2_name(self):
        return self.block_explorer_2_s.split()[-1]
