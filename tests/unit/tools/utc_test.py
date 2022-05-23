import datetime

from cypherpunkpay.tools.utc import utc_now, utc_ago, utc_from_now, utc_from_iso


class UtcTest:

    def test_utc_from_iso(self):
        dt = utc_from_iso('2022-02-11 16:43:25')
        assert dt.tzname() == 'UTC'
        assert dt.year == 2022
        assert dt.month == 2
        assert dt.day == 11
        assert dt.hour == 16
        assert dt.minute == 43
        assert dt.second == 25

        import pytest
        with pytest.raises(ValueError):
            utc_from_iso('2022-02-11 16:43:25+01:00')

    def test_utc_now(self):
        now = utc_now()
        assert now.tzname() == 'UTC'                      # has UTC timezone
        assert now.utcoffset() == datetime.timedelta(0)   # is not naive as per https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive

    def test_utc_ago(self):
        min_ago_17 = utc_now() - datetime.timedelta(minutes=17)
        min_ago_18 = utc_ago(minutes=18)
        min_ago_19 = utc_now() - datetime.timedelta(minutes=19)
        assert min_ago_18 < min_ago_17
        assert min_ago_18 < min_ago_17
        assert min_ago_19 < min_ago_18
