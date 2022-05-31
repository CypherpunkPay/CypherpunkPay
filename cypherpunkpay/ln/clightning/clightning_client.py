from cypherpunkpay.globals import *

from cypherpunkpay.models.ln_invoice_status import LnInvoiceStatus
from cypherpunkpay.tools.safe_uid import SafeUid

from .pylnclient.lightning import LightningRpc, RpcError
from ..lightning_client import LightningClient, LightningException, UnauthorizedLightningException, UnknownInvoiceLightningException


class CLightningClient(LightningClient):

    def __init__(self, lightningd_socket_path: str):
        self._lightningd_rpc = LightningRpc(socket_path=lightningd_socket_path)

    def ping(self) -> None:
        try:
            self._ping()
        except FileNotFoundError as e:
            log.error(f'File not found [{self._lightningd_rpc.socket_path}] - verify lightningd is running and creates RPC socket at this path')
            raise LightningException(e)
        except PermissionError as e:
            log.error(f'Permission denied while connecting to lightningd RPC socket [{self._lightningd_rpc.socket_path}] - verify cypherpunkpay user has r/w permissions to this path')
            raise UnauthorizedLightningException(e)
        except (RpcError, ValueError) as e:
            log.error(e)
            raise LightningException(e)

    def create_invoice(self, total_btc: [Decimal, None] = None, memo: str = None, expiry_seconds: [int, None] = None) -> str:
        # Our local variables names match lightningd RPC param names for easy reference.
        # The relevant RPC call: https://lightning.readthedocs.io/lightning-invoice.7.html

        # Amount to be paid expressed in milli satoshi as expected by lightningd
        value_msats = 'any'
        if isinstance(total_btc, Decimal) or isinstance(total_btc, int):
            value_msats = round(total_btc * 10 ** 8 * 1000)

        # Invoice ID we won't use but must provide to make lightningd happy
        label = SafeUid.gen()

        # Purpose of a payment or empty string as lightningd does not allow for None
        description = memo or ''

        # Expiry in seconds, lightningd will use 1 week if not provided
        expiry = expiry_seconds

        try:
            res: dict = self._invoice(value_msats, label, description, expiry)
            return res['bolt11']
        except FileNotFoundError as e:
            log.error(f'File not found [{self._lightningd_rpc.socket_path}] - verify lightningd is running and creates RPC socket at this path')
            raise LightningException(e)
        except PermissionError as e:
            log.error(f'Permission denied while connecting to lightningd RPC socket [{self._lightningd_rpc.socket_path}] - verify cypherpunkpay user has r/w permissions to this path')
            raise UnauthorizedLightningException(e)
        except (RpcError, ValueError) as e:
            log.error(e)
            raise LightningException(e)

    def get_invoice(self, payment_hash: bytes) -> LnInvoiceStatus:
        # The relevant RPC call: https://lightning.readthedocs.io/lightning-listinvoices.7.html?highlight=listinvoices
        self.assert_payment_hash(payment_hash)
        payment_hash_str: str = payment_hash.hex()

        try:
            res: dict = self._listinvoices(payment_hash=payment_hash_str)
            if res.get('invoices'):
                # {
                #     'invoices': [
                #         {'label': '...', 'bolt11': 'lntb1ps..', 'payment_hash': '...', 'status': 'unpaid', 'description': '', 'expires_at': 1644500937},
                #         {'label': 'tr2lqp23ozs5tfubxemy2nk5ky', 'bolt11': 'lntb1p3qyn6fpp5r2uq6rsvueyp2yjjkp4je2w8l6lcezkesmlxujxrgs8zhzr3dxlsdqqxqyjw5qcqp2sp5mkjzayng7kd6jec0qzf3qukhar8luskntn5kl2s24ta3v6mct84q9qyyssqukvmcurldz3cjk3vg3v5wp3zyss5h7nn5v37l04x83vdgmjj4dh5qf66lxlnuahqv87x747p0gf0hk5xzfgmdw3x0p2vdyclmj8tcuqpdlfc87', 'payment_hash': '1ab80d0e0ce648151252b06b2ca9c7febf8c8ad986fe6e48c3440e2b887169bf', 'status': 'unpaid', 'description': '', 'expires_at': 1644923337}
                #     ]
                # }
                invoice = res['invoices'][0]
                ln_invoice = LnInvoiceStatus()
                if invoice['status'] == 'paid':
                    ln_invoice.is_settled = True
                    ln_invoice.amt_paid_msat = invoice['amount_received_msat']
                return ln_invoice
            else:
                raise UnknownInvoiceLightningException()
        except FileNotFoundError as e:
            log.error(f'File not found [{self._lightningd_rpc.socket_path}] - verify lightningd is running and creates RPC socket at this path')
            raise LightningException(e)
        except PermissionError as e:
            log.error(f'Permission denied while connecting to lightningd RPC socket [{self._lightningd_rpc.socket_path}] - verify cypherpunkpay user has r/w permissions to this path')
            raise UnauthorizedLightningException(e)
        except (RpcError, ValueError) as e:
            log.error(e)
            raise LightningException(e)

    # MOCK ME
    def _ping(self):
        self._lightningd_rpc.getinfo()

    # MOCK ME
    def _invoice(self, value_msats, label, description, expiry):
        return self._lightningd_rpc.invoice(value_msats, label, description, expiry)

    # MOCK ME
    def _listinvoices(self, payment_hash: str):
        return self._lightningd_rpc.listinvoices(payment_hash=payment_hash)

    def name(self) -> str:
        return f'lightningd at {self._lightningd_rpc.socket_path}'
