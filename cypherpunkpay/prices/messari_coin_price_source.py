from decimal import Decimal

import json
import requests

from cypherpunkpay.prices.price_source import PriceSource


class MessariCoinPriceSource(PriceSource):

    def get(self, coin: str, fiat: str) -> [Decimal, None]:
        if fiat != 'usd':
            raise Exception(f'Unsupported fiat {fiat}')
        try:
            parsed_json = self._http_client.get_accepting_linkability(f'https://data.messari.io/api/v1/assets/{coin}/metrics/market-data').json()
        except requests.exceptions.RequestException:
            return None
        except json.decoder.JSONDecodeError:
            return None

        return Decimal(parsed_json['data']['market_data']['price_usd'])
