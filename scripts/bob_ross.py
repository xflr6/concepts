# bob_ross.py - download Bob Ross dataset and save as examples/bob_ross.cxt

import csv
import pathlib
import os
import shutil
import sys
import urllib.request

sys.path.insert(0, os.pardir)

import concepts
from concepts import formats
from concepts import tools

URL = ('https://raw.githubusercontent.com/fivethirtyeight/data'
       '/master/bob-ross/elements-by-episode.csv')

CSV = pathlib.Path(URL.rpartition('/')[2])

OPEN_KWARGS = {'encoding': 'ascii', 'newline': '\n'}

DIALECT = 'excel'

FLAGS = {'0': False, '1': True}

CXT = CSV.with_suffix('.cxt')

CSV_CONTEXT = CSV.with_name(f'{CSV.stem}-cxt{CSV.suffix}')


def read_episodes(path, *, dialect: str = DIALECT):
    with path.open(**OPEN_KWARGS) as f:
        reader = csv.reader(f, dialect=dialect)
        episode, _, *elements = next(reader)  # omit TITLE column
        yield [episode] + elements
        for episode, _, *elements in reader:
            yield [episode] + [FLAGS[e] for e in elements]


if not CSV.exists():
    urllib.request.urlretrieve(URL, CSV)
    assert CSV.stat().st_size

if not all(path.exists() for path in (CXT, CSV_CONTEXT)):
    header, *episodes = read_episodes(CSV)
    bools = [bools for _, *bools in episodes]
    lines = formats.iter_cxt_lines(objects=[e[0] for e in episodes],
                                   properties=header[1:],
                                   bools=bools)
    tools.write_lines(CXT, lines, **OPEN_KWARGS)

assert tools.sha256sum(CSV) == '42045c8b8aaa8296095d6b294927fb9d0f73a57259f59b560c375844c0fe01cf'

context = concepts.load_cxt(CXT)

assert len(context.objects) == 403

assert len(context.properties) == 67

context.tofile(CSV_CONTEXT, frmat='csv')

shutil.copy(CXT, pathlib.Path('..') / 'examples' / 'bob_ross.cxt')
