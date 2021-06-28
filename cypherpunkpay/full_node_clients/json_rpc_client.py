import decimal
import json
import logging as log
from json.decoder import JSONDecodeError
from typing import Dict, List
from base64 import b64encode

import requests

from cypherpunkpay.net.http_client.clear_http_client import ClearHttpClient


class JsonRpcClient(object):
    __id_count = 0

    def __init__(self, service_url, user='bitcoin', passwd='secret', http_client=None, service_name=None):
        self.__service_url = service_url

        self.__user = user
        self.__passwd = passwd
        user_bytes = user.encode('utf8')
        passwd_bytes = passwd.encode('utf8')
        authpair_bytes = user_bytes + b':' + passwd_bytes
        self.__auth_header = b'Basic ' + b64encode(authpair_bytes)

        self.__http_client = http_client if http_client else ClearHttpClient()
        self.__service_name = service_name

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        if self.__service_name is not None:
            name = "%s.%s" % (self.__service_name, name)
        return JsonRpcClient(self.__service_url, self.__user, self.__passwd, http_client=self.__http_client, service_name=name)

    def __call__(self, *args) -> [Dict, None]:
        JsonRpcClient.__id_count += 1
        log.debug("-%s-> %s %s" % (JsonRpcClient.__id_count, self.__service_name, json.dumps(args, default=decimal_to_float)))

        # Hack to extract the path from params
        path = ''
        if self._last_argument_is_wallet_path(args):
            path = args[-1]
            args = tuple(args[0:-1])
            if len(args) == 1 and isinstance(args[0], Dict):
                args = args[0]

        headers_d = {
            'Authorization': self.__auth_header,
            'Content-Type': 'application/json'
        }
        body_s = json.dumps(
            {
                'version': '1.1',
                'method': self.__service_name,
                'params': args,
                'id': JsonRpcClient.__id_count
            },
            default=decimal_to_float
        )

        try:
            response = self.__http_client.post_accepting_linkability(
                self.__service_url + path,
                headers=headers_d,
                body=body_s,
                set_tor_browser_headers=False
            )
        except requests.exceptions.RequestException as e:
            log.warning(f'Error connecting to {self.__service_url} [{e.__class__.__name__}]. Is full node running? Is RPC server enabled?')
            raise JsonRpcRequestError() from e

        if response.status_code == 401:
            log.warning(f'Error authenticating to {self.__service_url} Check RPC rpcuser, rpcpassword.')
            raise JsonRpcAuthenticationError()

        response_text = response.text
        #log.info(f'response_text={response_text}')

        try:
            response_json = json.loads(response_text, parse_float=decimal.Decimal)
        except JSONDecodeError as e:
            log.warning(f'[{self.__service_name}] Unexpected non-JSON API response: {response_text}')
            raise JsonRpcParsingError() from e

        if response_json.get('error') is not None:
            log.warning(f'[{self.__service_name}] JSON/RPC call error: {response_json["error"]}')
            raise JsonRpcCallError(response_json['error'])

        if 'result' not in response_json:
            log.warning(f'[{self.__service_name}] JSON/RPC call error: missing "result" attribute in JSON response: {response_text}')
            raise JsonRpcCallError()

        result = response_json['result']

        if isinstance(result, List):
            for result_item in result:
                if isinstance(result_item, Dict) and result_item.get('error') is not None:
                    log.warning(f'[{self.__service_name}] JSON/RPC call error: {result_item["error"]}')
                    raise JsonRpcCallError(result_item['error'])

        return result

    def _last_argument_is_wallet_path(self, args):
        return len(args) > 0 and isinstance(args[-1], str) and 'cypherpunkpay-wallet' in args[-1]


def decimal_to_float(obj):
    if isinstance(obj, decimal.Decimal):
        return float(round(obj, 8))
    raise TypeError(repr(obj) + " is not JSON serializable")


class JsonRpcError(BaseException):
    pass


class JsonRpcRequestError(JsonRpcError):
    pass


class JsonRpcAuthenticationError(JsonRpcError):
    pass


class JsonRpcParsingError(JsonRpcError):
    pass


class JsonRpcCallError(JsonRpcError):
    pass
