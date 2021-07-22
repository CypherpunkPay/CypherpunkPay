import logging as log

import os
import pytz
import sys
import re

import datetime
from datetime import timedelta, timezone

from abc import ABC, abstractmethod
import collections.abc

import json
from json import JSONDecodeError

import decimal
from decimal import Decimal

from typing import List, Dict

from pprint import pprint

from pathlib import Path

from types import SimpleNamespace


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


def is_blank(s: str) -> bool:
    if s and s.strip():
        # s is not None AND s is not empty or blank
        return False
    # s is None OR s is empty or blank
    return True


def remove_file_if_present(path: str) -> None:
    try:
        os.remove(path)
        log.debug(f'Removed {path}')
    except FileNotFoundError:
        pass


def deep_dict_merge(*args, add_keys=True):
    assert len(args) >= 2, "dict_merge requires at least two dicts to merge"
    rtn_dct = args[0].copy()
    merge_dicts = args[1:]
    for merge_dct in merge_dicts:
        if add_keys is False:
            merge_dct = {key: merge_dct[key] for key in set(rtn_dct).intersection(set(merge_dct))}
        for k, v in merge_dct.items():
            if not rtn_dct.get(k):
                rtn_dct[k] = v
            elif k in rtn_dct and type(v) != type(rtn_dct[k]):
                raise TypeError(f"Overlapping keys exist with different types: original is {type(rtn_dct[k])}, new value is {type(v)}")
            elif isinstance(rtn_dct[k], dict) and isinstance(merge_dct[k], collections.abc.Mapping):
                rtn_dct[k] = deep_dict_merge(rtn_dct[k], merge_dct[k], add_keys=add_keys)
            elif isinstance(v, list):
                for list_value in v:
                    if list_value not in rtn_dct[k]:
                        rtn_dct[k].append(list_value)
            else:
                rtn_dct[k] = v
    return rtn_dct


def first_true(iterable, default=False, pred=None):
    """Returns the first true value in the iterable.

    If no true value is found, returns *default*

    If *pred* is not None, returns the first item
    for which pred(item) is true.

    """
    # first_true([a,b,c], x) --> a or b or c or x
    # first_true([a,b], x, f) --> a if f(a) else b if f(b) else x
    return next(filter(pred, iterable), default)


def is_local_network(url: str) -> bool:
    from urllib.parse import urlparse
    host = urlparse(url).hostname
    if host == 'localhost':
        return True
    from ipaddress import ip_address
    try:
        ip = ip_address(host)
        return ip.is_link_local or ip.is_private
    except ValueError:
        # Neither IPv4 nor IPv6. Probably domain or onion.
        pass
    return False


def get_domain_or_ip(url: str) -> str:
    from urllib.parse import urlparse
    return urlparse(url).hostname


# This is used to skip certificate based authentication when connecting to LND
# We assume authentication to network level for example 1) localhost, 2) onion, 3) wireguard
def disable_unverified_certificate_warnings():
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
