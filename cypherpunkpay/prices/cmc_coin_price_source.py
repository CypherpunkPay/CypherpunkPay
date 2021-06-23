from decimal import Decimal

import json
import requests

from cypherpunkpay.prices.price_source import PriceSource


class CmcCoinPriceSource(PriceSource):

    def get(self, coin: str, fiat: str) -> [Decimal, None]:
        if fiat != 'usd':
            raise Exception(f'Unsupported fiat {fiat}')
        try:
            parsed_json = self._http_client.get_accepting_linkability('https://web-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=50&start=1').json()
        except requests.exceptions.RequestException:
            return None
        except json.decoder.JSONDecodeError:
            return None

        json_coins = parsed_json['data']
        for json_coin in json_coins:
            if json_coin['symbol'].casefold() == coin.casefold():
                return Decimal(json_coin['quote']['USD']['price'])
