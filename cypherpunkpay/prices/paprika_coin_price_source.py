from decimal import Decimal

import json
import requests

from cypherpunkpay.prices.price_source import PriceSource


class PaprikaCoinPriceSource(PriceSource):

    def get(self, coin: str, fiat: str) -> [Decimal, None]:
        if fiat != 'usd':
            raise Exception(f'Unsupported fiat {fiat}')
        try:
            parsed_json = self._http_client.get(f'https://api.coinpaprika.com/v1/tickers/{self.paprika_coin_id(coin)}', 'gerer').json()
        except requests.exceptions.RequestException:
            return None
        except json.decoder.JSONDecodeError:
            return None

        return Decimal(parsed_json['quotes']['USD']['price'])

    def paprika_coin_id(self, coin):
        if coin == 'btc':
            return 'btc-bitcoin'
        if coin == 'xmr':
            return 'xmr-monero'
        raise Exception(f'Unsupported coin {coin}')
