from typing import Union, Iterable

from cypherpunkpay.common import *
from cypherpunkpay.bitcoin.electrum.constants import BitcoinMainnet, BitcoinTestnet, AbstractNet
from cypherpunkpay.bitcoin.electrum.bitcoin import public_key_to_p2wpkh_addr, InvalidChecksum
from cypherpunkpay.bitcoin.electrum.bip32 import BIP32Node
from cypherpunkpay.bitcoin.electrum.util import BitcoinException

from cypherpunkpay.bitcoin.electrum.crypto import hash_160


class Bip32:

    @classmethod
    def validate_p2wpkh_xpub(cls, network: str, btc_account_xpub: str):
        prefix = btc_account_xpub[0:4]
        if network == 'mainnet':
            # Check zpub
            if prefix not in ['xpub', 'zpub']:
                return f'Only P2WPKH wallets are supported. Paste your wallet xpub or zpub as btc_mainnet_account_xpub value in your /etc/cypherpunkpay.conf [wallets] section.'
            # Check checksum and syntax
            try:
                BIP32Node.from_xkey(btc_account_xpub, net=BitcoinMainnet)
            except (InvalidChecksum, BitcoinException, ValueError) as e:
                return f'Malformed mainnet xpub for Bitcoin wallet ({e}). Paste your wallet xpub or zpub as btc_mainnet_account_xpub value in your /etc/cypherpunkpay.conf [wallets] section.'

        if network == 'testnet':
            # Check tpub or vpub
            if prefix not in ['tpub', 'vpub']:
                return f'Only P2WPKH wallets are supported. Paste your wallet tpub OR vpub as btc_testnet_account_xpub value in your /etc/cypherpunkpay.conf [wallets] section.'
            # Check checksum and syntax
            try:
                BIP32Node.from_xkey(btc_account_xpub, net=BitcoinTestnet)
            except (InvalidChecksum, BitcoinException, ValueError) as e:
                return f'Malformed testnet xpub for Bitcoin wallet ({e}). Paste your wallet tpub OR vpub as btc_testnet_account_xpub value in your /etc/cypherpunkpay.conf [wallets] section.'

        return {}

    @classmethod
    def p2wpkh_address_at(cls, network: str, btc_account_xpub: str, sequence: Union[str, Iterable[int]]):
        if network == 'mainnet':
            network_class = BitcoinMainnet
        elif network == 'testnet':
            network_class = BitcoinTestnet
        else:
            raise Exception(f'Invalid BTC network {network}')

        pubkey_bytes = cls._pubkey_at(network_class, btc_account_xpub, sequence)
        p2wpkh_addr = public_key_to_p2wpkh_addr(pubkey_bytes, net=network_class)
        return p2wpkh_addr

    @staticmethod
    def generate_testnet_p2wpkh_wallet() -> (str, str):
        import secrets
        private_key_bytes = secrets.token_bytes(32)
        bip32node = BIP32Node.from_rootseed(seed=private_key_bytes, xtype='p2wpkh')
        xprv = bip32node.to_xprv(net=BitcoinTestnet)
        xprv = 'v' + xprv[1:]
        xpub = bip32node.to_xpub(net=BitcoinTestnet)
        xpub = 'v' + xpub[1:]
        return xprv, xpub

    @staticmethod
    # zpub => xpub
    # vpub => tpub
    def to_standard_xpub(slip132_xpub: str) -> str:
        net = Bip32._electrum_net_for_xpub(slip132_xpub)
        node = BIP32Node.from_xkey(slip132_xpub, net=net)
        return node._replace(xtype='standard').to_xkey(net=net)

    @staticmethod
    def wallet_fingerprint(xpub: str) -> str:
        return Bip32._wallet_fingerprint_bytes(xpub).hex()

    @staticmethod
    def _wallet_fingerprint_bytes(xpub: str) -> bytes:
        standard_xpub = Bip32.to_standard_xpub(xpub)
        net = Bip32._electrum_net_for_xpub(standard_xpub)
        node = BIP32Node.from_xkey(standard_xpub, net=net)
        return hash_160(node.eckey.get_public_key_bytes(compressed=True))[0:8]  # do not change this length

    @staticmethod
    def _electrum_net_for_xpub(xpub: str) -> AbstractNet:
        if xpub[0] in 'xXyYzZ':
            return BitcoinMainnet
        elif xpub[0] in 'tTuUvV':
            return BitcoinTestnet

    @staticmethod
    def _pubkey_at(network_class: type, btc_account_xpub: str, sequence: Union[str, Iterable[int]]) -> bytes:
        account_node = BIP32Node.from_xkey(btc_account_xpub, net=network_class)
        pubkey_node = account_node.subkey_at_public_derivation(sequence)  # [84, 0, 0, 0, 0]
        return pubkey_node.eckey.get_public_key_bytes(compressed=True)
