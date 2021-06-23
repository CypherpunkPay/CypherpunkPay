from cypherpunkpay import bitcoin
from pathlib import Path


def main():
    cypherpunkpay_conf = '/etc/cypherpunkpay.conf'
    discard = '/var/lib/cypherpunkpay/can-discard'
    marker = '# btc_testnet_account_xpub = vpub......'

    if Path(cypherpunkpay_conf).exists():
        with open(cypherpunkpay_conf, 'r') as file:
            filedata = file.read()

        if marker in filedata:
            print(f'Writing example testnet wallet to {cypherpunkpay_conf} [wallets] btc_testnet_account_xpub = ...')
            xprv, xpub = bitcoin.Bip32.generate_testnet_p2wpkh_wallet()
            filedata = filedata.replace(marker, f'btc_testnet_account_xpub = {xpub}')
            with open(cypherpunkpay_conf, 'w') as file:
                file.write(filedata)
            if Path(discard).exists():
                with open(f'{discard}/example_btc_testnet_xprv', 'w') as file_xprv:
                    file_xprv.write('# Example BTC testnet private key generated during installation (can be safely discarded)\n\n')
                    file_xprv.write(f'{xprv}\n')
