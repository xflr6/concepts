#!/usr/bin/env python3

"""Download and convert dataset, save to examples/, try lattice generation."""

from collections.abc import Mapping
import csv
import os
import pathlib
import shutil
import sys
import time
import urllib.request

sys.path.insert(0, os.pardir)

import concepts  # noqa: E402
from concepts import formats  # noqa: E402
from concepts import tools  # noqa: E402

URL = ('https://raw.githubusercontent.com/fivethirtyeight/data'
       '/master/bob-ross/elements-by-episode.csv')

CSV = pathlib.Path(URL.rpartition('/')[2])

CSV_SHA256 = '42045c8b8aaa8296095d6b294927fb9d0f73a57259f59b560c375844c0fe01cf'

OPEN_KWARGS = {'encoding': 'ascii', 'newline': '\n'}

CXT = CSV.with_suffix('.cxt')

TARGET = pathlib.Path(os.pardir) / 'examples' / 'bob-ross.cxt'


def read_episodes(path, *,
                  dialect: csv.Dialect | type[csv.Dialect] | str = csv.excel,
                  symbols: Mapping[str, bool] = {'0': False, '1': True}):
    with path.open(**OPEN_KWARGS) as f:
        reader = csv.reader(f, dialect=dialect)
        episode, _, *elements = next(reader)  # omit TITLE column
        yield [episode] + elements
        for episode, _, *elements in reader:
            yield [episode] + [symbols[e] for e in elements]


if not CSV.exists():
    print(URL)
    urllib.request.urlretrieve(URL, CSV)
    assert CSV.stat().st_size

assert tools.sha256sum(CSV) == CSV_SHA256, f'{tools.sha256sum(CSV)} != {CSV_SHA256}'

if not CXT.exists():
    header, *episodes = read_episodes(CSV)
    bools = [bools for _, *bools in episodes]
    lines = formats.iter_cxt_lines(objects=[e[0] for e in episodes],
                                   properties=header[1:],
                                   bools=bools)
    print(CXT)
    tools.write_lines(CXT, lines, **OPEN_KWARGS)
    print(TARGET)
    shutil.copy(CXT, TARGET)

start = time.perf_counter_ns()

context = concepts.load_cxt(CXT)
print(f'{context!r}')

assert context.shape == (403, 67), f'{context.shape} != (403, 67)'

lattice = context.lattice
print(f'{lattice!r}')

assert len(lattice) == 3_463, f'{len(lattice):_d} != 3_463'

duration = (time.perf_counter_ns() - start) / 1_000_000_000
print(f'{duration:.1f} seconds')

# concepts 0.9.2, 2.2 GHz Intel i3-2330M CPU, 4GB RAM: 189s (PY2), 132s (PY3)
# concepts 0.10.dev0, 2.2 GHz Intel i3-2330M CPU, 4GB RAM: 32s
