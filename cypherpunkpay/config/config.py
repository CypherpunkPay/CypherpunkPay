import logging as log
import re

from typing import List, Dict

from cypherpunkpay.explorers.supported_explorers import SupportedExplorers
from cypherpunkpay.explorers.bitcoin.abs_block_explorer import AbsBlockExplorer
from cypherpunkpay.exceptions import UnsupportedCoin


class Config(object):

    class Invalid(Exception):
        pass

    _dict: dict

    def __init__(self, settings=None, env='test'):
        if settings:
            self._dict = settings
        else:
            self._dict = {}
        self._env = env

    def server(self) -> Dict:
        return self._dict.get('server', {})

    def db_file_path(self) -> str:
        return self._dict.get('db_file_path')

    def path_prefix(self) -> [str, None]:
        path_prefix = self._dict.get('path_prefix')
        # Normalize
        if path_prefix == '/' or not path_prefix:
            return
        if not path_prefix.startswith('/'):
            path_prefix = '/' + path_prefix
        if path_prefix.endswith('/'):
            path_prefix = path_prefix[0:-1]
        if path_prefix.count('/') > 1:
            log.error('The path_prefix cannot be nested. Please use a flat path like the default /cypherpunkpay')
            exit(1)
        return path_prefix

    def btc_account_xpub(self) -> str:
        if self.btc_mainnet():
            return self._dict.get('btc_mainnet_account_xpub')
        else:
            return self._dict.get('btc_testnet_account_xpub')

    def xmr_secret_view_key(self) -> str:
        if self.xmr_mainnet():
            return self._dict.get('xmr_mainnet_secret_view_key')
        else:
            return self._dict.get('xmr_stagenet_secret_view_key')

    def xmr_main_address(self) -> str:
        if self.xmr_mainnet():
            return self._dict.get('xmr_mainnet_main_address')
        else:
            return self._dict.get('xmr_stagenet_main_address')

    def charge_payment_timeout_in_minutes(self) -> int:
        return int(self._dict.get('charge_payment_timeout_in_minutes', 15))

    def charge_payment_timeout_in_milliseconds(self) -> int:
        return self.charge_payment_timeout_in_minutes() * 60 * 1000

    def charge_completion_timeout_in_hours(self) -> int:
        return int(self._dict.get('charge_completion_timeout_in_hours', 48))

    def charge_completion_timeout_in_milliseconds(self) -> int:
        return self.charge_completion_timeout_in_hours() * 60 * 60 * 1000

    def btc_node_enabled(self) -> bool:
        if self.btc_mainnet():
            return self._dict.get('btc_mainnet_node_enabled', 'false') == 'true'
        else:
            return self._dict.get('btc_testnet_node_enabled', 'false') == 'true'

    def btc_node_rpc_url(self) -> str:
        if self.btc_mainnet():
            return self._dict.get('btc_mainnet_node_rpc_url', 'http://127.0.0.1:8332')
        else:
            return self._dict.get('btc_testnet_node_rpc_url', 'http://127.0.0.1:18332')

    def btc_node_rpc_user(self) -> str:
        if self.btc_mainnet():
            return self._dict.get('btc_mainnet_node_rpc_user', 'bitcoin')
        else:
            return self._dict.get('btc_testnet_node_rpc_user', 'bitcoin')

    def btc_node_rpc_password(self) -> str:
        if self.btc_mainnet():
            return self._dict.get('btc_mainnet_node_rpc_password', 'secret')
        else:
            return self._dict.get('btc_testnet_node_rpc_password', 'secret')

    def xmr_node_enabled(self) -> bool:
        if self.xmr_mainnet():
            return self._dict.get('xmr_mainnet_node_enabled', 'false') == 'true'
        else:
            return self._dict.get('xmr_stagenet_node_enabled', 'false') == 'true'

    def btc_network(self):
        return self._dict.get('btc_network', 'testnet')

    def xmr_network(self):
        return self._dict.get('xmr_network', 'stagenet')

    def cc_network(self, cc: str):
        if cc.casefold() == 'btc':
            return self.btc_network()
        if cc.casefold() == 'xmr':
            return self.xmr_network()
        raise UnsupportedCoin(cc)

    def btc_mainnet(self):
        return self.btc_network() == 'mainnet'

    def btc_testnet(self):
        return self.btc_network() == 'testnet'

    def xmr_mainnet(self):
        return self.xmr_network() == 'mainnet'

    def xmr_stagenet(self):
        return self.xmr_network() == 'stagenet'

    def supported_coins(self) -> List[str]:
        return ['btc', 'xmr']

    def supported_explorers(self, coin: str) -> List[AbsBlockExplorer]:
        return SupportedExplorers().get(coin, self.cc_network(coin))

    @staticmethod
    def supported_fiats() -> List[str]:
        # 'nzd'
        return [
            'usd',
            'eur', 'cny', 'gbp',
            'aud', 'brl', 'cad', 'chf', 'czk', 'inr', 'jpy', 'krw', 'mxn', 'pln', 'rub', 'zar'
        ]

    @staticmethod
    def supported_themes() -> List[str]:
        return ['plain', 'entertainment']

    def configured_coins(self) -> List[str]:
        ret = []
        if self.btc_account_xpub():
            ret.append('btc')
        if self.xmr_secret_view_key() and self.xmr_main_address():
            ret.append('xmr')
        return ret

    def supported_currencies(self) -> List[str]:
        return self.supported_coins() + self.supported_fiats()

    # Tor

    def use_tor(self) -> bool:
        return self._dict.get('use_tor', 'true') == 'true'

    def tor_socks5_host(self) -> str:
        return self._dict.get('tor_socks5_host', '127.0.0.1')

    def tor_socks5_port(self) -> int:
        return int(self._dict.get('tor_socks5_port', 9050))

    # Donations

    def donations_enabled(self) -> bool:
        return self._dict.get('donations_enabled', 'false') == 'true'

    def donations_cause(self) -> str:
        cause = self._dict.get('donations_cause', None)
        return cause or None  # convert '' to None

    def theme(self) -> str:
        theme = self._dict.get('theme', 'plain')
        if theme not in self.supported_themes():
            log.error(f'Unsupported theme in your config file. Pick one of {self.supported_themes()}')
            exit(1)
        return theme

    def donations_fiat_currency(self) -> str:
        s = self._dict.get('donations_fiat_currency', 'usd').strip().casefold()
        if s not in self.supported_fiats():
            log.error(f'Unsupported donations_fiat_currency in your config file. Pick one of {self.supported_fiats()}')
            exit(1)
        return s

    def donations_fiat_amounts(self) -> List[str]:
        s = self._dict.get('donations_fiat_amounts', '[25, 75, 125, 250, 500]').strip()
        if not re.match(r'^\[[\d,\s]*\]$', s):   # highly imperfect, just a sanity check!
            log.error('Incorrect value for config entry donations_fiat_amounts.')
            exit(1)
        return eval(s)

    # Merchant

    def merchant_enabled(self) -> bool:
        return self._dict.get('merchant_enabled', 'false') == 'true'

    def payment_completed_notification_url(self) -> str:
        return self._dict.get('payment_completed_notification_url', None)

    def payment_failed_notification_url(self) -> str:
        return self._dict.get('payment_failed_notification_url', None)

    def back_to_merchant_url(self) -> str:
        return self._dict.get('back_to_merchant_url', None)

    def cypherpunkpay_to_merchant_auth_token(self) -> str:
        return self._dict.get('cypherpunkpay_to_merchant_auth_token', None)

    def merchant_to_cypherpunkpay_auth_token(self) -> str:
        return self._dict.get('merchant_to_cypherpunkpay_auth_token', None)

    def skip_tor_for_merchant_callbacks(self) -> bool:
        return self._dict.get('skip_tor_for_merchant_callbacks', 'false') == 'true'

    # Admin

    def admin_panel_enabled(self) -> bool:
        return self._dict.get('admin_panel_enabled', 'false') == 'true'

    # Dummy Store

    def dummystore_enabled(self) -> bool:
        return self._dict.get('dummystore_enabled', 'false') == 'true'

    def btc_lightning_enabled(self) -> bool:
        return self._dict.get('btc_lightning_enabled', 'false') == 'true'

    def btc_lightning_lnd_url(self) -> bool:
        return self._dict.get('btc_lightning_lnd_url', 'https://127.0.0.1:8081/')

    def btc_lightning_lnd_invoice_macaroon(self) -> str:
        return self._dict.get('btc_lightning_lnd_invoice_macaroon', None)

    # Environments

    def test_env(self):
        return self._env == 'test'

    def dev_env(self):
        return self._env == 'dev'

    def prod_env(self):
        return self._env == 'prod'

    # Private

    def _verify_enum(self, param: str, acceptable: List[str], default: str) -> str:
        value = self._dict.get(param, default)
        if value not in acceptable:
            raise Config.Invalid(f"{param} should be one of {acceptable}")
        return value
