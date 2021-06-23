import random
import importlib

from cypherpunkpay import App, Config
from cypherpunkpay.common import *
from cypherpunkpay.models.charge import Charge
from cypherpunkpay.net.http_client.dummy_http_client import DummyHttpClient
from cypherpunkpay.usecases import UseCase


class EnsureBlockExplorersUC(UseCase):

    charge: Charge

    DISCREPANCIES_THRESHOLD = 10

    def __init__(self, charge: Charge, config: Config):
        assert charge.cc_currency is not None
        self.charge = charge
        self._config = config if config else App().config()

    # Returns True if chaged, False otherwise
    def exec(self) -> bool:

        # No block explorers assigned (initial scenario)
        if self.charge.block_explorer_1 is None or \
                self.charge.block_explorer_2 is None:
            self.assign_random_block_explorers()
            return True

        # The pair of block explorers failed too many times for whatever reason
        if self.charge.subsequent_discrepancies >= self.DISCREPANCIES_THRESHOLD:
            # If by chance exactly the same block explorers as previously get picked, we consider it okay
            # This is to make sure CypherpunkPay will still work with only two block explorers available in configuration
            self.assign_random_block_explorers()
            return True

        # Changes or refactorings of available block explorers can render database module/klass paths not instantiable
        # In this case we need to pick a new pair
        if not self.is_valid(self.charge.block_explorer_1) or \
                not self.is_valid(self.charge.block_explorer_2):
            self.assign_random_block_explorers()
            return True

        # No changes made to block explorers pair
        return False

    def assign_random_block_explorers(self):
        if self.charge.subsequent_discrepancies >= self.DISCREPANCIES_THRESHOLD:
            log.info(f'Picking new block explorers for charge={self.charge.short_uid()} as existing ones did not agree {self.DISCREPANCIES_THRESHOLD} times in a row. This may happen if one block explorer is temporarily unavailable, delayed, buggy or malicious.')
        self.charge.block_explorer_1 = self.random_module_klass_name()
        self.charge.block_explorer_2 = self.random_module_klass_name(forbidden=self.charge.block_explorer_1)
        self.charge.subsequent_discrepancies = 0

    def random_module_klass_name(self, forbidden=None) -> str:
        available_explorers = self._config.supported_explorers(self.charge.cc_currency)
        klass = random.choice(available_explorers)
        candidate = klass.__module__ + ' ' + klass.__name__
        if candidate == forbidden:
            return self.random_module_klass_name(forbidden=forbidden)
        return candidate

    def is_valid(self, module_klass) -> bool:
        module_name, klass_name = module_klass.split()
        try:
            # This is just a test instantiation to ensure module/klass are valid
            module = importlib.import_module(module_name)
            klass = getattr(module, klass_name)
            klass(http_client=DummyHttpClient())
            return True
        except Exception:
            log.info(f'Picking new block explorers for charge={self.charge.short_uid()} as cannot instantiate {module_name}/{klass_name}. This may happen after CypherpunkPay upgrade.')
            return False
