from cypherpunkpay.common import *
from cypherpunkpay.explorers.bitcoin.abs_block_explorer import AbsBlockExplorer
from cypherpunkpay.models.address_credits import AddressCredits
from cypherpunkpay.models.credit import Credit


class AbsEsploraExplorer(AbsBlockExplorer):

    # Returns None on any error
    def get_height(self) -> [int, None]:
        text_height = self.http_client.get_text_or_None_on_error_while_accepting_linkability(f'{self.api_endpoint()}/blocks/tip/height')
        if text_height is not None:
            try:
                return int(text_height)
            except ValueError as e:
                log.debug(f'Cannot parse "{text_height}" as int')

    # Returns None on any error
    def get_address_credits(self, address: str, current_height: int) -> [AddressCredits, None]:
        json_dict = self.http_get_json_or_None_on_error(
            url=f'{self.api_endpoint()}/address/{address}/txs',
            privacy_context=address
        )
        if json_dict is not None:
            credits = []
            for tx_json in json_dict:
                credits.extend(self._credits_from_relevant_tx_outs(address, tx_json))
            return AddressCredits(credits, current_height)

    def _credits_from_relevant_tx_outs(self, address, tx_json):
        credits = []
        confirmed_height = tx_json['status'].get('block_height')
        inputs = tx_json['vin']
        outputs = tx_json['vout']

        # See: https://bitcoin.stackexchange.com/questions/55112/what-is-the-recomended-sequence-for-signalling-rbf
        is_rbf = any(filter(lambda input: input['sequence'] < 0xfffffffe, inputs))

        for output in outputs:
            if 'scriptpubkey_address' in output.keys():
                if output['scriptpubkey_address'] == address:
                    credit = Credit(value=Decimal(output['value']) / 10**8, confirmed_height=confirmed_height, has_replaceable_flag=is_rbf)
                    credits.append(credit)

        return credits
