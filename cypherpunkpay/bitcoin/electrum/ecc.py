# Electrum - lightweight Bitcoin client
# Copyright (C) 2018 The Electrum developers
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import hashlib
import functools
import copy
from typing import Union, Tuple, Optional

import ecdsa
from ecdsa.ecdsa import curve_secp256k1, generator_secp256k1
from ecdsa.curves import SECP256k1
from ecdsa.ellipticcurve import Point
from ecdsa.util import string_to_number, number_to_string

from .util import bfh, bh2u, assert_bytes
from .crypto import sha256d
from . import msqr
from . import constants

CURVE_ORDER = SECP256k1.order


def generator():
    return ECPubkey.from_point(generator_secp256k1)


def point_at_infinity():
    return ECPubkey(None)


def sig_string_from_der_sig(der_sig: bytes, order=CURVE_ORDER) -> bytes:
    r, s = ecdsa.util.sigdecode_der(der_sig, order)
    return ecdsa.util.sigencode_string(r, s, order)


def der_sig_from_sig_string(sig_string: bytes, order=CURVE_ORDER) -> bytes:
    r, s = ecdsa.util.sigdecode_string(sig_string, order)
    return ecdsa.util.sigencode_der_canonize(r, s, order)


def der_sig_from_r_and_s(r: int, s: int, order=CURVE_ORDER) -> bytes:
    return ecdsa.util.sigencode_der_canonize(r, s, order)


def get_r_and_s_from_der_sig(der_sig: bytes, order=CURVE_ORDER) -> Tuple[int, int]:
    r, s = ecdsa.util.sigdecode_der(der_sig, order)
    return r, s


def get_r_and_s_from_sig_string(sig_string: bytes, order=CURVE_ORDER) -> Tuple[int, int]:
    r, s = ecdsa.util.sigdecode_string(sig_string, order)
    return r, s


def sig_string_from_r_and_s(r: int, s: int, order=CURVE_ORDER) -> bytes:
    return ecdsa.util.sigencode_string_canonize(r, s, order)


def point_to_ser(point, compressed=True) -> Optional[bytes]:
    if isinstance(point, tuple):
        assert len(point) == 2, f'unexpected point: {point}'
        x, y = point
    else:
        x, y = point.x(), point.y()
    if x is None or y is None:  # infinity
        return None
    if compressed:
        return bfh(('%02x' % (2+(y&1))) + ('%064x' % x))
    return bfh('04'+('%064x' % x)+('%064x' % y))


def get_y_coord_from_x(x: int, *, odd: bool) -> int:
    curve = curve_secp256k1
    _p = curve.p()
    _a = curve.a()
    _b = curve.b()
    x = x % _p
    y2 = (pow(x, 3, _p) + _a * x + _b) % _p
    y = msqr.modular_sqrt(y2, _p)
    if curve.contains_point(x, y):
        if odd == bool(y & 1):
            return y
        return _p - y
    raise InvalidECPointException()


def ser_to_point(ser: bytes) -> Tuple[int, int]:
    if ser[0] not in (0x02, 0x03, 0x04):
        raise ValueError('Unexpected first byte: {}'.format(ser[0]))
    if ser[0] == 0x04:
        return string_to_number(ser[1:33]), string_to_number(ser[33:])
    x = string_to_number(ser[1:])
    odd = ser[0] == 0x03
    return x, get_y_coord_from_x(x, odd=odd)


def _ser_to_python_ecdsa_point(ser: bytes) -> ecdsa.ellipticcurve.Point:
    x, y = ser_to_point(ser)
    try:
        return Point(curve_secp256k1, x, y, CURVE_ORDER)
    except:
        raise InvalidECPointException()


class InvalidECPointException(Exception):
    """e.g. not on curve, or infinity"""


class _MyVerifyingKey(ecdsa.VerifyingKey):
    @classmethod
    def from_signature(klass, sig, recid, h, curve):  # TODO use libsecp??
        """ See http://www.secg.org/download/aid-780/sec1-v2.pdf, chapter 4.1.6 """
        from ecdsa import util, numbertheory
        from . import msqr
        curveFp = curve.curve
        G = curve.generator
        order = G.order()
        # extract r,s from signature
        r, s = util.sigdecode_string(sig, order)
        # 1.1
        x = r + (recid//2) * order
        # 1.3
        alpha = ( x * x * x  + curveFp.a() * x + curveFp.b() ) % curveFp.p()
        beta = msqr.modular_sqrt(alpha, curveFp.p())
        y = beta if (beta - recid) % 2 == 0 else curveFp.p() - beta
        # 1.4 the constructor checks that nR is at infinity
        try:
            R = Point(curveFp, x, y, order)
        except:
            raise InvalidECPointException()
        # 1.5 compute e from message:
        e = string_to_number(h)
        minus_e = -e % order
        # 1.6 compute Q = r^-1 (sR - eG)
        inv_r = numbertheory.inverse_mod(r,order)
        try:
            Q = inv_r * ( s * R + minus_e * G )
        except:
            raise InvalidECPointException()
        return klass.from_public_point( Q, curve )


class _MySigningKey(ecdsa.SigningKey):
    """Enforce low S values in signatures"""

    def sign_number(self, number, entropy=None, k=None):
        r, s = ecdsa.SigningKey.sign_number(self, number, entropy, k)
        if s > CURVE_ORDER//2:
            s = CURVE_ORDER - s
        return r, s


class _PubkeyForPointAtInfinity:
    point = ecdsa.ellipticcurve.INFINITY


@functools.total_ordering
class ECPubkey(object):

    def __init__(self, b: Optional[bytes]):
        if b is not None:
            assert_bytes(b)
            point = _ser_to_python_ecdsa_point(b)
            self._pubkey = ecdsa.ecdsa.Public_key(generator_secp256k1, point)
        else:
            self._pubkey = _PubkeyForPointAtInfinity()

    @classmethod
    def from_sig_string(cls, sig_string: bytes, recid: int, msg_hash: bytes):
        assert_bytes(sig_string)
        if len(sig_string) != 64:
            raise Exception('Wrong encoding')
        if recid < 0 or recid > 3:
            raise ValueError('recid is {}, but should be 0 <= recid <= 3'.format(recid))
        ecdsa_verifying_key = _MyVerifyingKey.from_signature(sig_string, recid, msg_hash, curve=SECP256k1)
        ecdsa_point = ecdsa_verifying_key.pubkey.point
        return ECPubkey.from_point(ecdsa_point)

    @classmethod
    def from_signature65(cls, sig: bytes, msg_hash: bytes):
        if len(sig) != 65:
            raise Exception("Wrong encoding")
        nV = sig[0]
        if nV < 27 or nV >= 35:
            raise Exception("Bad encoding")
        if nV >= 31:
            compressed = True
            nV -= 4
        else:
            compressed = False
        recid = nV - 27
        return cls.from_sig_string(sig[1:], recid, msg_hash), compressed

    @classmethod
    def from_point(cls, point):
        _bytes = point_to_ser(point, compressed=False)  # faster than compressed
        return ECPubkey(_bytes)

    def get_public_key_bytes(self, compressed=True):
        if self.is_at_infinity(): raise Exception('point is at infinity')
        return point_to_ser(self.point(), compressed)

    def get_public_key_hex(self, compressed=True):
        return bh2u(self.get_public_key_bytes(compressed))

    def point(self) -> Tuple[int, int]:
        return self._pubkey.point.x(), self._pubkey.point.y()

    def __repr__(self):
        return f"<ECPubkey {self.get_public_key_hex()}>"

    def __mul__(self, other: int):
        if not isinstance(other, int):
            raise TypeError('multiplication not defined for ECPubkey and {}'.format(type(other)))
        ecdsa_point = self._pubkey.point * other
        return self.from_point(ecdsa_point)

    def __rmul__(self, other: int):
        return self * other

    def __add__(self, other):
        if not isinstance(other, ECPubkey):
            raise TypeError('addition not defined for ECPubkey and {}'.format(type(other)))
        ecdsa_point = self._pubkey.point + other._pubkey.point
        return self.from_point(ecdsa_point)

    def __eq__(self, other):
        return self._pubkey.point.x() == other._pubkey.point.x() \
                and self._pubkey.point.y() == other._pubkey.point.y()

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self._pubkey.point.x())

    def __lt__(self, other):
        if not isinstance(other, ECPubkey):
            raise TypeError('comparison not defined for ECPubkey and {}'.format(type(other)))
        return self._pubkey.point.x() < other._pubkey.point.x()

    def __deepcopy__(self, memo: dict = None):
        # note: This custom deepcopy implementation needed as copy.deepcopy(self._pubkey) raises.
        if memo is None: memo = {}
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == '_pubkey' and not self.is_at_infinity():
                point = _ser_to_python_ecdsa_point(self.get_public_key_bytes(compressed=False))
                _pubkey_copy = ecdsa.ecdsa.Public_key(generator_secp256k1, point)
                setattr(result, k, _pubkey_copy)
            else:
                setattr(result, k, copy.deepcopy(v, memo))
        return result

    def verify_message_for_address(self, sig65: bytes, message: bytes, algo=lambda x: sha256d(msg_magic(x))) -> None:
        assert_bytes(message)
        h = algo(message)
        public_key, compressed = self.from_signature65(sig65, h)
        # check public key
        if public_key != self:
            raise Exception("Bad signature")
        # check message
        self.verify_message_hash(sig65[1:], h)

    def verify_message_hash(self, sig_string: bytes, msg_hash: bytes) -> None:
        assert_bytes(sig_string)
        if len(sig_string) != 64:
            raise Exception('Wrong encoding')
        ecdsa_point = self._pubkey.point
        verifying_key = _MyVerifyingKey.from_public_point(ecdsa_point, curve=SECP256k1)
        verifying_key.verify_digest(sig_string, msg_hash, sigdecode=ecdsa.util.sigdecode_string)

    @classmethod
    def order(cls):
        return CURVE_ORDER

    def is_at_infinity(self):
        return self == point_at_infinity()

    @classmethod
    def is_pubkey_bytes(cls, b: bytes):
        try:
            ECPubkey(b)
            return True
        except:
            return False


def msg_magic(message: bytes) -> bytes:
    from .bitcoin import var_int
    length = bfh(var_int(len(message)))
    return b"\x18Bitcoin Signed Message:\n" + length + message


def verify_signature(pubkey: bytes, sig: bytes, h: bytes) -> bool:
    try:
        ECPubkey(pubkey).verify_message_hash(sig, h)
    except:
        return False
    return True


def verify_message_with_address(address: str, sig65: bytes, message: bytes, *, net=None):
    from .bitcoin import pubkey_to_address
    assert_bytes(sig65, message)
    if net is None: net = constants.net
    try:
        h = sha256d(msg_magic(message))
        public_key, compressed = ECPubkey.from_signature65(sig65, h)
        # check public key using the address
        pubkey_hex = public_key.get_public_key_hex(compressed)
        for txin_type in ['p2pkh','p2wpkh','p2wpkh-p2sh']:
            addr = pubkey_to_address(txin_type, pubkey_hex, net=net)
            if address == addr:
                break
        else:
            raise Exception("Bad signature")
        # check message
        public_key.verify_message_hash(sig65[1:], h)
        return True
    except Exception as e:
        return False


def is_secret_within_curve_range(secret: Union[int, bytes]) -> bool:
    if isinstance(secret, bytes):
        secret = string_to_number(secret)
    return 0 < secret < CURVE_ORDER


class ECPrivkey(ECPubkey):

    def __init__(self, privkey_bytes: bytes):
        assert_bytes(privkey_bytes)
        if len(privkey_bytes) != 32:
            raise Exception('unexpected size for secret. should be 32 bytes, not {}'.format(len(privkey_bytes)))
        secret = string_to_number(privkey_bytes)
        if not is_secret_within_curve_range(secret):
            raise InvalidECPointException('Invalid secret scalar (not within curve order)')
        self.secret_scalar = secret

        point = generator_secp256k1 * secret
        super().__init__(point_to_ser(point))

    @classmethod
    def from_secret_scalar(cls, secret_scalar: int):
        secret_bytes = number_to_string(secret_scalar, CURVE_ORDER)
        return ECPrivkey(secret_bytes)

    @classmethod
    def from_arbitrary_size_secret(cls, privkey_bytes: bytes):
        """This method is only for legacy reasons. Do not introduce new code that uses it.
        Unlike the default constructor, this method does not require len(privkey_bytes) == 32,
        and the secret does not need to be within the curve order either.
        """
        return ECPrivkey(cls.normalize_secret_bytes(privkey_bytes))

    @classmethod
    def normalize_secret_bytes(cls, privkey_bytes: bytes) -> bytes:
        scalar = string_to_number(privkey_bytes) % CURVE_ORDER
        if scalar == 0:
            raise Exception('invalid EC private key scalar: zero')
        privkey_32bytes = number_to_string(scalar, CURVE_ORDER)
        return privkey_32bytes

    def __repr__(self):
        return f"<ECPrivkey {self.get_public_key_hex()}>"

    @classmethod
    def generate_random_key(cls):
        randint = ecdsa.util.randrange(CURVE_ORDER)
        ephemeral_exponent = number_to_string(randint, CURVE_ORDER)
        return ECPrivkey(ephemeral_exponent)

    def get_secret_bytes(self) -> bytes:
        return number_to_string(self.secret_scalar, CURVE_ORDER)

    def sign(self, data: bytes, sigencode=None, sigdecode=None) -> bytes:
        if sigencode is None:
            sigencode = sig_string_from_r_and_s
        if sigdecode is None:
            sigdecode = get_r_and_s_from_sig_string
        private_key = _MySigningKey.from_secret_exponent(self.secret_scalar, curve=SECP256k1)
        def sig_encode_r_s(r, s, order):
            return r, s
        r, s = private_key.sign_digest_deterministic(data, hashfunc=hashlib.sha256, sigencode=sig_encode_r_s)
        counter = 0
        while r >= 2**255:  # grind for low R value https://github.com/bitcoin/bitcoin/pull/13666
            counter += 1
            extra_entropy = int.to_bytes(counter, 32, 'little')
            r, s = private_key.sign_digest_deterministic(data, hashfunc=hashlib.sha256, sigencode=sig_encode_r_s, extra_entropy=extra_entropy)
        sig = sigencode(r, s, CURVE_ORDER)
        public_key = private_key.get_verifying_key()
        if not public_key.verify_digest(sig, data, sigdecode=sigdecode):
            raise Exception('Sanity check verifying our own signature failed.')
        return sig

    def sign_transaction(self, hashed_preimage: bytes) -> bytes:
        return self.sign(hashed_preimage,
                         sigencode=der_sig_from_r_and_s,
                         sigdecode=get_r_and_s_from_der_sig)


def construct_sig65(sig_string: bytes, recid: int, is_compressed: bool) -> bytes:
    comp = 4 if is_compressed else 0
    return bytes([27 + recid + comp]) + sig_string
