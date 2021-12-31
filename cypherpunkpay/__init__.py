import logging
import secrets
import time

from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.static import QueryStringConstantCacheBuster

from cypherpunkpay.app import App
from cypherpunkpay.common import *
from cypherpunkpay.config.config import Config
from cypherpunkpay.config.config_parser import ConfigParser
from cypherpunkpay.bitcoin.electrum.constants import set_btc_mainnet, set_btc_testnet
from cypherpunkpay.jobs.job_scheduler import DummyJobScheduler
from cypherpunkpay.prices.price_tickers import ExamplePriceTickers
from cypherpunkpay.web.security.root_acl import RootACL


def main(global_config, **settings):
    """ This function instantiates real app singleton and returns a Pyramid WSGI web app.
    """
    start_application_singleton_or_exit(settings)

    pyramid = Configurator(settings=settings, root_factory='cypherpunkpay.web.security.root_acl.RootACL')

    # Template engine
    pyramid.include('pyramid_jinja2')

    # Routing
    path_prefix = App().config().path_prefix()
    if path_prefix:
        pyramid.add_route('get_root_not_prefixed', '/', request_method='GET')  # 302: / -> /path_prefix/

    pyramid.include(routing_config, route_prefix=path_prefix)

    # Authentication and Authorization
    configure_pyramid_authn_and_authz(pyramid)

    # Scan for views (controllers)
    scan_views(pyramid)

    # Create pyramid WSGI app
    wsgi_app = pyramid.make_wsgi_app()

    return wsgi_app


def start_application_singleton_or_exit(settings):
    log = logging.getLogger()
    if settings.get('test_env'):
        # Application already instantiated by tests setup
        pass
    elif settings.get('dev_env'):
        config = ConfigParser(env='dev').from_user_conf_files()
        set_btc_network(config)
        App(config=config)
    else:
        config = ConfigParser(env='prod').from_user_conf_files_and_cli_args()
        set_btc_network(config)
        App(config=config)


def configure_pyramid_authn_and_authz(pyramid):
    authn_secret = secrets.token_bytes(nbytes=64)  # generating this dynamically will invalidate sessions on app restart
    authn_policy = AuthTktAuthenticationPolicy(
        authn_secret,
        hashalg='sha512',
        timeout=3600,
        reissue_time=60,
        path=f'{App().config().path_prefix()}/admin',
        http_only=True,
        callback=(lambda user_login, request: ['group:admins'] if user_login == 'admin' else [])  # return groups for specific user
    )
    authz_policy = ACLAuthorizationPolicy()
    pyramid.set_authentication_policy(authn_policy)
    pyramid.set_authorization_policy(authz_policy)


def routing_config(pyramid):
    log = logging.getLogger()

    pyramid.add_static_view('js', 'web/js')
    pyramid.add_static_view('css', 'web/css')
    pyramid.add_static_view('png', 'web/png')
    timestamp = str(int(time.time()))
    pyramid.add_cache_buster('web/js/', QueryStringConstantCacheBuster(timestamp))
    pyramid.add_cache_buster('web/css/', QueryStringConstantCacheBuster(timestamp))
    pyramid.add_cache_buster('web/png/', QueryStringConstantCacheBuster(timestamp))

    pyramid.add_notfound_view(None, append_slash=True)  # auto append slash on 404

    pyramid.add_route('get_root', '/', request_method='GET')
    pyramid.add_route('post_charge', '/charge', request_method='POST')
    pyramid.add_route('get_charge_pick_coin', '/charge/{uid}/pick_coin', request_method='GET')
    pyramid.add_route('post_charge_pick_coin', '/charge/{uid}/pick_coin', request_method='POST')
    pyramid.add_route('post_charge_cancel', '/charge/{uid}/cancel', request_method='POST')
    pyramid.add_route('get_charge_state_hash', '/charge/{uid}/state_hash', request_method='GET')
    pyramid.add_route('get_charge', '/charge/{uid}/{ux_type}', request_method='GET')
    pyramid.add_route('get_charge_root', '/charge/{uid}', request_method='GET')

    if App().config().donations_enabled():
        pyramid.add_route('get_donations', '/donations', request_method='GET')

    if App().config().admin_panel_enabled():
        unique = App().get_admin_unique_path_segment()
        with pyramid.route_prefix_context(f'/admin/{unique}'):
            log.info(f'Admin panel enabled at /{pyramid.route_prefix}/')
            pyramid.add_route('admin_register', '/register', request_method=['GET', 'POST'])
            pyramid.add_route('admin_login', '/login', request_method=['GET', 'POST'])
            pyramid.add_route('admin_logout', '/logout', request_method='POST')
            pyramid.add_route('get_admin_root', '/', request_method='GET')
            pyramid.add_route('get_admin_charges', '/charges', request_method='GET')
            pyramid.add_route('get_admin_stats', '/stats', request_method='GET')
    else:
        log.info(f'Admin panel DISABLED (see /etc/cypherpunkpay.conf)')

    if App().config().dummystore_enabled():
        with pyramid.route_prefix_context(f'/dummystore'):
            log.info(f'Dummy store enabled at /{pyramid.route_prefix}/')
            pyramid.add_route('get_dummystore_root', '/', request_method='GET')
            pyramid.add_route('post_cypherpunkpay_payment_completed', '/cypherpunkpay_payment_completed', request_method='POST')
            pyramid.add_route('post_cypherpunkpay_payment_failed', '/cypherpunkpay_payment_failed', request_method='POST')
            pyramid.add_route('get_dummystore_order', '/order/{uid}', request_method='GET')


def scan_views(pyramid):
    pyramid.scan('cypherpunkpay.web.views')
    if App().config().path_prefix():
        pyramid.scan('cypherpunkpay.web.views_prefix')
    if App().config().donations_enabled():
        pyramid.scan('cypherpunkpay.web.views_donations')
    if App().config().admin_panel_enabled():
        pyramid.scan('cypherpunkpay.web.views_admin')
    if App().config().dummystore_enabled():
        pyramid.scan('cypherpunkpay.web.views_dummystore')


def set_btc_network(config):
    # This is necessary because of Electrum's code unfortunate reliance on global state
    if config.btc_mainnet():
        set_btc_mainnet()
    else:
        set_btc_testnet()
