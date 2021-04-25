#!/usr/bin/env python3

"""Profile fcbo.fast_generate_from() with a bigger context."""

import cProfile
import os
import pathlib
import sys
import time

sys.path.insert(1, os.pardir)

import concepts  # noqa: E402
from concepts import algorithms  # noqa: E402

MUSHROOM = pathlib.Path(os.pardir) / 'examples' / 'mushroom.cxt'

ENCODING = 'ascii'


start = time.perf_counter()

context = concepts.load(MUSHROOM, encoding=ENCODING)
print(f'{context!r}')

assert len(context.objects) == 8_124,  f'{len(context.objects):_d)} != 8_124'
assert len(context.properties) == 128, f'{len(context.properties):_d} != 128'

n_concepts = sum(1 for _ in algorithms.fast_generate_from(context))
print(f'{n_concepts:_d} concepts')

assert n_concepts >= 150_000, f'{n_concepts:_d} < 150_000'

duration = time.perf_counter() - start
print(f'{duration:.1f} seconds')

assert duration <= 90, f'{duration:.1f} > 90'

cProfile.run('list(algorithms.fast_generate_from(context))')
