import csv
import typing

from .base import ContextArgs, Format

__all__ = ['Csv']

SYMBOLS = {False: '', True: 'X'}

EXTRA_PARSING_SYMBOLS = {'0': False, '1': True}


class Csv(Format):
    """Formal context as CSV table."""

    suffix = '.csv'

    newline = ''

    dumps_rstrip = False

    dialect = csv.excel

    symbols = SYMBOLS

    values = {s: b for b, s in symbols.items()}
    values.update(EXTRA_PARSING_SYMBOLS)

    @classmethod
    def loadf(cls, file, *, dialect: typing.Optional[str] = None) -> ContextArgs:
        if dialect is None:
            dialect = cls.dialect
        reader = csv.reader(file, dialect=dialect)

        objects, bools = ([] for _ in range(2))

        _, *properties = next(reader)

        get_value = cls.values.__getitem__

        for obj, *symbols in reader:
            objects.append(obj)
            bools.append(tuple(map(get_value, symbols)))

        return ContextArgs(objects, properties, bools)

    @classmethod
    def dumpf(cls, file, objects, properties, bools,
              *, dialect: typing.Optional[str] = None,
              _serialized=None) -> None:
        if dialect is None:
            dialect = cls.dialect
        writer = csv.writer(file, dialect=dialect)

        symbool = cls.symbols.__getitem__

        writer.writerow([''] + list(properties))

        writer.writerows([o] + list(map(symbool, bs))
                         for o, bs in zip(objects, bools))
