#!/usr/bin/env python3

"""Measure time to create bigger lattice and profile lindig.lattice() with it."""

import cProfile
import os
import pathlib
import sys
import time

sys.path.insert(1, os.pardir)

import concepts  # noqa: E402

SEGMENTS = pathlib.Path(os.pardir) / 'examples' / 'segments.cxt'

ENCODING = 'utf-8'


start = time.perf_counter()

context = concepts.load(SEGMENTS, encoding=ENCODING)
print(f'{context!r:}')

assert len(context.objects) == 143, f'{len(context.object):_d} != 143'
assert len(context.properties) == 56, f'{len(context.properties):_d} != 56'

lattice = context.lattice
print(f'{lattice!r:}')

assert len(lattice) == 11_878, f'{len(lattice):_d} != 11_878'

duration = time.perf_counter() - start
print(f'{duration:.1f} seconds')

assert duration <= 40, f'{duration:.1f} > 40'

context = context.copy()

cProfile.run('context.lattice')
