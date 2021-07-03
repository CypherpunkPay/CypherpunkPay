from cypherpunkpay.bitcoin.electrum.constants import BitcoinMainnet, BitcoinTestnet


def btc_network_class(network_name):
    if network_name == 'mainnet':
        return BitcoinMainnet
    elif network_name == 'testnet':
        return BitcoinTestnet


def is_testnet_address(address: str):
    # See: https://en.bitcoin.it/wiki/List_of_address_prefixes
    return \
        address.startswith('tb1') or \
        address.startswith('2') or \
        address.startswith('m') or \
        address.startswith('n')


def is_mainnet_address(address: str):
    return not is_testnet_address(address)
