import os

from decimal import Decimal
from pathlib import Path
from typing import Iterable
from pprint import pprint

import pytest


def this_dir(python_script_path):
    return Path(os.path.dirname(os.path.realpath(python_script_path)))


# We use this to:
#   * more explicitly assert emptiness
#   * while disallowing None
#   * and while expecting iterable (and not another type)
def is_empty(iterable: Iterable) -> bool:
    if not isinstance(iterable, Iterable):
        raise ValueError(f'Expected value to be iterable: {iterable}')
    return not iterable  # Pythonic way to check for emptiness
