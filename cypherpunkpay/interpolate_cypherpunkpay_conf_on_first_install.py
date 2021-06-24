from cypherpunkpay import bitcoin
from pathlib import Path

from cypherpunkpay.tools.safe_uid import SafeUid


def main():
    cypherpunkpay_conf = '/etc/cypherpunkpay.conf'
    discard = '/var/lib/cypherpunkpay/can-discard'

    if Path(cypherpunkpay_conf).exists():
        changed = False

        # Load config
        with open(cypherpunkpay_conf, 'r') as file:
            filedata = file.read()

        # Generate example testnet wallet
        marker = '# btc_testnet_account_xpub = REPLACE_ME_WITH_BTC_TESTNET_ACCOUNT_XPUB'
        if marker in filedata:
            print(f'Writing example testnet wallet to {cypherpunkpay_conf} [wallets] btc_testnet_account_xpub = ...')
            xprv, xpub = bitcoin.Bip32.generate_testnet_p2wpkh_wallet()
            filedata = filedata.replace(marker, f'btc_testnet_account_xpub = {xpub}')
            if Path(discard).exists():
                with open(f'{discard}/example_btc_testnet_xprv', 'w') as file_xprv:
                    file_xprv.write('# Example BTC testnet private key generated during installation (can be safely discarded)\n\n')
                    file_xprv.write(f'{xprv}\n')
            changed = True

        # Generate high entropy cypherpunkpay_to_merchant_auth_token
        marker = 'REPLACE_ME_WITH_CYPHERPUNKPAY_TO_MERCHANT_AUTH_TOKEN'
        if marker in filedata:
            token = SafeUid.gen(32)
            filedata = filedata.replace(marker, token)
            changed = True

        # Generate high entropy cypherpunkpay_to_merchant_auth_token
        marker = 'REPLACE_ME_WITH_MERCHANT_TO_CYPHERPUNKPAY_AUTH_TOKEN'
        if marker in filedata:
            token = SafeUid.gen(32)
            filedata = filedata.replace(marker, token)
            changed = True

        # Save
        if changed:
            with open(cypherpunkpay_conf, 'w') as file:
                file.write(filedata)
