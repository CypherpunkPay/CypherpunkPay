from cypherpunkpay.common import *
from cypherpunkpay.models.user import User
from cypherpunkpay.tools.pbkdf2 import PBKDF2
from cypherpunkpay.tools.safe_uid import SafeUid
from cypherpunkpay.usecases.create_charge_uc import CreateChargeUC
from cypherpunkpay.usecases.pick_cryptocurrency_for_charge_uc import PickCryptocurrencyForChargeUC


class DevExamples(object):

    DUMMY_STORE_ITEMS = [
        { 'name': 'Peanut', 'price': Decimal('0.01'), 'currency': 'usd' },
        { 'name': 'Box of matches', 'price': Decimal('0.12'), 'currency': 'eur' },
        { 'name': 'Laptop sticker', 'price': Decimal('0.99'), 'currency': 'cny' },
        { 'name': 'E-mail 1 month', 'price': Decimal('2.50'), 'currency': 'gbp' },
        { 'name': 'VPN 1 month', 'price': Decimal('6'), 'currency': 'usd' },
        { 'name': 'A hardware wallet', 'price': Decimal('100'), 'currency': 'usd' },
        { 'name': 'A laptop', 'price': Decimal('2500'), 'currency': 'usd' },
        { 'name': 'Million sats', 'price': Decimal('0.01000000'), 'currency': 'btc' },
        { 'name': 'One bitcoin', 'price': 1, 'currency': 'btc' },
    ]

    def create_all_if_missing(self):
        from cypherpunkpay.app import App
        db = App().db()

        if len(db.get_users()) > 0:
            return  # examples already created

        self.create_all(db)

    def create_all(self, db):
        log.info('Creating development examples...')
        self.create_admin_user(db)
        self.create_charges(db)
        log.info('Done creating development examples')

    def create_admin_user(self, db):
        log.info('...creating admin user')
        # Admin user
        user = User(username='admin', password_hash=PBKDF2.hash('admin123'))
        db.insert(user)

    def create_charges(self, db):
        log.info('...creating charges')

        # Draft USD round amount
        charge = CreateChargeUC(
            total='1',
            currency='usd'
        ).exec()
        charge.created_at = utc_ago(seconds=5)
        db.save(charge)

        # Draft EUR precise amount
        charge = CreateChargeUC(
            total='149.99',
            currency='eur'
        ).exec()
        charge.created_at = utc_ago(seconds=10)
        db.save(charge)

        # Awaiting unpaid BTC precise amount
        charge = CreateChargeUC(
            total='0.00000001',
            currency='btc'
        ).exec()
        charge.created_at = utc_ago(seconds=15)
        charge.activated_at = charge.created_at
        db.save(charge)

        # Awaiting unpaid BTC round amount
        charge = CreateChargeUC(
            total='2',
            currency='btc'
        ).exec()
        charge.created_at = utc_ago(seconds=20)
        charge.activated_at = charge.created_at
        db.save(charge)

        # Awaiting unpaid XMR precise amount
        charge = CreateChargeUC(
            total='0.00000001',
            currency='xmr'
        ).exec()
        charge.created_at = utc_ago(seconds=25)
        charge.activated_at = charge.created_at
        db.save(charge)

        # Awaiting unpaid XMR round amount
        charge = CreateChargeUC(
            total='10',
            currency='xmr'
        ).exec()
        charge.created_at = utc_ago(seconds=30)
        charge.activated_at = charge.created_at
        db.save(charge)

        # Awaiting underpaid USD/BTC
        charge = CreateChargeUC(
            total='12.75',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(seconds=35)
        charge.activated_at = charge.created_at
        charge.cc_received_total = Decimal('0.00081')
        charge.pay_status = 'underpaid'
        charge.status = 'awaiting'
        db.save(charge)

        # Awaiting underpaid BTC
        charge = CreateChargeUC(
            total='0.01',
            currency='btc'
        ).exec()
        charge.created_at = utc_ago(hours=8)
        charge.activated_at = charge.created_at
        charge.cc_received_total = Decimal('0.008')
        charge.pay_status = 'underpaid'
        db.save(charge)

        # Awaiting paid USD/BTC
        charge = CreateChargeUC(
            total='1',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(hours=9)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total
        charge.pay_status = 'paid'
        charge.paid_at = utc_ago(hours=8, minutes=55)
        db.save(charge)

        # Awaiting confirmed USD/BTC
        charge = CreateChargeUC(
            total='1',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(hours=10)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total
        charge.pay_status = 'confirmed'
        charge.paid_at = utc_ago(hours=9, minutes=50)
        charge.confirmations = 1
        db.save(charge)

        # Completed confirmed USD/BTC
        charge = CreateChargeUC(
            total='10.99',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(hours=10, minutes=10)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total
        charge.confirmations = 2
        charge.pay_status = 'confirmed'
        charge.paid_at = utc_ago(hours=10)
        charge.status = 'completed'
        db.save(charge)

        # Completed confirmed EUR/XMR
        charge = CreateChargeUC(
            total='20',
            currency='eur'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='xmr',
        ).exec()
        charge.created_at = utc_ago(hours=10, minutes=20)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total
        charge.confirmations = 20
        charge.pay_status = 'confirmed'
        charge.paid_at = utc_ago(hours=10, minutes=15)
        charge.status = 'completed'
        db.save(charge)

        # Completed confirmed EUR/XMR
        charge = CreateChargeUC(
            total='100',
            currency='czk'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(hours=10, minutes=30)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total
        charge.confirmations = 3
        charge.pay_status = 'confirmed'
        charge.paid_at = utc_ago(hours=10, minutes=20)
        charge.status = 'completed'
        db.save(charge)

        # Completed overpaid USD/BTC
        charge = CreateChargeUC(
            total='7',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(hours=11)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total + Decimal('0.0005')
        charge.confirmations = 2
        charge.pay_status = 'confirmed'
        charge.paid_at = utc_ago(hours=10, minutes=45)
        charge.status = 'completed'
        db.save(charge)

        # Cancelled unpaid USD/BTC
        charge = CreateChargeUC(
            total='2',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(hours=12)
        charge.activated_at = charge.created_at
        charge.pay_status = 'unpaid'
        charge.paid_at = utc_ago(hours=11, minutes=45)
        charge.status = 'cancelled'
        db.save(charge)

        # Cancelled paid USD/BTC
        charge = CreateChargeUC(
            total='2',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(hours=13)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total
        charge.pay_status = 'paid'
        charge.paid_at = utc_ago(hours=12, minutes=45)
        charge.status = 'cancelled'
        db.save(charge)

        # Cancelled confirmed USD/BTC
        charge = CreateChargeUC(
            total='2',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(hours=14)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total
        charge.pay_status = 'confirmed'
        charge.paid_at = utc_ago(hours=13, minutes=45)
        charge.confirmations = 1
        charge.status = 'cancelled'
        db.save(charge)

        # Expired unpaid USD/BTC
        charge = CreateChargeUC(
            total='2',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(days=3)
        charge.activated_at = charge.created_at
        charge.pay_status = 'unpaid'
        db.save(charge)

        # Expired paid USD/BTC
        charge = CreateChargeUC(
            total='2',
            currency='usd'
        ).exec()
        charge = PickCryptocurrencyForChargeUC(
            charge=charge,
            cc_currency='btc',
        ).exec()
        charge.created_at = utc_ago(days=3)
        charge.activated_at = charge.created_at
        charge.cc_received_total = charge.cc_total
        charge.pay_status = 'paid'
        charge.paid_at = utc_ago(days=2, hours=23, minutes=45)
        db.save(charge)

    def create_dummy_store_orders(self, db):
        from cypherpunkpay.models.dummy_store_order import DummyStoreOrder
        orders = []
        for i, item in enumerate(self.DUMMY_STORE_ITEMS):
            order = DummyStoreOrder(uid=SafeUid.gen(), item_id=i, total=item['price'], currency=item['currency'])
            orders.append(order)
            db.insert(order)
        return orders
