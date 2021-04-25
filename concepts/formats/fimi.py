import csv

from .. import tools

from .base import Format

__all__ = ['Fimi',
           'read_concepts_dat', 'write_concepts_dat']


class FimiDialect(csv.Dialect):

    delimiter = ' '

    quotechar = escapechar = None
    quoting = csv.QUOTE_NONE

    lineterminator = '\n'

    strict = True

def iter_fimi_rows(bools):
    for row in bools:
        yield [i for i, value in enumerate(row) if value]

def dump_file(file, objects, properties, bools, *, _serialized=None):
    rows = iter_fimi_rows(bools)
    tools.write_csv_file(file, rows, dialect=FimiDialect)


class Fimi(Format):

    suffix = '.dat'

    encoding = 'ascii'

    newline = ''

    dumps_rstrip = False

    dumpf = staticmethod(dump_file)

    dialect = FimiDialect


def read_concepts_dat(path, encoding=Fimi.encoding, newline=Fimi.newline):
    rows = tools.csv_iterrows(path, encoding=encoding, newline=newline,
                              dialect=Fimi.dialect)
    for values in rows:
        yield tuple(map(int, values))


def write_concepts_dat(path, iterconcepts, *, extents: bool = False,
                       encoding=Fimi.encoding,
                       newline=Fimi.newline):
    rows = ((list(extent.iter_set()) for extent, _ in iterconcepts) if extents
            else (list(intent.iter_set()) for _, intent in iterconcepts))

    with open(path, 'w', encoding=encoding, newline=newline) as f:
        tools.write_csv_file(f, rows, dialect=Fimi.dialect)

