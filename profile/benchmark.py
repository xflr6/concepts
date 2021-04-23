# benchmark.py - benchmark time to create bigger lattice and profile it

import os
import sys
import time

sys.path.insert(1, os.pardir)

import concepts  # noqa: E402


start = time.perf_counter()

c = concepts.load_cxt('segments.cxt', encoding='utf-8')

print(repr(c.lattice))

duration = time.perf_counter() - start
print(duration)


import cProfile as Profile  # noqa: E402

c = concepts.load_cxt('segments.cxt', encoding='utf-8')

Profile.run('c.lattice')
