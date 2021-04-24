import csv

from .. import tools

from .base import Format

__all__ = ['Fimi']


def iter_fimi_rows(bools):
    for row in bools:
        yield [i for i, value in enumerate(row) if value]


class FimiDialect(csv.Dialect):

    delimiter = ' '

    quotechar = escapechar = None
    quoting = csv.QUOTE_NONE

    lineterminator = '\n'

    strict = True


def dump_file(file, objects, properties, bools, *,  _serialized=None):
    rows = iter_fimi_rows(bools)
    tools.write_csv_file(file, rows, dialect=FimiDialect)


class Fimi(Format):

    suffix = '.dat'

    encoding = 'ascii'

    newline = ''

    dumps_rstrip = False

    dumpf = staticmethod(dump_file)
