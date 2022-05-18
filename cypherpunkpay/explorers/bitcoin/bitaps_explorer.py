from cypherpunkpay.globals import *
from cypherpunkpay.explorers.bitcoin.block_explorer import BlockExplorer
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit


class BitapsExplorer(BlockExplorer):

    # Returns None on any error
    def get_height(self) -> [int, None]:
        parsed_json = self.http_get_json_or_None_on_error_while_accepting_linkability(f'{self.api_endpoint()}/block/last')
        if parsed_json is not None:
            height = parsed_json.get('data', {}).get('height')
            try:
                return int(height)
            except ValueError as e:
                log.debug(f'Cant parse "{height}" as int')

    # Returns None on any error
    def get_address_credits(self, address: str, current_height: int) -> [AddressCredits, None]:
        json_dict_unconfirmed = self.http_get_json_or_None_on_error(
            url=f'{self.api_endpoint()}/address/unconfirmed/transactions/{address}',
            privacy_context=address
        )
        json_dict_confirmed = self.http_get_json_or_None_on_error(
            url=f'{self.api_endpoint()}/address/transactions/{address}',
            privacy_context=address
        )
        if json_dict_unconfirmed is not None and json_dict_confirmed is not None:
            json_dict = deep_dict_merge(json_dict_unconfirmed, json_dict_confirmed)
            credits = []
            for tx_json in json_dict['data']['list']:
                credits.extend(self._credits_from_relevant_tx_outs(address, tx_json))
            return AddressCredits(credits, current_height)

    def _credits_from_relevant_tx_outs(self, address, tx_json):
        credits = []
        value = Decimal(tx_json['amount']) / 100_000_000
        if value > 0:
            confirmed_height = tx_json.get('blockHeight')
            is_rbf = tx_json.get('rbf')
            credit = Credit(value=value, confirmed_height=confirmed_height, has_replaceable_flag=is_rbf)
            credits.append(credit)
        return credits

    def api_endpoint(self):
        # The onion services for BitAps are misconfigured.
        # For rate limiting purposes the onion services merge together all incoming traffic (all IP addresses),
        # and we very soon hit the per-second limit, despite connecting from various IPs.
        #
        # That's why we use clearnet version of the API.
        if self.mainnet():
            return 'https://api.bitaps.com/btc/v1/blockchain'
        else:
            return 'https://api.bitaps.com/btc/testnet/v1/blockchain'


# This function was found on the Internet
def deep_dict_merge(*args, add_keys=True):
    assert len(args) >= 2, "dict_merge requires at least two dicts to merge"
    rtn_dct = args[0].copy()
    merge_dicts = args[1:]
    for merge_dct in merge_dicts:
        if add_keys is False:
            merge_dct = {key: merge_dct[key] for key in set(rtn_dct).intersection(set(merge_dct))}
        for k, v in merge_dct.items():
            from collections.abc import Mapping
            if not rtn_dct.get(k):
                rtn_dct[k] = v
            elif k in rtn_dct and type(v) != type(rtn_dct[k]):
                raise TypeError(f"Overlapping keys exist with different types: original is {type(rtn_dct[k])}, new value is {type(v)}")
            elif isinstance(rtn_dct[k], dict) and isinstance(merge_dct[k], Mapping):
                rtn_dct[k] = deep_dict_merge(rtn_dct[k], merge_dct[k], add_keys=add_keys)
            elif isinstance(v, list):
                for list_value in v:
                    if list_value not in rtn_dct[k]:
                        rtn_dct[k].append(list_value)
            else:
                rtn_dct[k] = v
    return rtn_dct
