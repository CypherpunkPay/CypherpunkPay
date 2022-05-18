import datetime
import pytz


def utc_now():
    return datetime.datetime.now(pytz.utc)


def utc_ago(
    days=0, seconds=0, microseconds=0,
    milliseconds=0, minutes=0, hours=0, weeks=0) -> datetime.datetime:
    return utc_now() - datetime.timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks
    )


def utc_from_now(
    days=0, seconds=0, microseconds=0,
    milliseconds=0, minutes=0, hours=0, weeks=0) -> datetime.datetime:
    return utc_now() + datetime.timedelta(
        days=days,
        seconds=seconds,
        microseconds=microseconds,
        milliseconds=milliseconds,
        minutes=minutes,
        hours=hours,
        weeks=weeks
    )


def utc_from_iso(s: str) -> datetime.datetime:
    if '+' in s:
        raise ValueError('Please do NOT pass the timezone. This method enforces UTC.')
    s += '+00:00'  # enforce UTC
    return datetime.datetime.fromisoformat(s)
