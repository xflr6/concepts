# formats.py - parse and serialize FCA context tables

"""Parse and serialize formal contexts in different formats."""

import ast
import contextlib
import csv
import functools
import io
import os
import typing

from . import tools

__all__ = ['Format']


class ContextArgs(typing.NamedTuple):
    """Return value of ``.loads()`` and ``.load()``."""

    objects: typing.List[str]

    properties: typing.List[str]

    bools: typing.List[typing.Tuple[bool, ...]]

    serialized: typing.Optional['SerializedType'] = None


LatticeType = typing.List[typing.Tuple[typing.Tuple[int],
                                       typing.Tuple[int],
                                       typing.Tuple[int],
                                       typing.Tuple[int]]]


class SerializedArgs(ContextArgs):

    lattice: typing.Optional[LatticeType] = None


class FormatMeta(type):
    """Collect and retrieve concrete ``Format`` subclasses by name."""

    _map = {}

    by_suffix = {}

    def __init__(self, name, bases, dct):  # noqa: N804
        if not dct.get('__abstract__'):
            if 'name' not in dct:
                self.name = tools.snakify(name, sep='-')
            if 'suffix' in dct:
                self.by_suffix[self.suffix] = self.name
            self._map[self.name] = self
            if 'aliases' in dct:
                self._map.update(dict.fromkeys(dct['aliases'], self))

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

    newline = None

    dumps_rstrip = None

    @classmethod
    def load(cls, filename, encoding, **kwargs) -> ContextArgs:
        """Load and parse serialized objects, properties, bools from file."""
        if encoding is None:
            encoding = cls.encoding

        with open(filename, encoding=encoding, newline=cls.newline) as f:
            return cls.loadf(f, **kwargs)
        return cls.loads(source)

    @classmethod
    def loads(cls, source, **kwargs) -> ContextArgs:
        """Parse source string and return ``ContextArgs``."""
        with io.StringIO(source) as buf:
            return cls.loadf(buf, **kwargs)

    @classmethod
    def dump(cls, filename, objects, properties, bools,
             *, encoding: typing.Optional[str], _serialized=None, **kwargs):
        """Write serialized objects, properties, bools to file."""
        if encoding is None:
            encoding = cls.encoding

        with open(filename, 'w', encoding=encoding, newline=cls.newline) as f:
            cls.dumpf(f, objects, properties, bools, _serialized=_serialized,
                      **kwargs)

    @classmethod
    def dumps(cls, objects, properties, bools, _serialized=None, **kwargs):
        with io.StringIO(newline=cls.newline) as buf:
            cls.dumpf(buf, objects, properties, bools, _serialized=_serialized,
                      **kwargs)
            source = buf.getvalue()
        if cls.dumps_rstrip:
            source = source.rstrip()
        return source

    @staticmethod
    def loadf(file, **kwargs) -> ContextArgs:
        """Parse file-like object and return ``ContextArgs``."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def dumpf(file, objects, properties, bools, *, _serialized=None, **kwargs):
        """Serialize ``(objects, properties, bools)`` into file-like object."""
        raise NotImplementedError  # pragma: no cover


class Cxt(Format):
    """Formal context in the classic CXT format."""

    suffix = '.cxt'

    dumps_rstrip = False

    @staticmethod
    def loadf(file):
        source = file.read().strip()
        b, yx, table = source.split('\n\n')
        y, x = (int(i) for i in yx.split())
        lines = [l.strip() for l in table.strip().split('\n')]
        objects = lines[:y]
        properties = lines[y:y + x]
        bools = [tuple(f == 'X' for f in l) for l in lines[y + x:]]
        return ContextArgs(objects, properties, bools)

    @staticmethod
    def dumpf(file, objects, properties, bools, *, _serialized=None):
        write = functools.partial(print, file=file)
        for line in iter_cxt_lines(objects, properties, bools,
                                   end_with_empty_line=False):
            write(line)


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

    dumps_rstrip = True

    @staticmethod
    def loadf(file):
        lines = (line.partition('#')[0].strip() for line in file)
        lines = list(filter(None, lines))
        properties = [p.strip() for p in lines[0].strip('|').split('|')]
        table = [(obj.strip(),
            tuple(bool(f.strip()) for f in flags.strip('|').split('|')))
            for obj, flags in
                (objflags.partition('|')[::2] for objflags in lines[1:])]
        objects, bools = zip(*table)
        return ContextArgs(objects, properties, bools)

    @staticmethod
    def dumpf(file, objects, properties, bools, *, indent=0, _serialized=None):
        wd = [tools.max_len(objects)]
        wd.extend(map(len, properties))
        tmpl = ' ' * indent + '|'.join(f'%-{w:d}s' for w in wd) + '|'

        write = functools.partial(print, file=file)
        write(tmpl % (('',) + tuple(properties)))
        for o, intent in zip(objects, bools):
            write(tmpl % ((o,) + tuple('X' if b else '' for b in intent)))


class Csv(Format):
    """Formal context as CSV table."""

    suffix = '.csv'

    newline = ''

    dumps_rstrip = False

    dialect = csv.excel

    @classmethod
    def loadf(cls, file, *, dialect: typing.Optional[str] = None) -> ContextArgs:
        if dialect is None:
            dialect = cls.dialect
        reader = csv.reader(file, dialect=dialect)

        objects, bools = ([] for _ in range(2))
        _, *properties = next(reader)
        for obj, *values in reader:
            objects.append(obj)
            bools.append(tuple(v == 'X' for v in values))

        return ContextArgs(objects, properties, bools)

    @classmethod
    def dumpf(cls, file, objects, properties, bools,
              *, dialect: typing.Optional[str] = None,
              _serialized=None) -> None:
        if dialect is None:
            dialect = cls.dialect

        writer = csv.writer(file, dialect=dialect)
        symbool = ('', 'X').__getitem__
        writer.writerow([''] + list(properties))
        writer.writerows([o] + list(map(symbool, bs))
                         for o, bs in zip(objects, bools))


class WikiTable(Format):
    """Formal context as MediaWiki markup table."""

    aliases = ['wikitable']

    dumps_rstrip = True

    @staticmethod
    def dumpf(file, objects, properties, bools, *,  _serialized=None):
        write = functools.partial(print, file=file)
        write('{| class="featuresystem"')
        write('!')
        write('!{}'.format('!!'.join(properties)))

        wp = list(map(len, properties))

        for o, intent in zip(objects, bools):
            bcells = (('X' if b else '').ljust(w) for w, b in zip(wp, intent))
            write('|-')
            write(f'!{o}')
            write('|{}'.format('||'.join(bcells)))
        write('|}')


class PythonLiteral(Format):
    """Format context as input for ``ast.literal_eval()``."""

    suffix = '.py'

    dumps_rstrip = True

    @staticmethod
    def loadf(file) -> SerializedArgs:
        python_source = file.read()
        args = ast.literal_eval(python_source)
        assert args is not None
        assert isinstance(args, dict)

        objects = args['objects']
        properties = args['properties']

        bools = [[False for _ in args['properties']]
                 for _ in args['objects']]
        for row, true_indexes in zip(bools, args['context']):
            for i in true_indexes:
                row[i] = True
        bools = [tuple(row) for row in bools]

        return SerializedArgs(objects, properties, bools, serialized=args)

    @staticmethod
    def dumpf(file, objects, properties, bools, *, _serialized=None) -> None:
        if _serialized is None:
            doc = {'objects': objects,
                   'properties': properties,
                   'context': [tuple(i for i, b in enumerate(row) if b)
                               for row in bools]}
        else:
            doc = _serialized
            assert isinstance(doc, dict)
            keys = ('objects', 'properties', 'context')
            assert all(k in doc for k in keys)

        indent = ' ' * 2

        def itersection(key, lines, value_list: bool = False):
            start, end = ('[', ']') if value_list else ('(', ')')

            yield f'{indent}{key!r}: {start}'
            yield from lines
            yield f'{indent}{end},'
            
        def iterlines(doc):
            yield '{'

            for key in ('objects', 'properties'):
                line = ', '.join(map(repr, doc[key]))
                yield from itersection(key, [f'{indent * 2}{line},'])

            for key in ('context',) + (('lattice',) if 'lattice' in doc else ()):
                lines = [f'{indent * 2}{line},' for line in map(repr, doc[key])]
                yield from itersection(key, lines, value_list=True)

            yield '}'

        write = functools.partial(print, file=file)
        for line in iterlines(doc):
            write(line)
