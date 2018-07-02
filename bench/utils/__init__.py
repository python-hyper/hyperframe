import os
import struct
import sys
import time
import random
import warnings

# Seed was randomly generated with 128 bytes of entropy because old Python
# versions have low initial entropy when seeds have too many NULL bytes.
_SEED = open(os.path.join(os.path.dirname(__file__), "seed"), "rb").read()
_RANDOM = random.Random(_SEED)


def reset_rng():
    global _RANDOM
    _RANDOM = random.Random(_SEED)


def get_bool():
    return True if get_int(0, 1) == 1 else False


def get_int(l, h):
    return _RANDOM.randint(l, h)


def get_bytes(n):
    return b''.join([struct.pack("@B", _RANDOM.randint(0, 255)) for _ in range(n)])
