#!/usr/bin/env python3

"""Measure time to create bigger lattice and profile it."""

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

context = concepts.load_cxt(SEGMENTS, encoding=ENCODING)
print(repr(context))

assert len(context.objects) == 143
assert len(context.properties) == 56

lattice = context.lattice
print(repr(lattice))

assert len(lattice) == 11_878

duration = time.perf_counter() - start
print(duration)

context = context.copy()

cProfile.run('context.lattice')
