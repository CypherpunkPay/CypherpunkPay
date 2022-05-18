# !!! READ BEFORE MODIFYING !!!
#
# This module namespace is merged GLOBALLY by importing * from this file.
# Be careful while introducing new names to this namespace.
#
# The rationale behind this module is import pragmatism.
# We want immediate availability of the most commonly used names.

import logging as log

import os
import sys
import re
import datetime
from datetime import timedelta
import json
from json import JSONDecodeError
from decimal import Decimal

from typing import List, Dict

from pprint import pprint

from pathlib import Path

from cypherpunkpay.tools.utc import utc_now, utc_ago, utc_from_now, utc_from_iso
from cypherpunkpay.tools.iter import first
