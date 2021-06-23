from cypherpunkpay.models.user import User
from test.unit.cypherpunkpay.cypherpunkpay_test_case import CypherpunkpayTestCase


class UserTest(CypherpunkpayTestCase):

    def test_instantiates(self):
        user = User(username='satoshi', password_hash='password hash')
        self.assertEqual(user.username, 'satoshi')
        self.assertEqual(user.password_hash, 'password hash')
        self.assertIsNotNone(user.created_at)
