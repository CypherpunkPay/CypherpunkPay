from cypherpunkpay.models.user import User


class UserTest:

    def test_instantiates(self):
        user = User(username='satoshi', password_hash='password hash')
        assert user.username == 'satoshi'
        assert user.password_hash == 'password hash'
        assert user.created_at is not None
