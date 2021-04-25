# tools.py - generic helpers

import collections.abc
import csv
import functools
import hashlib
from itertools import permutations, groupby, starmap
import json
import operator
import re
import typing
import zlib

__all__ = ['snakify',
           'Unique',
           'max_len', 'maximal',
           'lazyproperty',
           'crc32_hex',
           'sha256sum',
           'write_lines',
           'csv_iterrows',
           'write_csv', 'write_csv_file',
           'dump_json', 'load_json']

CSV_DIALECT = 'excel'

DEFAULT_ENCODING = 'utf-8'


def snakify(name: str, *, sep: str = '_',
            _re_upper=re.compile(r'([A-Z])')) -> str:
    """Lowercase ``name`` adding ``sep`` before in-word-uppercase letters.

    >>> snakify('CamelCase')
    'camel_case'
    """
    return (name[:1] + _re_upper.sub(rf'{sep}\1', name[1:])).lower()


class Unique(collections.abc.MutableSet):
    """Unique items preserving order.

    >>> Unique([3, 2, 1, 3, 2, 1, 0])
    Unique([3, 2, 1, 0])
    """

    @classmethod
    def _fromargs(cls, _seen, _items):
        inst = super().__new__(cls)
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
        arg = repr(self._items) if self._items else ''
        return f'{self.__class__.__name__}({arg})'

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
            raise ValueError(f'{new_item!r} already in list')

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
        return minimum
    return max(result, minimum)


def maximal(iterable, comparison=operator.lt, _groupkey=operator.itemgetter(0)):
    """Yield the unique maximal elements from ``iterable`` using ``comparison``.

    >>> list(maximal([1, 2, 3, 3]))
    [3]

    >>> list(maximal([1]))
    [1]
    """
    iterable = set(iterable)
    if len(iterable) < 2:
        return iter(iterable)

    return (item
            for item, pairs in groupby(permutations(iterable, 2), key=_groupkey)
            if not any(starmap(comparison, pairs)))


class lazyproperty:  # noqa: N801
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


def crc32_hex(data):
    """Return unsigned CRC32 of binary data as hex-encoded string.

    >>> crc32_hex(b'spam')
    '43daff3d'
    """
    value = zlib.crc32(data) & 0xffffffff
    return f'{value:x}'


def sha256sum(filepath, bufsize: int = 32_768) -> str:
    """Return SHA-256 hexdigest from reading ``filepath``."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for data in iter(functools.partial(f.read, bufsize), b''):
            h.update(data)
    return h.hexdigest()


def write_lines(path, lines: typing.Iterable[str],
                *, encoding: str = DEFAULT_ENCODING,
                newline: typing.Optional[str] = None):
    """Write ``lines`` to ``path``."""
    with open(path, 'w', encoding=encoding, newline=newline) as f:
        write = functools.partial(print, file=f)
        for line in lines:
            write(line)


def csv_iterrows(path, *, dialect: str = CSV_DIALECT,
                 encoding: str = DEFAULT_ENCODING,
                 newline: typing.Optional[str] = ''):
    with open(path, encoding=encoding, newline=newline) as f:
        reader = csv.reader(f, dialect=dialect)
        yield from reader


def write_csv(path, rows,
              *, header: typing.Optional[typing.Iterable[str]] = None,
              dialect: str = CSV_DIALECT,
              encoding: str = DEFAULT_ENCODING,
              newline: typing.Optional[str] = ''):
    """Write ``rows`` as CSV to ``path`` with optional ``header``."""
    with open(path, 'w', encoding=encoding, newline=newline) as f:
        write_csv_file(f, rows, header=header)


def write_csv_file(file, rows,
                   *, header: typing.Optional[typing.Iterable[str]] = None,
                   dialect: str = CSV_DIALECT):
    """Write ``rows`` as CSV to file-like object with optional ``header``."""
    writer = csv.writer(file, dialect=dialect)
    if header is not None:
        writer.writerow(header)
    writer.writerows(rows)


def dump_json(obj, path_or_fileobj,
              *, encoding: str = DEFAULT_ENCODING,
              mode: str = 'w', **kwargs):
    """Serialize ``obj`` via :func:`json.load` to path or file-like object."""
    kwargs['obj'] = obj
    _call_json('dump', path_or_fileobj, encoding, mode, **kwargs)


def load_json(path_or_fileobj,
              *, encoding: str = DEFAULT_ENCODING,
              mode: str = 'r', **kwargs):
    """Return deserialized :func:`json.load` from path or file-like object."""
    return _call_json('load', path_or_fileobj, encoding, mode, **kwargs)


def _call_json(funcname, path_or_fileobj, encoding, mode, **kwargs):
    f, fallthrough = _get_fileobj(path_or_fileobj, mode, encoding=encoding)
    close = not fallthrough

    try:
        return getattr(json, funcname)(fp=f, **kwargs)
    except (AttributeError, TypeError):
        raise TypeError('path_or_fileobj: {path_or_fileobj!r}')
    finally:
        if close:
            f.close()


def _get_fileobj(path_or_fileobj, mode, encoding):
    fallthrough = False

    try:
        f = open(path_or_fileobj, mode, encoding=encoding)
    except TypeError:
        try:
            f = path_or_fileobj.open(mode, encoding=encoding)
        except AttributeError:
            f = path_or_fileobj
            fallthrough = True

    return f, fallthrough
