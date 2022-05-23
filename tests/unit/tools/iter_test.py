from cypherpunkpay.tools.iter import first


class IterTest:

    def test_first(self):
        # Empty iterable
        assert first(lambda _: True, []) is None
        assert first(lambda _: True, set()) is None
        assert first(lambda _: True, tuple()) is None
        assert first(lambda _: True, {}) is None

        # Iterable with falsy values
        assert first(lambda x: x, [None, False, []]) is None

        # Returns default value
        assert first(lambda x: x, [None, None, None], default='default value') == 'default value'
        assert first(lambda x: x, [None, None, None], default=False) is False

        # Returns first value meeting condition
        assert first(lambda x: x and x > 0, (None, -7, 0, 7, 10, 5), default=10) == 7
