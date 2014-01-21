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
    def load(cls, filename):
        """Load and parse serialized objects, properties, bools from file."""
        if cls.encoding is None:
            with open(filename, 'rb') as fd:
                source = fd.read()
        else:
           with codecs.open(filename, 'rb', cls.encoding) as fd:
                source = fs.read()
 
        if cls.normalize_newlines:
            source = source.replace('\r\n', '\n').replace('\r', '\n')
        return cls.loads(source)

    @classmethod
    def dump(cls, filename, objects, properties, bools):
        """Write serialized objects, properties, bools to file."""
        source = cls.dumps(objects, properties, bools)

        if cls.encoding is None:
            with open(filename, 'wb') as fd:
                fd.write(source)
        else:
            with codecs.open(filename, 'wb', cls.encoding) as fd:
                fd.write(source)
    
    @staticmethod
    def loads(source):
        """Parse source string and return objects, properties, bools."""
        raise NotImplementedError

    @staticmethod
    def dumps(objects, properties, bools):
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
    def dumps(objects, properties, bools, indent=0):
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

    dialect = 'excel'

    @classmethod
    def load(cls, filename, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        with open(filename, 'rb') as fd:
            return cls._load(fd, dialect, cls.encoding)

    @classmethod
    def dump(cls, filename, objects, properties, bools, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        with open(filename, 'wb') as fd:
            cls._dump(fd, objects, properties, bools, dialect, cls.encofing)

    @classmethod
    def loads(cls, source, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        with contextlib.closing(StringIO.StringIO(source)) as fd:
            return cls._load(fd, dialect, cls.encoding)

    @classmethod
    def dumps(cls, objects, properties, bools, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        with contextlib.closing(StringIO.StringIO()) as fd:
            cls._dump(fd, objects, properties, bools, dialect, cls.encoding)
            return fd.getvalue()

    @staticmethod
    def _load(fd, dialect, encoding):
        objects, bools = [], []
        reader = csv.reader(fd, dialect)
        if encoding is None:
            properties = next(reader)[1:]
            for cols in reader:
                objects.append(cols[0])
                bools.append(tuple(c == 'X' for c in cols[1:]))
        else:
            properties = [col.decode(encoding) for col in next(reader)[1:]]
            for cols in reader:
                objects.append(cols[0].decode(encoding))
                bools.append(tuple(c == 'X' for c in cols[1:]))
        return objects, properties, bools
    
    @staticmethod
    def _dump(fd, objects, properties, bools, dialect, encoding):
        symbool = ('', 'X').__getitem__
        writer = csv.writer(fd, dialect)
        if encoding is None:
            writer.writerow([''] + list(properties))
            writer.writerows([o] + map(symbool, bs)
                for o, bs in izip(objects, bools))
        else:
            writer.writerow([''] + [p.encode(encoding) for p in properties])
            writer.writerows([o.encode(encoding)] + map(symbool, bs)
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


def _test(verbose=False):
    import doctest
    doctest.testmod(verbose=verbose)

if __name__ == '__main__':
    _test()
