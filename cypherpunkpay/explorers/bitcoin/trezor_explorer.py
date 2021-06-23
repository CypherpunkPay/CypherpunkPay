from cypherpunkpay.common import *
from cypherpunkpay.explorers.bitcoin.abs_block_explorer import AbsBlockExplorer
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit


class TrezorExplorer(AbsBlockExplorer):
    # https://github.com/trezor/blockbook/blob/master/docs/api.md

    # Returns None on any error
    def get_height(self) -> [int, None]:
        parsed_json = self.http_get_json_or_None_on_error_while_accepting_linkability(f'{self.api_endpoint()}/bestHeight')
        if parsed_json is not None:
            height = parsed_json.get('blockbook', {}).get('bestHeight')
            try:
                return int(height)
            except ValueError as e:
                log.debug(f'Cant parse "{height}" as int')

    # Returns None on any error
    def get_address_credits(self, address: str, current_height: int) -> [AddressCredits, None]:
        json_dict = self.http_get_json_or_None_on_error(
            url=f'{self.api_endpoint()}/address/{address}?details=txs',
            privacy_context=address
        )
        if json_dict is not None:
            credits = []
            for tx_json in json_dict.get('transactions', []):
                credits.extend(self._credits_from_relevant_tx_outs(address, tx_json))
            return AddressCredits(credits, current_height)

    def _credits_from_relevant_tx_outs(self, address, tx_json):
        credits = []
        confirmed_height = tx_json.get('blockHeight', None)
        if confirmed_height == -1:
            confirmed_height = None
        inputs = tx_json['vin']
        outputs = tx_json['vout']

        # See: https://bitcoin.stackexchange.com/questions/55112/what-is-the-recomended-sequence-for-signalling-rbf
        is_rbf = any(filter(lambda i: i['sequence'] < 0xfffffffe, inputs))

        for output in outputs:
            if 'addresses' in output.keys():
                if address in output['addresses']:
                    credit = Credit(value=Decimal(output['value']) / 10**8, confirmed_height=confirmed_height, has_replaceable_flag=is_rbf)
                    credits.append(credit)

        return credits

    def api_endpoint(self) -> str:
        if self.mainnet():
            return 'https://btc3.trezor.io/api/v2'
        else:
            return 'https://tbtc2.trezor.io/api/v2'
