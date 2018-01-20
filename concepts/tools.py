# tools.py

import collections
import operator
from itertools import permutations, groupby, starmap

from ._compat import map

__all__ = ['Unique', 'max_len', 'maximal', 'lazyproperty']


class Unique(collections.MutableSet):
    """Unique items preserving order.

    >>> Unique([3, 2, 1, 3, 2, 1, 0])
    Unique([3, 2, 1, 0])
    """

    @classmethod
    def _fromargs(cls, _seen, _items):
        inst = super(Unique, cls).__new__(cls)
        inst._seen = _seen
        inst._items = _items
        return inst

    def __init__(self, iterable=()):
        self._seen = seen = set()
        add = seen.add
        self._items = [item for item in iterable
            if item not in seen and not add(item)]

    def copy(self):
        return self._fromargs(self._seen.copy(), self._items[:])

    def __iter__(self):
        return iter(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, item):
        return item in self._seen

    def __repr__(self):
        items = repr(self._items) if self._items else ''
        return '%s(%s)' % (self.__class__.__name__, items)

    def add(self, item):
        if item not in self._seen:
            self._seen.add(item)
            self._items.append(item)

    def discard(self, item):
        if item in self._seen:
            self._seen.remove(item)
            self._items.remove(item)

    def replace(self, item, new_item):
        """Replace an item preserving order.

        >>> u = Unique([0, 1, 2])
        >>> u.replace(1, 'spam')
        >>> u
        Unique([0, 'spam', 2])

        >>> u.replace('eggs', 1)
        Traceback (most recent call last):
            ...
        ValueError: 'eggs' is not in list

        >>> u.replace('spam', 0)
        Traceback (most recent call last):
            ...
        ValueError: 0 already in list
        """
        if new_item in self._seen:
            raise ValueError('%r already in list' % new_item)
        idx = self._items.index(item)
        self._seen.remove(item)
        self._seen.add(new_item)
        self._items[idx] = new_item

    def move(self, item, new_index):
        """Move an item to the given position.

        >>> u = Unique(['spam', 'eggs'])
        >>> u.move('spam', 1)
        >>> u
        Unique(['eggs', 'spam'])

        >>> u.move('ham', 0)
        Traceback (most recent call last):
            ...
        ValueError: 'ham' is not in list
        """
        idx = self._items.index(item)
        if idx != new_index:
            item = self._items.pop(idx)
            self._items.insert(new_index, item)

    def issuperset(self, items):
        """Return whether this collection contains all items.

        >>> Unique(['spam', 'eggs']).issuperset(['spam', 'spam', 'spam'])
        True
        """
        return all(map(self._seen.__contains__, items))

    def rsub(self, items):
        """Return order preserving unique items not in this collection.

        >>> Unique(['spam']).rsub(['ham', 'spam', 'eggs'])
        Unique(['ham', 'eggs'])
        """
        ignore = self._seen
        seen = set()
        add = seen.add
        items = [i for i in items
                 if i not in ignore and i not in seen and not add(i)]
        return self._fromargs(seen, items)


def max_len(iterable, minimum=0):
    """Return the len() of the longest item in ``iterable`` or ``minimum``.

    >>> max_len(['spam', 'ham'])
    4

    >>> max_len([])
    0

    >>> max_len(['ham'], 4)
    4
    """
    try:
        result = max(map(len, iterable))
    except ValueError:
        result = minimum
    return minimum if result < minimum else result


def maximal(iterable, comparison=operator.lt, _groupkey=operator.itemgetter(0)):
    """Yield the unique maximal elements from ``iterable`` using ``comparison``.

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
