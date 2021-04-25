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
from concepts import formats  # noqa: E402

ROOT = pathlib.Path(os.pardir)

MUSHROOM =  ROOT / 'examples' / 'mushroom.cxt'

INTENTS =  ROOT / 'test-output' / f'{MUSHROOM.stem}-intents.dat'

ENCODING = 'ascii'


start = time.perf_counter()

context = concepts.load(MUSHROOM, encoding=ENCODING)
print(f'{context!r}')

assert len(context.objects) == 8_124,  f'{len(context.objects):_d)} != 8_124'
assert len(context.properties) == 128, f'{len(context.properties):_d} != 128'

result = algorithms.get_concepts(context)
print(f'{len(result):_d} concepts')

result.tofile(INTENTS)
print(INTENTS, f'{INTENTS.stat().st_size:_d} bytes')

duration = time.perf_counter() - start
print(f'{duration:.1f} seconds')

assert len(result) >= 150_000, f'{len(result):_d} < 150_000'

assert duration <= 90, f'{duration:.1f} > 90'

cProfile.run('list(algorithms.fast_generate_from(context))',
             sort='tottime')
