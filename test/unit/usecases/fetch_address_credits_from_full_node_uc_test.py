from test.unit.db_test_case import CypherpunkpayDBTestCase


class FetchAddressCreditsFromFullNodeUCTest(CypherpunkpayDBTestCase):

    # No need for a test because FetchAddressCreditsFromFullNodeUC is just a pass through class,
    # existing primarily for layer consistency. It really only does the coin-to-node dispatch.
    # See tests for BitcoinCoreClient, etc.
    pass
