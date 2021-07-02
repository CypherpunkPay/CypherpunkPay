from test.unit.config.example_config import ExampleConfig
from cypherpunkpay.common import *
from test.unit.db_test_case import CypherpunkpayDBTestCase
from cypherpunkpay.models.charge import ExampleCharge
from cypherpunkpay.usecases.ensure_block_explorers_uc import EnsureBlockExplorersUC


class EnsureBlockExplorersUCTest(CypherpunkpayDBTestCase):

    def test_assigns_explorers_to_new_charge(self):
        charge = ExampleCharge.create()

        EnsureBlockExplorersUC(charge, config=ExampleConfig()).exec()

        self.assertIsNotNone(charge.block_explorer_1)
        self.assertIsNotNone(charge.block_explorer_2)
        self.assertTrue(charge.block_explorer_1.startswith('cypherpunkpay.'))
        self.assertTrue(charge.block_explorer_2.startswith('cypherpunkpay.'))
        self.assertTrue(charge.block_explorer_1.endswith('Explorer'))
        self.assertTrue(charge.block_explorer_2.endswith('Explorer'))

    def test_does_not_change_fine_explorers(self):
        charge = ExampleCharge.create()
        charge.block_explorer_1 = 'cypherpunkpay.explorers.bitcoin.mempool_explorer MempoolExplorer'
        charge.block_explorer_2 = 'cypherpunkpay.explorers.bitcoin.blockstream_explorer BlockstreamExplorer'
        charge.subsequent_discrepancies = 9  # below threshold

        EnsureBlockExplorersUC(charge, config=ExampleConfig()).exec()

        self.assertEqual('cypherpunkpay.explorers.bitcoin.mempool_explorer MempoolExplorer', charge.block_explorer_1)
        self.assertEqual('cypherpunkpay.explorers.bitcoin.blockstream_explorer BlockstreamExplorer', charge.block_explorer_2)

    def test_resets_explorers_if_subsequent_discrepancies_reached_threshold(self):
        good_luck = 0
        for i in range(100):
            charge = ExampleCharge.create()
            charge.block_explorer_1 = 'cypherpunkpay.explorers.bitcoin.mempool_explorer MempoolExplorer'
            charge.block_explorer_2 = 'cypherpunkpay.explorers.bitcoin.blockstream_explorer BlockstreamExplorer'
            charge.subsequent_discrepancies = 10

            EnsureBlockExplorersUC(charge, config=ExampleConfig()).exec()

            both_new = charge.block_explorer_1 != 'cypherpunkpay.explorers.bitcoin.mempool_explorer MempoolExplorer' and \
                charge.block_explorer_2 != 'cypherpunkpay.explorers.bitcoin.blockstream_explorer BlockstreamExplorer'

            if both_new:
                good_luck += 1

        # Most of the time both explorers should be reset
        assert good_luck > 50

    def test_resets_explorers_if_cannot_instantiate(self):
        good_luck = 0
        for i in range(50):
            charge = ExampleCharge.create()
            charge.block_explorer_1 = 'cypherpunkpay.explorers.bitcoin.mempool_explorer MempoolExplorer'
            charge.block_explorer_2 = 'cypherpunkpay.explorers.bitcoin.incorrect_explorer IncorrectExplorer'

            EnsureBlockExplorersUC(charge, config=ExampleConfig()).exec()
            log.info(charge.block_explorer_1)
            log.info(charge.block_explorer_2)

            both_new = charge.block_explorer_1 != 'cypherpunkpay.explorers.bitcoin.mempool_explorer MempoolExplorer' and \
                charge.block_explorer_2 != 'cypherpunkpay.explorers.bitcoin.blockstream_explorer BlockstreamExplorer'

            if both_new:
                good_luck += 1

        # Most of the time both explorers should be reset
        self.assertGreater(good_luck, 25)
