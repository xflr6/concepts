# formats.py - parse and serialize FCA context tables

"""Parse and serialize formal contexts in different formats."""

from itertools import izip
import contextlib
import codecs
import csv

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import tools

__all__ = ['Format']


class FormatMeta(type):

    _map = {}

    def __init__(self, name, bases, dct):
        if '__metaclass__' not in dct:
            if 'name' not in dct:
                self.name = name.lower()
            self._map[self.name] = self

    def __getitem__(self, name):
        if name not in self._map:
            raise KeyError('%r unknown format: %r' % (self, name))
        return self._map[name]


class Format(object):
    """Parse and serialize formal contexts in a specific string format."""

    __metaclass__ = FormatMeta

    encoding = None

    normalize_newlines = True

    @classmethod
    def load(cls, filename, encoding):
        """Load and parse serialized objects, properties, bools from file."""
        if encoding is None:
            encoding = cls.encoding

        if encoding is None:
            with open(filename, 'rb') as fd:
                source = fd.read()
        else:
           with codecs.open(filename, 'rb', encoding) as fd:
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

        if encoding is None:
            with open(filename, 'wb') as fd:
                fd.write(source)
        else:
            with codecs.open(filename, 'wb', encoding) as fd:
                fd.write(source)
    
    @staticmethod
    def loads(source, **kwargs):
        """Parse source string and return objects, properties, bools."""
        raise NotImplementedError

    @staticmethod
    def dumps(objects, properties, bools, **kwargs):
        """Serialize objects, properties, bools and return string."""
        raise NotImplementedError


class Cxt(Format):
    """Formal context in the classic CXT format.

    >>> print Cxt.dumps(['Cheddar', 'Limburger'], ['in_stock', 'sold_out'],
    ... [(False, True), (False, True)])
    B
    <BLANKLINE>
    2
    2
    <BLANKLINE>
    Cheddar
    Limburger
    in_stock
    sold_out
    .X
    .X
    <BLANKLINE>
    """

    @staticmethod
    def loads(source):
        b, yx, table = source.strip().split('\n\n')
        y, x = (int(i) for i in yx.split())
        lines = [l.strip() for l in table.strip().split('\n')]
        objects = lines[:y]
        properties = lines[y:y + x]
        bools = [[f == 'X' for f in l] for l in lines[y + x:]]
        return objects, properties, bools

    @staticmethod
    def dumps(objects, properties, bools):
        result = ['B', '', '%d' % len(objects), '%d' % len(properties), '']
        result.extend(objects)
        result.extend(properties)
        result.extend(''.join('X' if b else '.' for b in intent)
            for intent in bools)
        result.append('')
        return '\n'.join(result)


class Table(Format):
    """Formal context as ASCII-art style table.

    >>> print Table.dumps(['Cheddar', 'Limburger'], ['in_stock', 'sold_out'],
    ... [(False, True), (False, True)])
             |in_stock|sold_out|
    Cheddar  |        |X       |
    Limburger|        |X       |
    """

    @staticmethod
    def escape(item):
        return unicode(item).encode('unicode_escape')

    @staticmethod
    def loads(source):
        lines = (l.partition('#')[0].strip() for l in source.splitlines())
        lines = filter(None, lines)
        properties = [p.strip() for p in lines[0].strip('|').split('|')]
        table = [(obj.strip(),
            [bool(f.strip()) for f in flags.strip('|').split('|')])
            for obj, flags in
                (objflags.partition('|')[::2] for objflags in lines[1:])]
        objects, bools = zip(*table)
        return objects, properties, bools

    @staticmethod
    def dumps(objects, properties, bools, escape=False, indent=0):
        if escape:
            objects = map(Table.escape, objects)
            properties = map(Table.escape, properties)
        wd = [max(len(o) for o in objects)] + map(len, properties)
        tmpl = ' ' * indent + '|'.join('%%-%ds' % w for w in wd) + '|'
        result = [tmpl % (('',) + tuple(properties))]
        result.extend(tmpl % ((o,) + tuple('X' if b else '' for b in intent))
            for o, intent in izip(objects, bools))
        return '\n'.join(result)


class Csv(Format):
    """Formal context as CSV table.

    >>> print Csv.dumps(['Cheddar', 'Limburger'], ['in_stock', 'sold_out'],
    ... [(False, True), (False, True)])  # doctest: +NORMALIZE_WHITESPACE
    ,in_stock,sold_out
    Cheddar,,X
    Limburger,,X
    <BLANKLINE>
    """

    dialect = csv.excel

    @classmethod
    def load(cls, filename, encoding, dialect=None):
        if encoding is None:
            encoding = cls.encoding

        if dialect is None:
            dialect = cls.dialect

        with open(filename, 'rb') as fd:
            return cls._load(fd, dialect, encoding)

    @classmethod
    def dump(cls, filename, objects, properties, bools, encoding, dialect=None):
        if encoding is None:
            encoding = cls.encoding

        if dialect is None:
            dialect = cls.dialect

        with open(filename, 'wb') as fd:
            cls._dump(fd, objects, properties, bools, dialect, encoding)

    @classmethod
    def loads(cls, source, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        with contextlib.closing(StringIO.StringIO(source.encode('utf8'))) as fd:
            return cls._load(fd, dialect, 'utf8')

    @classmethod
    def dumps(cls, objects, properties, bools, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        with contextlib.closing(StringIO.StringIO()) as fd:
            cls._dump(fd, objects, properties, bools, dialect, 'utf8')
            return fd.getvalue().decode('utf8')

    @staticmethod
    def _load(fd, dialect, encoding):
        objects, bools = [], []
        if encoding is None:
            reader = csv.reader(fd, dialect)
        else:
            reader = tools.UnicodeReader(fd, dialect, encoding)
        
        properties = next(reader)[1:]
        for cols in reader:
            objects.append(cols[0])
            bools.append(tuple(c == 'X' for c in cols[1:]))

        return objects, properties, bools
    
    @staticmethod
    def _dump(fd, objects, properties, bools, dialect, encoding):
        if encoding is None:
            writer = csv.writer(fd, dialect)
        else:
            writer = tools.UnicodeWriter(fd, dialect, encoding)

        symbool = ('', 'X').__getitem__
        writer.writerow([''] + list(properties))
        writer.writerows([o] + map(symbool, bs)
            for o, bs in izip(objects, bools))


class WikiTable(Format):
    """Formal context as MediaWiki markup table.

    >>> print WikiTable.dumps(['Cheddar', 'Limburger'], ['in_stock', 'sold_out'],
    ... [(False, True), (False, True)])
    {| class="featuresystem"
    !
    !in_stock!!sold_out
    |-
    !Cheddar
    |        ||X       
    |-
    !Limburger
    |        ||X       
    |}
    """

    @staticmethod
    def dumps(objects, properties, bools):
        result = ['{| class="featuresystem"', '!', '!%s' % '!!'.join(properties)]
        wp = map(len, properties)
        for o, intent in izip(objects, bools):
            result += ['|-', '!%s' % o,
                '|%s' % '||'.join(('X' if b else '').ljust(w)
                    for w, b in izip(wp, intent))]
        result.append('|}')
        return '\n'.join(result)
