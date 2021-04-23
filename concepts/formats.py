# formats.py - parse and serialize FCA context tables

"""Parse and serialize formal contexts in different formats."""

import contextlib
import csv
import io
import os

from . import tools

__all__ = ['Format']


class FormatMeta(type):
    """Collect and retrieve concrete ``Format`` subclasses by name."""

    _map = {}

    by_suffix = {}

    def __init__(self, name, bases, dct):  # noqa: N804
        if not dct.get('__abstract__'):
            if 'name' not in dct:
                self.name = name.lower()
            if 'suffix' in dct:
                self.by_suffix[self.suffix] = self.name
            self._map[self.name] = self

    def __getitem__(self, name):  # noqa: N804
        try:
            return self._map[name.lower()]
        except KeyError:
            raise KeyError(f'{self!r} unknown format: {name!r}')

    def infer_format(self, filename, frmat=None):  # noqa: N804
        _, suffix = os.path.splitext(filename)
        try:
            return self.by_suffix[suffix.lower()]
        except KeyError:
            raise ValueError('cannot infer file format from filename suffix'
                             f' {suffix!r}, please specify ``frmat``')


class Format(metaclass=FormatMeta):
    """Parse and serialize formal contexts in a specific string format."""

    __abstract__ = True

    encoding = None

    normalize_newlines = True

    @staticmethod
    def loads(source, **kwargs):
        """Parse source string and return ``(objects, properties, bools)``."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def dumps(objects, properties, bools, **kwargs):
        """Serialize ``(objects, properties, bools)`` and return string."""
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def load(cls, filename, encoding):
        """Load and parse serialized objects, properties, bools from file."""
        if encoding is None:
            encoding = cls.encoding

        with open(filename, 'r', encoding=encoding) as fd:
            source = fd.read()

        if cls.normalize_newlines:
            source = source.replace('\r\n', '\n').replace('\r', '\n')
        return cls.loads(source)

    @classmethod
    def dump(cls, filename, objects, properties, bools, encoding):
        """Write serialized objects, properties, bools to file."""
        if encoding is None:
            encoding = cls.encoding

        source = cls.dumps(objects, properties, bools)

        with open(filename, 'w', encoding=encoding) as fd:
            fd.write(source)


class Cxt(Format):
    """Formal context in the classic CXT format."""

    suffix = '.cxt'

    @staticmethod
    def loads(source):
        b, yx, table = source.strip().split('\n\n')
        y, x = (int(i) for i in yx.split())
        lines = [l.strip() for l in table.strip().split('\n')]
        objects = lines[:y]
        properties = lines[y:y + x]
        bools = [tuple(f == 'X' for f in l) for l in lines[y + x:]]
        return objects, properties, bools

    @staticmethod
    def dumps(objects, properties, bools):
        lines = iter_cxt_lines(objects, properties, bools,
                               end_with_empty_line=True)
        return '\n'.join(lines)


def iter_cxt_lines(objects, properties, bools,
                   *, end_with_empty_line: bool = False):
    assert len(objects) == len(bools)
    assert {len(properties)} == set(map(len, bools))
    
    yield 'B'
    yield ''
    yield f'{len(objects):d}'
    yield f'{len(properties):d}'
    yield ''

    yield from objects
    yield from properties

    flags = {False: '.', True: 'X'}

    for row in bools:
        yield ''.join(flags[value] for value in row)

    if end_with_empty_line:
        yield ''


class Table(Format):
    """Formal context as ASCII-art style table."""

    suffix = '.txt'

    @staticmethod
    def loads(source):
        lines = (l.partition('#')[0].strip() for l in source.splitlines())
        lines = list(filter(None, lines))
        properties = [p.strip() for p in lines[0].strip('|').split('|')]
        table = [(obj.strip(),
            tuple(bool(f.strip()) for f in flags.strip('|').split('|')))
            for obj, flags in
                (objflags.partition('|')[::2] for objflags in lines[1:])]
        objects, bools = zip(*table)
        return objects, properties, bools

    @staticmethod
    def dumps(objects, properties, bools, indent=0):
        wd = [tools.max_len(objects)]
        wd.extend(map(len, properties))
        tmpl = ' ' * indent + '|'.join(f'%-{w:d}s' for w in wd) + '|'
        result = [tmpl % (('',) + tuple(properties))]
        result.extend(tmpl % ((o,) + tuple('X' if b else '' for b in intent))
                      for o, intent in zip(objects, bools))
        return '\n'.join(result)


class Csv(Format):
    """Formal context as CSV table."""

    suffix = '.csv'

    dialect = csv.excel

    @staticmethod
    def _load(reader):
        objects, bools = [], []
        properties = next(reader)[1:]
        for cols in reader:
            objects.append(cols[0])
            bools.append(tuple(c == 'X' for c in cols[1:]))

        return objects, properties, bools

    @staticmethod
    def _dump(writer, objects, properties, bools):
        symbool = ('', 'X').__getitem__
        writer.writerow([''] + list(properties))
        writer.writerows([o] + list(map(symbool, bs))
            for o, bs in zip(objects, bools))

    @classmethod
    def loads(cls, source, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        csv_reader = csv.reader

        with io.StringIO(source) as fd:
            reader = csv_reader(fd, dialect)
            return cls._load(reader)

    @classmethod
    def dumps(cls, objects, properties, bools, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        with io.StringIO() as fd:
            writer = csv.writer(fd, dialect)
            cls._dump(writer, objects, properties, bools)
            result = fd.getvalue()

        return result

    @classmethod
    def load(cls, filename, encoding, dialect=None):
        if encoding is None:
            encoding = cls.encoding

        if dialect is None:
            dialect = cls.dialect

        with open(filename, 'r', encoding=encoding, newline='') as fd:
            reader = csv.reader(fd, dialect)
            return cls._load(reader)

    @classmethod
    def dump(cls, filename, objects, properties, bools, encoding, dialect=None):
        if encoding is None:
            encoding = cls.encoding

        if dialect is None:
            dialect = cls.dialect

        with open(filename, 'w', encoding=encoding, newline='') as fd:
            writer = csv.writer(fd, dialect)
            return cls._dump(writer, objects, properties, bools)


class WikiTable(Format):
    """Formal context as MediaWiki markup table."""

    @staticmethod
    def dumps(objects, properties, bools):
        result = ['{| class="featuresystem"', '!',
                  '!{}'.format('!!'.join(properties))]
        wp = list(map(len, properties))
        for o, intent in zip(objects, bools):
            bcells = (('X' if b else '').ljust(w) for w, b in zip(wp, intent))
            result += ['|-', f'!{o}', '|{}'.format('||'.join(bcells))]
        result.append('|}')
        return '\n'.join(result)
