from collections.abc import Mapping
import functools

from .base import ContextArgs, Format

__all__ = ['iter_cxt_lines', 'Cxt']

SYMBOLS = {False: '.', True: 'X'}


def iter_cxt_lines(objects, properties, bools, *,
                   symbols: Mapping[bool, str] = SYMBOLS):
    assert len(objects) == len(bools)
    assert {len(properties)} == set(map(len, bools))

    yield 'B'
    yield ''
    yield f'{len(objects):d}'
    yield f'{len(properties):d}'
    yield ''

    yield from objects
    yield from properties

    for row in bools:
        yield ''.join(symbols[value] for value in row)


class Cxt(Format):
    """Formal context in the classic CXT format."""

    suffix = '.cxt'

    dumps_rstrip = False

    symbols = SYMBOLS

    values = {s: b for b, s in symbols.items()}

    @classmethod
    def loadf(cls, file):
        source = file.read().strip()
        b, yx, table = source.split('\n\n')
        y, x = map(int, yx.split())
        lines = [l.strip() for l in table.strip().split('\n')]
        objects = lines[:y]
        properties = lines[y:y + x]
        bools = [tuple(map(cls.values.__getitem__, l))
                 for l in lines[y + x:]]
        return ContextArgs(objects, properties, bools)

    @classmethod
    def dumpf(cls, file, objects, properties, bools, *, _serialized=None):
        write = functools.partial(print, file=file)
        for line in iter_cxt_lines(objects, properties, bools,
                                   symbols=cls.symbols):
            write(line)
