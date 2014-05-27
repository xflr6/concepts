# tools.py

import csv
import codecs
import operator
from itertools import permutations, groupby, starmap

from ._compat import StringIO

__all__ = ['maximal', 'lazyproperty', 'unicode_csv_reader', 'UnicodeWriter']


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

    >>> Spam.eggs  # doctest: +ELLIPSIS
    <...lazyproperty object at 0x...>
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


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data), dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


class UnicodeWriter(object):

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwargs):
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwargs)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode('utf-8') for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
