import csv

from .base import Format

__all__ = ['Fimi']

ENCODING = 'ascii'


def write_csv(file, rows, *, header=None, dialect='excel', encoding=ENCODING):
    writer = csv.writer(file, dialect=dialect)
    if header is not None:
        writer.writerow(header)
    writer.writerows(rows)


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
    write_csv(file, rows, dialect=FimiDialect)


class Fimi(Format):

    suffix = '.dat'

    encoding = ENCODING

    newline = ''

    dumps_rstrip = False

    dumpf = staticmethod(dump_file)
