import os

import waitress
from pyramid import paster

from cypherpunkpay import App


def main():
    production_ini_path: str = get_production_ini_path()
    paster.setup_logging(production_ini_path)
    wsgi_app = paster.get_app(production_ini_path)  # reads *.conf and CLI args, instantiates CypherpunkPay App(), creates wsgi app
    server_config = App().config().server()
    waitress.serve(wsgi_app, **server_config)


def get_production_ini_path() -> str:
    return os.path.join(os.path.dirname(__file__), 'config', 'production.ini')
