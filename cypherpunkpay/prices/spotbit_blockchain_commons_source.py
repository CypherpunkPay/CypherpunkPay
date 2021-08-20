# Ref. https://github.com/BlockchainCommons/spotbit.git

from decimal import Decimal

import logging as log
import json
import requests

from cypherpunkpay.prices.price_source import PriceSource

class SpotBitBlockchainCommonsPriceSource(PriceSource):

    def get(self, coin: str, fiat: str) -> [Decimal, None]:
        # log.info('SpotBitBlockchainCommonsPriceSource')
        spotBitHiddenService  = 'h6zwwkcivy2hjys6xpinlnz2f74dsmvltzsd4xb42vinhlcaoe7fdeqd.onion'
        clearNetPriceEndpoint = 'https://spotbit.info/spotbit/proxy.php'

        if fiat != 'usd':   # TODO(nochiel) Verify that CypherpunkPay shows a user-selected fiat currency.
            raise Exception(f'Unsupported fiat {fiat}')
        try:
            # FIXME(nochiel) When using spotBitHiddenService we get the error:
            # 2021-08-21 00:52:57 ERROR [ThreadPoolExecutor-0_0] Request failed: Invalid URL 'h6zwwkcivy2hjys6xpinlnz2f74dsmvltzs d4xb42vinhlcaoe7fdeqd.onion/now/usd': No schema supplied. Perhaps you meant http://h6zwwkcivy2hjys6xpinlnz2f74dsmvl tzsd4xb42vinhlcaoe7fdeqd.onion/now/usd?
            # parsed_json = self._http_client.get_accepting_linkability(f'{spotBitHiddenService}/now/{fiat}').json()

            parsed_json = self._http_client.get_accepting_linkability(clearNetPriceEndpoint).json()
            # log.info(f'response: {parsed_json}')
        except requests.exceptions.RequestException as e:
            log.error(f'Request failed: {e}')
            return None
        except json.decoder.JSONDecodeError:
            log.error('Decoding JSON failed.')
            return None

        # Hidden service gives us:
        # {"close":48765.376000000004,"currency_pair":"BTC-USD","datetime":"Fri, 20 Aug 2021 21:39:59 GMT","exchanges":["coin basepro","okcoin","bitfinex","kraken","bitstamp"],"failed_exchanges":[],"high":48766.286,"id":"average_value","low" :48763.476,"oldest_timestamp":1629494760000,"open":48764.409888672,"timestamp":1629495599851.749,"volume":0.6105790 819999999}
        # ---
        # Clearnet gives us:
        # [{"close":48511.83,"datetime":"Fri, 20 Aug 2021 15:55:23 GMT","id":"on_demand","symbol":"BTC/USD","timestamp":162947 4923,"volume":null}]
        
        coin = coin.casefold()
        if coin == 'btc':
            return Decimal(parsed_json[0]['close'])
            # return Decimal(parsed_json['close'])
        else:
            raise Exception(f'Unsupported coin {coin}')




