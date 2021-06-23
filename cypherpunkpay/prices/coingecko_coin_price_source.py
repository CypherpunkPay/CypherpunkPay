from decimal import Decimal

import json
import requests

from cypherpunkpay.prices.price_source import PriceSource


class CoingeckoCoinPriceSource(PriceSource):

    def get(self, coin: str, fiat: str) -> [Decimal, None]:
        if fiat != 'usd':
            raise Exception(f'Unsupported fiat {fiat}')
        try:
            parsed_json = self._http_client.get_accepting_linkability('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin%2Cmonero&vs_currencies=usd').json()
        except requests.exceptions.RequestException:
            return None
        except json.decoder.JSONDecodeError:
            return None

        """
        {"bitcoin":{"usd":60060},"monero":{"usd":230.31}}
        """
        coin = coin.casefold()
        if coin == 'btc':
            return Decimal(parsed_json['bitcoin']['usd'])
        if coin == 'xmr':
            return Decimal(parsed_json['monero']['usd'])
        raise Exception(f'Unsupported coin {coin}')
