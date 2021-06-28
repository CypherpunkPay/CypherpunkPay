import argparse
import configparser
import logging
import os
import pkg_resources
from pathlib import Path

from cypherpunkpay import bitcoin
from cypherpunkpay.config.config import Config
from cypherpunkpay.monero.monero_wallet import MoneroWallet

log = logging.getLogger()


class ConfigParser(object):

    def __init__(self, env):
        self.env = env

    def from_user_conf_files(self):
        self.log_starting_cypherpunkpay_banner()
        user_config = self.parse_user_config_files()
        self.validate(user_config)
        return Config(user_config, env=self.env)

    def from_user_conf_files_and_cli_args(self):
        user_cli_args = self.parse_cli_args()
        self.log_starting_cypherpunkpay_banner()
        user_config = self.parse_user_config_files(user_cli_args)
        self.validate(user_config)
        return Config(user_config, env=self.env)

    def parse_cli_args(self):
        program = 'cypherpunkpay'
        version = pkg_resources.require("cypherpunkpay")[0].version
        description = 'CypherpunkPay is a webapp for accepting Bitcoin on clearnet and onion websites.'
        parser = argparse.ArgumentParser(
            prog=program,
            description=description,
            add_help=False)

        parser.add_argument(
            '--help', '-h', action='help', default='==SUPPRESS==', help='Show this help message and exit')
        parser.add_argument(
            '--version', '-v', action='version', version=f"%(prog)s {version}", help='Show program\'s version number and exit')
        parser.add_argument(
            '--config-file',
            type=str,
            dest='configs',
            metavar="FILE",
            action='append',
            help=("Configuration file path. "
                  "By default CypherpunkPay reads config file /etc/cypherpunkpay.conf followed by /etc/cypherpunkpay.d/*.conf"))

        return parser.parse_args()

    def parse_user_config_files(self, cli_overrides=None):
        cfg = configparser.ConfigParser()
        log.debug(f"Reading defaults from {self.internal_default_conf_path()}")
        cfg.read(self.internal_default_conf_path())

        paths = []
        must_exist = False

        if self.test_env():
            paths = [self.test_user_conf_path()]

        if self.dev_env():
            paths = [self.dev_user_conf_path()]

        if self.prod_env():
            if cli_overrides and cli_overrides.configs is not None:
                paths = cli_overrides.configs
                must_exist = True
            else:
                paths = self.prod_user_conf_paths()

        for path in paths:
            log.info(f"Reading config {path}")
            ok = cfg.read(path)
            if must_exist and not ok:
                log.error(f"Error reading {path} - check path and permissions")
                exit(1)

        partially_collapsed = {
            **cfg['wallets'],
            **cfg['donations'],
            **cfg['admin'],
            **cfg['full node'],
            **cfg['merchant'],
            **cfg['db'],
            **cfg['tor'],
            **cfg['expert']
        }
        if cfg.has_section('lightning-network'):
            partially_collapsed = { **partially_collapsed, **cfg['lightning-network'] }
        if cfg.has_section('dummystore'):
            partially_collapsed = { **partially_collapsed, **cfg['dummystore'] }
        partially_collapsed['server'] = cfg['server']

        return partially_collapsed

    def internal_default_conf_path(self):
        return os.path.join(os.path.dirname(__file__), '..', 'config', 'cypherpunkpay_defaults.conf')

    def test_user_conf_path(self):
        return os.path.join(os.path.dirname(__file__), '..', 'config', 'cypherpunkpay_test.conf')

    def dev_user_conf_path(self):
        return os.path.join(os.path.dirname(__file__), '..', 'config', 'cypherpunkpay_dev.conf')

    def prod_user_conf_paths(self):
        p = Path('/etc/')
        return list(p.glob('cypherpunkpay.conf')) + list(p.glob('cypherpunkpay.d/*.conf'))

    def test_env(self):
        return self.env == 'test'

    def dev_env(self):
        return self.env == 'dev'

    def prod_env(self):
        return self.env == 'prod'

    def validate(self, user_config):
        candidate = Config(user_config)
        if not candidate.configured_coins():
            log.error(f"No cryptocurrency wallets configured. Review /etc/cypherpunkpay.conf [wallets] section.")
            exit(1)
        else:
            for coin in candidate.configured_coins():
                error = None
                if coin == 'btc':
                    error = bitcoin.Bip32.validate_p2wpkh_xpub(candidate.btc_network(), candidate.btc_account_xpub())
                if coin == 'xmr':
                    error = MoneroWallet.validate_viewkey_mainaddress(candidate.xmr_network(), candidate.xmr_secret_view_key(), candidate.xmr_main_address())
                if error:
                    log.error(error)
                    exit(1)
                log.info(f'Found wallet config: {candidate.cc_network(coin)} {coin}')
        if candidate.merchant_enabled():
            if not candidate.payment_completed_notification_url():
                log.error(f'When merchant_enabled = true, you must provide valid payment_completed_notification_url. Review /etc/cypherpunkpay.conf [merchant] section.')
                exit(1)
            if not candidate.cypherpunkpay_to_merchant_auth_token():
                log.error(f'When merchant_enabled = true, you must provide cypherpunkpay_to_merchant_auth_token. Review /etc/cypherpunkpay.conf [merchant] section.')
                exit(1)
            if not candidate.back_to_merchant_url():
                log.warning(f'When merchant_enabled = true, you want to provide back_to_merchant_url. Review /etc/cypherpunkpay.conf [merchant] section.')

    def log_starting_cypherpunkpay_banner(self):
        env_info = ''
        if self.env == 'dev':
            env_info = ' in DEVELOPMENT environment'
        if self.env == 'test':
            env_info = ' in TEST environment'
        log.info(f"Starting CypherpunkPay {pkg_resources.require('cypherpunkpay')[0].version}{env_info}")
