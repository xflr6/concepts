# formats.py - parse and serialize FCA context tables

"""Parse and serialize formal contexts in different formats."""

from itertools import izip

__all__ = ['Format']


class FormatMeta(type):

    _map = {}
    _default = None

    def __init__(self, name, bases, dct):
        if '__metaclass__' not in dct:
            if 'name' not in dct:
                self.name = name.lower()
            self._map[self.name] = self
            if self.default:
                self.__class__._default = self.name

    def __getitem__(self, name):
        if not name:
            name = self._default
        if name not in self._map:
            raise KeyError('%r unknown format: %r' % (self, name))
        return self._map[name]


class Format(object):
    """Parse and serialize formal contexts in a specific string format."""

    __metaclass__ = FormatMeta

    default = False

    @classmethod
    def load(cls, filename):
        with open(filename, 'rb') as fd:
            source = fd.read()
        return cls.loads(source)

    @classmethod
    def dump(cls, filename, objects, properties, bools):
        source = cls.dumps(objects, properties, bools)
        with open(filename, 'wb') as fd:
            fd.write(source)
    
    @staticmethod
    def loads(source):
        """Parse source string and return objects, properties, bools."""
        raise NotImplementedError

    @staticmethod
    def dumps(objects, properties, bools):
        """Serialize objects, properties, bools and return string."""
        raise NotImplementedError


class Table(Format):
    """Formal context as ascii-art style table.

    >>> print Table.dumps(['Cheddar', 'Limburger'], ['in_stock', 'sold_out'],
    ... [(False, True), (False, True)])
             |in_stock|sold_out|
    Cheddar  |        |X       |
    Limburger|        |X       |
    """

    default = True

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
        
        
class Cxt(Format):
    """Formal context in cxt format.

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


class WikiTable(Format):
    """Formal context as mediawiki markup table.

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
