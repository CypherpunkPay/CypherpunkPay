from cypherpunkpay.bitcoin import Bip32
from cypherpunkpay.common import *
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit
from cypherpunkpay.net.http_client.base_http_client import BaseHttpClient
from cypherpunkpay.full_node_clients.json_rpc_client import JsonRpcClient


class BitcoinCoreClient(object):

    _json_rpc_client: JsonRpcClient = None

    def __init__(self, url: str, rpc_user: str, rpc_password: str, http_client: BaseHttpClient):
        self._json_rpc_client = JsonRpcClient(url, user=rpc_user, passwd=rpc_password, http_client=http_client)

    def get_height(self) -> int:
        return self._json_rpc_client.getblockcount()

    def create_wallet_idempotent(self, xpub, rescan_since: int = None):
        wallet_name = self.wallet_name_from_xpub(xpub)
        wallet_path = f'/wallet/{wallet_name}'
        if rescan_since is None:
            # this default value slightly more than 550 blocks (which is pruned node default history memory)
            rescan_since = int(utc_ago(days=4).timestamp())

        # https://developer.bitcoin.org/reference/rpc/listwallets.html
        existing_wallets = self._json_rpc_client.listwallets()

        if wallet_name not in existing_wallets:
            log.info("Creating watch only wallet on your Bitcoin Core...")
            # https://developer.bitcoin.org/reference/rpc/createwallet.html
            self._json_rpc_client.createwallet(wallet_name, True, True, None, False, True, True)

        # https://developer.bitcoin.org/reference/rpc/getwalletinfo.html
        wallet_info = self._json_rpc_client.getwalletinfo(wallet_path)

        if wallet_info['txcount'] == 0:
            log.info("Importing wallet descriptor to your Bitcoin Core wallet...")

            # https://developer.bitcoin.org/reference/rpc/getdescriptorinfo.html
            standard_xpub = Bip32.to_standard_xpub(xpub)
            result = self._json_rpc_client.getdescriptorinfo(f'wpkh({standard_xpub}/0/*)')
            checksum = result['checksum']

            # https://developer.bitcoin.org/reference/rpc/importdescriptors.html
            self._json_rpc_client.importdescriptors(
                {
                    "requests":
                        [
                            {
                                "desc": f"wpkh({standard_xpub}/0/*)#{checksum}",
                                "timestamp": rescan_since,
                                "watchonly": True,
                                "internal": False,
                                "active": True,
                                "range": [0, 256]
                            }
                        ]
                },
                wallet_path
            )

        log.info(f'Successfully connected to Bitcoin Core wallet ({wallet_name})')

    def get_address_credits(self, wallet_fingerprint: str, address: str, current_height: int) -> [AddressCredits, None]:
        wallet_name = self.wallet_name_from_fingerprint(wallet_fingerprint)
        wallet_path = f'/wallet/{wallet_name}'

        # This is a dirty hack due to listreceivedbyaddress not working for descriptor wallets in Bitcoin Core 0.21

        total_6_plus = self._json_rpc_client.getreceivedbyaddress(address, 6, wallet_path)
        total_5_plus = self._json_rpc_client.getreceivedbyaddress(address, 5, wallet_path)
        total_4_plus = self._json_rpc_client.getreceivedbyaddress(address, 4, wallet_path)
        total_3_plus = self._json_rpc_client.getreceivedbyaddress(address, 3, wallet_path)
        total_2_plus = self._json_rpc_client.getreceivedbyaddress(address, 2, wallet_path)
        total_1_plus = self._json_rpc_client.getreceivedbyaddress(address, 1, wallet_path)
        total_0_plus = self._json_rpc_client.getreceivedbyaddress(address, 0, wallet_path)

        total_6 = total_6_plus
        total_5 = total_5_plus - total_6_plus
        total_4 = total_4_plus - total_5_plus
        total_3 = total_3_plus - total_4_plus
        total_2 = total_2_plus - total_3_plus
        total_1 = total_1_plus - total_2_plus
        total_0 = total_0_plus - total_1_plus

        # log.info(f'total_6={total_6}')
        # log.info(f'total_5={total_5}')
        # log.info(f'total_4={total_4}')
        # log.info(f'total_3={total_3}')
        # log.info(f'total_2={total_2}')
        # log.info(f'total_1={total_1}')
        # log.info(f'total_0={total_0}')

        credits = []
        if total_0 > 0:
            credits.append(Credit(total_0, confirmed_height=None, has_replaceable_flag=True))
        if total_1 > 0:
            credits.append(Credit(total_1, confirmed_height=current_height, has_replaceable_flag=True))
        if total_2 > 0:
            credits.append(Credit(total_2, confirmed_height=current_height-1, has_replaceable_flag=True))
        if total_3 > 0:
            credits.append(Credit(total_3, confirmed_height=current_height-2, has_replaceable_flag=True))
        if total_4 > 0:
            credits.append(Credit(total_4, confirmed_height=current_height-3, has_replaceable_flag=True))
        if total_5 > 0:
            credits.append(Credit(total_5, confirmed_height=current_height-4, has_replaceable_flag=True))
        if total_6 > 0:
            credits.append(Credit(total_6, confirmed_height=current_height-5, has_replaceable_flag=True))

        address_credits = AddressCredits(credits, current_height)

        return address_credits

    def wallet_name_from_fingerprint(self, fingerprint: str) -> str:
        return f'cypherpunkpay-wallet-{fingerprint}'

    def wallet_name_from_xpub(self, xpub: str) -> str:
        return self.wallet_name_from_fingerprint(Bip32.wallet_fingerprint(xpub))
