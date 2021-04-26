import csv
import typing

from .. import tools

from .base import ContextArgs, Format

__all__ = ['Csv']

SYMBOLS = {False: {False: '', True: 'X'},
           True: {False: 0, True: 1}}

VALUES = {as_int: {str(s): v for v, s in symbols.items()}
          for as_int, symbols in SYMBOLS.items()}

VALUES[None] = {s: v
                for values in VALUES.values()
                for s, v in values.items()}

assert len(VALUES[None]) == 4


class Csv(Format):
    """Formal context as CSV table."""

    suffix = '.csv'

    newline = ''

    dumps_rstrip = False

    dialect = csv.excel

    symbols = SYMBOLS

    values = VALUES

    @classmethod
    def loadf(cls, file, *, bools_as_int: typing.Optional[bool] = None,
              dialect: typing.Optional[str] = None) -> ContextArgs:
        if dialect is None:
            dialect = cls.dialect
        reader = csv.reader(file, dialect=dialect)

        objects, bools = ([] for _ in range(2))

        _, *properties = next(reader)

        get_value = cls.values[bools_as_int].__getitem__

        for obj, *symbols in reader:
            objects.append(obj)
            bools.append(tuple(map(get_value, symbols)))

        return ContextArgs(objects, properties, bools)

    @classmethod
    def dumpf(cls, file, objects, properties, bools,
              *, object_header: typing.Optional[str] = None,
              bools_as_int: bool = False,
              dialect: typing.Optional[str] = None,
              _serialized=None) -> None:
        if dialect is None:
            dialect = cls.dialect

        header = [object_header] + list(properties)

        symbool = cls.symbols[bools_as_int].__getitem__

        rows = ([o] + list(map(symbool, bs))
                for o, bs in zip(objects, bools))

        tools.write_csv_file(file, rows, header=header, dialect=dialect)
