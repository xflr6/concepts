# tools.py

import csv
import codecs
from itertools import permutations, groupby, starmap
import operator

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

__all__ = ['maximal', 'lazyproperty', 'UnicodeReader', 'UnicodeWriter']


def maximal(iterable, comparison=operator.lt, _groupkey=operator.itemgetter(0)):
    """Yield the unique maximal elements from iterable using comparison.

    >>> list(maximal([1, 2, 3, 3]))
    [3]

    >>> list(maximal([1]))
    [1]
    """
    iterable = set(iterable)
    if len(iterable) < 2:
        return iterable
    return (item for item, pairs
        in groupby(permutations(iterable, 2), key=_groupkey)
        if not any(starmap(comparison, pairs)))


class lazyproperty(object):
    """Non-data descriptor caching the computed result as instance attribute.

    >>> class Spam(object):
    ...     @lazyproperty
    ...     def eggs(self):
    ...         return 'spamspamspam'

    >>> spam=Spam(); spam.eggs
    'spamspamspam'

    >>> spam.eggs='eggseggseggs'; spam.eggs
    'eggseggseggs'

    >>> Spam().eggs
    'spamspamspam'
    """

    def __init__(self, fget):
        self.fget = fget
        for attr in ('__module__', '__name__', '__doc__'):
            setattr(self, attr, getattr(fget, attr))

    def __get__(self, instance, owner):
        if instance is None:
            return self
        result = instance.__dict__[self.__name__] = self.fget(instance)
        return result


# from stdlib recipe

class UTF8Recoder(object):

    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode('utf8')


class UnicodeReader(object):

    def __init__(self, f, dialect=csv.excel, encoding='utf8', **kwargs):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwargs)

    def next(self):
        row = self.reader.next()
        return [unicode(s, 'utf8') for s in row]

    def __iter__(self):
        return self


class UnicodeWriter(object):

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwargs):
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode('utf8') for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf8')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
