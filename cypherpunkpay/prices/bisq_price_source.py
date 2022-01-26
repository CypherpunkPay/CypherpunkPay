from decimal import Decimal

import json
import requests

from cypherpunkpay.prices.price_source import PriceSource


# This queries specific "Bisq Price Node" operated by devinbileck for the Bisq decentralized exchange.
# Bisq Price Nodes are price aggregators over a number of crypto exchanges.
# As a side note, the Bisq exchange itself uses a handful of independent Price Nodes to understand crypto asset prices.
# We here use a single, specific price node.
class BisqPriceSource(PriceSource):

    def get(self, coin: str, fiat: str) -> [Decimal, None]:
        if fiat != 'usd':
            raise Exception(f'Unsupported fiat {fiat}')
        try:
            parsed_json = self._http_client.get_accepting_linkability('http://devinpndvdwll4wiqcyq5e7itezmarg7rzicrvf6brzkwxdm374kmmyd.onion/getAllMarketPrices').json()
        except requests.exceptions.RequestException:
            return None
        except json.decoder.JSONDecodeError:
            return None

        """
        {
            "data": [
                {
                    "currencyCode" : "USD",
                    "price" : 37642.836421944856,
                    "timestampSec" : 1643192687466,
                    "provider" : "Bisq-Aggregate"
                },
                {
                    "currencyCode" : "XMR",
                    "price" : 0.00390313,
                    "timestampSec" : 1643192687466,
                    "provider" : "Bisq-Aggregate"
                }
            ]
        }
        """
        coin = coin.casefold()
        data = parsed_json['data']
        # Bitcoin and Monero are treated differently in the JSON data file, hence implementation assymetry.
        # We first need to learn BTC/USD price even if we are ultimately after XMR/USD.
        for entry in data:
            if entry['currencyCode'] == 'USD':
                btc_usd = Decimal(entry['price'])
                if coin == 'btc':
                    return btc_usd
        if coin == 'xmr':
            for entry in data:
                if entry['currencyCode'] == 'XMR':
                    xmr_btc = Decimal(entry['price'])
                    return xmr_btc * btc_usd
        raise Exception(f'Unsupported coin {coin}')
