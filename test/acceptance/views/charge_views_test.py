from decimal import Decimal

from cypherpunkpay.app import App
from test.acceptance.app_test_case import CypherpunkpayAppTestCase


class ChargeViewsTest(CypherpunkpayAppTestCase):

    def test_get_charge_root(self):
        res = self.webapp.get('/cypherpunkpay/charge/abcd1234', status=302)
        self.assertMatch('http://localhost/cypherpunkpay/charge/abcd1234/auto', res.location)

    # User enters incorrect amount in donations and clicks [Donate]
    def test_attempt_to_charge_invalid_amount(self):
        # POST charge - missing amount
        res = self.webapp.post('/cypherpunkpay/charge', dict(currency='usd'), status=302)
        self.assertRedirectsToDonationsWithErrorOn(res, 'total')

        # POST charge - empty amount
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='', currency='usd'), status=302)
        self.assertRedirectsToDonationsWithErrorOn(res, 'total')

        # POST charge - invalid amount
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='r!23', currency='usd'), status=302)
        self.assertRedirectsToDonationsWithErrorOn(res, 'total')

    # User enters incorrect amount in donations and clicks [Donate]
    def test_attempt_to_charge_invalid_currency(self):
        # POST charge - missing currency
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='25'), status=302)
        self.assertRedirectsToDonationsWithErrorOn(res, 'currency')

        # POST charge - empty currency
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='25', curency='usd'), status=302)
        self.assertRedirectsToDonationsWithErrorOn(res, 'currency')

        # POST charge - invalid currency
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='25', curency='xxx'), status=302)
        self.assertRedirectsToDonationsWithErrorOn(res, 'currency')

    def test_charge_btc_success_flow_auto(self):
        # POST charge
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='0.00000307', currency='btc'))
        url = res.location
        self.assertEqual(302, res.status_int)

        # GET unpaid
        res = self.webapp.get(url)
        charge = App().db().get_last_charge()
        self.assertInBody(res, '0.00000307')
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, charge.cc_address)

        # GET underpaid
        charge.pay_status = 'underpaid'
        charge.cc_received_total = Decimal('0.00000300')
        App().db().save(charge)
        res = self.webapp.get(url)
        self.assertInBody(res, '0.00000007')
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, charge.cc_address)

        # GET paid
        charge.pay_status = 'paid'
        charge.cc_received_total = Decimal('0.00000308')   # slightly over pay
        App().db().save(charge)
        res = self.webapp.get(url)
        self.assertInBody(res, '0.00000308')  # we noticed your incoming payment AMOUNT
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, 'in progress')
        self.assertInBody(res, charge.uid)    # your reference charge ID
        self.assertNotInBody(res, charge.cc_address)  # address should no longer be displayed

        # GET confirmed
        charge.pay_status = 'confirmed'
        charge.confirmations = 1
        App().db().save(charge)
        res = self.webapp.get(url)
        self.assertInBody(res, '0.00000308')  # we noticed your incoming payment AMOUNT
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, '1 network confirmation')
        self.assertInBody(res, charge.uid)    # your reference charge ID
        self.assertNotInBody(res, charge.cc_address)  # address should no longer be displayed

        # GET completed
        charge.pay_status = 'confirmed'
        charge.status = 'completed'
        charge.confirmations = 2
        App().db().save(charge)
        res = self.webapp.get(url)
        self.assertInBody(res, '0.00000308')  # we received AMOUNT
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, 'completed')
        self.assertInBody(res, charge.uid)    # your reference charge ID
        self.assertNotInBody(res, charge.cc_address)  # address should no longer be displayed

    def test_charge_btc_success_flow_manual(self):
        # POST charge
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='37', currency='btc'))
        url = res.location
        self.assertEqual(302, res.status_int)

        # GET unpaid
        res = self.webapp.get(url.replace('/auto', '/manual'))
        charge = App().db().get_last_charge()
        self.assertInBody(res, '37')
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, charge.cc_address)

        # GET underpaid
        charge.pay_status = 'underpaid'
        charge.cc_received_total = Decimal('11')
        App().db().save(charge)
        res = self.webapp.get(url.replace('/auto', '/manual'))
        self.assertInBody(res, '26')
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, charge.cc_address)

        # GET paid
        charge.pay_status = 'paid'
        charge.cc_received_total = Decimal('37')
        App().db().save(charge)
        res = self.webapp.get(url.replace('/auto', '/manual'))
        self.assertInBody(res, '37')  # we noticed your incoming payment AMOUNT
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, 'in progress')
        self.assertInBody(res, charge.uid)  # your reference charge ID
        self.assertNotInBody(res, charge.cc_address)  # address should no longer be displayed

        # GET confirmed
        charge.pay_status = 'confirmed'
        charge.confirmations = 1
        App().db().save(charge)
        res = self.webapp.get(url.replace('/auto', '/manual'))
        self.assertInBody(res, '37')  # we noticed your incoming payment AMOUNT
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, '1 network confirmation')
        self.assertInBody(res, charge.uid)  # your reference charge ID
        self.assertNotInBody(res, charge.cc_address)  # address should no longer be displayed

        # GET completed
        charge.pay_status = 'confirmed'
        charge.status = 'completed'
        charge.confirmations = 2
        App().db().save(charge)
        res = self.webapp.get(url.replace('/auto', '/manual'))
        self.assertInBody(res, '37')  # we received AMOUNT
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, 'completed')
        self.assertInBody(res, charge.uid)  # your reference charge ID
        self.assertNotInBody(res, charge.cc_address)  # address should no longer be displayed

    def test_charge_usd_then_select_btc_payment(self):
        # POST charge
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='10.73', currency='usd'))
        url = res.location
        self.assertEqual(302, res.status_int)

        # GET pick_coin
        res = self.webapp.get(url)
        self.assertInBody(res, '$10.73')

        # POST pick_coin
        charge = App().db().get_last_charge()
        res = self.webapp.post(f'/cypherpunkpay/charge/{charge.uid}/pick_coin', dict(cc_currency='btc'))
        url = res.location

        # GET unpaid
        res = self.webapp.get(url)
        charge = App().db().get_last_charge()
        self.assertInBody(res, 'BTC')
        self.assertInBody(res, charge.cc_address)

    def test_charge_eur_then_select_xmr_payment(self):
        # POST charge
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='10.73', currency='eur'))
        url = res.location
        self.assertEqual(302, res.status_int)

        # GET pick_coin
        res = self.webapp.get(url)
        self.assertInBody(res, '10.73\xa0€')

        # POST pick_coin
        charge = App().db().get_last_charge()
        res = self.webapp.post(f'/cypherpunkpay/charge/{charge.uid}/pick_coin', dict(cc_currency='xmr'))
        url = res.location

        # GET unpaid
        res = self.webapp.get(url)
        charge = App().db().get_last_charge()
        self.assertInBody(res, 'XMR')
        self.assertInBody(res, charge.cc_address)

    def test_get_charge_state_hash(self):
        # POST charge
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='0.00005', currency='btc'))
        url = res.location
        charge = App().db().get_last_charge()

        res = self.webapp.get(f'/cypherpunkpay/charge/{charge.uid}/state_hash')
        hash_before = res.body.decode('utf-8')

        charge.pay_status = 'paid'
        App().db().save(charge)

        res = self.webapp.get(f'/cypherpunkpay/charge/{charge.uid}/state_hash')
        hash_after = res.body.decode('utf-8')

        self.assertNotEqual(hash_after, hash_before)

    def test_cancel_charge(self):
        # POST charge
        res = self.webapp.post('/cypherpunkpay/charge', dict(total='0.1', currency='btc'))
        charge = App().db().get_last_charge()

        # Cancel charge
        res = self.webapp.post(f'/cypherpunkpay/charge/{charge.uid}/cancel')
        charge = App().db().reload(charge)

        donations_url = res.location
        self.assertTrue('/cypherpunkpay/donations' in res.location)
        self.assertEqual('cancelled', charge.status)

    def assertRedirectsToDonationsWithErrorOn(self, res, error_field_name: str):
        donations_url = res.location
        self.assertTrue('/cypherpunkpay/donations' in res.location)
        self.assertTrue(error_field_name in donations_url)
        res = self.webapp.get(donations_url)
        self.assertInBody(res, 'is-danger')  # error got recognized
