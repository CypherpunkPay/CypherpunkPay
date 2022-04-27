from cypherpunkpay.config.config import Config


class ExampleConfig(Config):

    def btc_account_xpub(self):
        return 'vpub5UtSQhMcYBgGe3UxC5suwHbayv9Xw2raS9U4kyv5pTrikTNGLbxhBdogWm8TffqLHZhEYo7uBcouPiFQ8BNMP6JFyJmqjDxxUyToB1RcToF'

    def xmr_main_address(self) -> str:
        # Monero donations primary address, see https://web.getmonero.org/get-started/contributing/
        return '44AFFq5kSiGBoZ4NMDwYtN18obc8AemS33DBLWs3H7otXft3XjrpDtQGv7SqSsaBYBb98uNbr2VBBEt7f2wfn3RVGQBEP3A'

    def xmr_secret_view_key(self) -> str:
        # Monero donations secret view key, see https://web.getmonero.org/get-started/contributing/
        return 'f359631075708155cc3d92a32b75a7d02a5dcf27756707b47a2b31b21c389501'

    def btc_network(self):
        return 'testnet'

    def xmr_network(self):
        return 'stagenet'

    def merchant_enabled(self):
        return True

    def payment_completed_notification_url(self):
        return 'http://127.0.0.1:6543/cypherpunkpay/dummystore/cypherpunkpay_payment_completed'

    def back_to_merchant_url(self):
        return 'http://127.0.0.1:6543/cypherpunkpay/dummystore/order/{merchant_order_id}'

    def cypherpunkpay_to_merchant_auth_token(self):
        return 'nsrzukv53xjhmw4w5ituyk5cre'
