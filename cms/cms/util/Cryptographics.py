#!/usr/bin/python
# -*- coding: utf-8 -*-

# Programming contest management system
# Copyright © 2010-2011 Giovanni Mascellani <mascellani@poisson.phc.unipi.it>
# Copyright © 2010-2011 Stefano Maggiolo <s.maggiolo@gmail.com>
# Copyright © 2010-2011 Matteo Boscariol <boscarim@hotmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from Crypto.Cipher import AES
#from Crypto import Random
import base64
import binascii
import random

from cms.async import Config
secret_key_unhex = binascii.unhexlify(Config.secret_key)


def get_random_key():
    """Generate 16 random bytes, safe to be used as AES key.

    """
    # Bad hack: some older version of Crypto do not support Random
    #return Random.get_random_bytes(16)
    return binascii.unhexlify("%032x" % random.getrandbits(16 * 8))


def get_hex_random_key():
    """Generate 16 random bytes, safe to be used as AES key.
    Return it encoded in hexadecimal.

    """
    return binascii.hexlify(get_random_key())


def get_encryption_alphabet():
    """Return the alphabet used by cryptograms generated by
    encrypt_string and encrypt_number.

    """
    return "a-zA-Z0-9._-"


def encrypt_string(string, key=None):
    """Encrypt the string s num with the 16-bytes key. Moreover, it
    encrypts it using a random salt, so that encrypting repeatedly the
    same string gives different outputs. This way no analisys can made
    when the same number is used in different contexts.  The generated
    string uses the alphabet { 'a', ..., 'z', 'A', ..., 'Z', '0', ...,
    '9', '.', '-', '_' }, so it is safe to use in URLs.

    This function pads the string s with NULL bytes, so any NULL byte
    at the end of the string will be discarded by decryption function.

    If key is not specified, it is obtained from the configuration.

    """
    if key is None:
        key = secret_key_unhex
    # FIXME - This could easily deplete the server entropy pool
    iv2 = get_random_key()
    dec = iv2 + string
    dec += "\x00" * (16 - ((len(dec) - 1) % 16 + 1))
    aes = AES.new(key, mode=AES.MODE_CBC)
    return base64.urlsafe_b64encode(aes.encrypt(dec)).replace('=', '.')


def decrypt_string(enc, key=None):
    """Decrypt a string encrypted with encrypt_string.

    If key is not specified, it is obtained from the configuration.

    """
    if key is None:
        key = secret_key_unhex
    aes = AES.new(key, mode=AES.MODE_CBC)
    try:
        return aes.decrypt(base64.urlsafe_b64decode(
            str(enc).replace('.', '=')))[16:].rstrip('\x00')
    except TypeError:
        raise ValueError('Could not decode from base64')
    except ValueError:
        raise ValueError('Wrong AES cryptogram length')


def encrypt_number(num, key=None):
    """Encrypt an integer number, with the same properties as encrypt_string().

    If key is not specified, it is obtained from the configuration.

    """
    hexnum = hex(num).replace('0x', '')
    return encrypt_string(hexnum, key)


def decrypt_number(enc, key=None):
    """Decrypt an integer number encrypted with encrypt_number().

    If key is not specified, it is obtained from the configuration.

    """
    return int(decrypt_string(enc, key), 16)
