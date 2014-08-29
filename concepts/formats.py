# formats.py - parse and serialize FCA context tables

"""Parse and serialize formal contexts in different formats."""

import io
import csv
import contextlib

from ._compat import PY2, text_type, zip, with_metaclass, StringIO

from . import tools, unicodecsv

__all__ = ['Format']


class FormatMeta(type):
    """Collect and retrieve concrete Format subclasses by name."""

    _map = {}

    by_extension = {}

    def __init__(self, name, bases, dct):
        if not dct.get('__abstract__'):
            if 'name' not in dct:
                self.name = name.lower()
            if 'extension' in dct:
                self.by_extension[self.extension] = self.name
            self._map[self.name] = self

    def __getitem__(self, name):
        if name not in self._map:
            raise KeyError('%r unknown format: %r' % (self, name))
        return self._map[name]


class Format(with_metaclass(FormatMeta, object)):
    """Parse and serialize formal contexts in a specific string format."""

    __abstract__ = True

    encoding = None

    normalize_newlines = True

    @staticmethod
    def loads(source, **kwargs):
        """Parse source string and return objects, properties, bools."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def dumps(objects, properties, bools, **kwargs):
        """Serialize objects, properties, bools and return string."""
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def load(cls, filename, encoding):
        """Load and parse serialized objects, properties, bools from file."""
        if encoding is None:
            encoding = cls.encoding

        with io.open(filename, 'r', encoding=encoding) as fd:
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
        if PY2:
            source = unicode(source)

        with io.open(filename, 'w', encoding=encoding) as fd:
            fd.write(source)


class Cxt(Format):
    """Formal context in the classic CXT format."""

    extension = '.cxt'

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
        result = ['B', '', '%d' % len(objects), '%d' % len(properties), '']
        result.extend(objects)
        result.extend(properties)
        result.extend(''.join('X' if b else '.' for b in intent)
            for intent in bools)
        result.append('')
        return '\n'.join(result)


class Table(Format):
    """Formal context as ASCII-art style table."""

    extension = '.txt'

    @staticmethod
    def escape(item):
        return text_type(item).encode('ascii', 'backslashreplace')

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
    def dumps(objects, properties, bools, escape=False, indent=0):
        if escape:
            objects = list(map(Table.escape, objects))
            properties = list(map(Table.escape, properties))
        wd = [tools.max_len(objects)]
        wd.extend(map(len, properties))
        tmpl = ' ' * indent + '|'.join('%%-%ds' % w for w in wd) + '|'
        result = [tmpl % (('',) + tuple(properties))]
        result.extend(tmpl % ((o,) + tuple('X' if b else '' for b in intent))
            for o, intent in zip(objects, bools))
        return '\n'.join(result)


class Csv(Format):
    """Formal context as CSV table."""

    extension = '.csv'

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

        with contextlib.closing(StringIO(source)) as fd:
            if not PY2 or isinstance(source, str):
                reader = csv.reader(fd, dialect)
            else:
                reader = unicodecsv.unicode_csv_reader(fd, dialect)
            return cls._load(reader)

    @classmethod
    def dumps(cls, objects, properties, bools, dialect=None):
        if dialect is None:
            dialect = cls.dialect

        if PY2:
            if all(isinstance(s, str) for s in objects + properties):
                with contextlib.closing(StringIO()) as fd:
                    writer = csv.writer(fd, dialect)
                    cls._dump(writer, objects, properties, bools)
                    return fd.getvalue()

            with contextlib.closing(StringIO()) as fd:
                writer = unicodecsv.UnicodeWriter(fd, dialect, 'utf-8')
                cls._dump(writer, objects, properties, bools)
                return fd.getvalue().decode('utf-8')

        with contextlib.closing(StringIO()) as fd:
            writer = csv.writer(fd, dialect)
            cls._dump(writer, objects, properties, bools)
            return fd.getvalue()

    @classmethod
    def load(cls, filename, encoding, dialect=None):
        if encoding is None:
            encoding = cls.encoding

        if dialect is None:
            dialect = cls.dialect

        if PY2:
            if encoding is None:
                with open(filename, 'rb') as fd:
                    reader = csv.reader(fd, dialect)
                    return cls._load(reader)

            with io.open(filename, 'r', encoding=encoding, newline='') as fd:
                reader = unicodecsv.unicode_csv_reader(fd, dialect)
                return cls._load(reader)

        with io.open(filename, 'r', encoding=encoding, newline='') as fd:
            reader = csv.reader(fd, dialect)
            return cls._load(reader)

    @classmethod
    def dump(cls, filename, objects, properties, bools, encoding, dialect=None):
        if encoding is None:
            encoding = cls.encoding

        if dialect is None:
            dialect = cls.dialect

        if PY2:
            with open(filename, 'wb') as fd:
                if encoding is None:
                    writer = csv.writer(fd, dialect)
                else:
                    writer = unicodecsv.UnicodeWriter(fd, dialect, encoding)
                return cls._dump(writer, objects, properties, bools)

        with io.open(filename, 'w', encoding=encoding, newline='') as fd:
            writer = csv.writer(fd, dialect)
            return cls._dump(writer, objects, properties, bools)


class WikiTable(Format):
    """Formal context as MediaWiki markup table."""

    @staticmethod
    def dumps(objects, properties, bools):
        result = ['{| class="featuresystem"', '!', '!%s' % '!!'.join(properties)]
        wp = list(map(len, properties))
        for o, intent in zip(objects, bools):
            bcells = (('X' if b else '').ljust(w) for w, b in zip(wp, intent))
            result += ['|-', '!%s' % o, '|%s' % '||'.join(bcells)]
        result.append('|}')
        return '\n'.join(result)
