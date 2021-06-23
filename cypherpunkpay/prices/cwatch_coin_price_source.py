from decimal import Decimal

import json
import requests

from cypherpunkpay.prices.price_source import PriceSource


class CwatchCoinPriceSource(PriceSource):

    def get(self, coin: str, fiat: str) -> [Decimal, None]:
        if fiat != 'usd':
            raise Exception(f'Unsupported fiat {fiat}')
        try:
            parsed_json = self._http_client.get_accepting_linkability(f'https://billboard.service.cryptowat.ch/assets?quote=usd&limit=50&sort=marketcap').json()
        except requests.exceptions.RequestException:
            return None
        except json.decoder.JSONDecodeError:
            return None

        coins_json = parsed_json['result']['rows']
        for coin_json in coins_json:
            if coin_json['symbol'].casefold() == coin:
                return Decimal(coin_json['price'])
