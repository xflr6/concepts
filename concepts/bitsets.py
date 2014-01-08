# bitsets.py - integer bits representing subsets of totally orderd finite set

"""Subsets of a totally ordered finite set as rank in colexicographical order."""

from itertools import izip, imap, compress
import copy_reg
import collections

__all__ = ['bitset']


def indexes(n):
    """Yield indexes unranking n in colexicographical order.

    >>> [tuple(indexes(i)) for i in range(8)]
    [(), (0,), (1,), (0, 1), (2,), (0, 2), (1, 2), (0, 1, 2)]
    """
    i = 0
    while n:
        if n & 1:
            yield i
        i += 1
        n >>= 1


def unrank(n, sequence='abcdefghijklmnopqrstuvwxyz'):
    """Unrank n from sequence in colexicographical order.

    >>> [''.join(unrank(i)) for i in range(8)]
    ['', 'a', 'b', 'ab', 'c', 'ac', 'bc', 'abc']
    >>> unrank(147491)
    ['a', 'b', 'f', 'o', 'r']
    """
    return map(sequence.__getitem__, indexes(n))


def reinverted(n, r):
    """Integer with reversed and inverted bits of n assuming bit length r.

    >>> [reinverted(x, 6) for x in [7, 11, 13, 14, 19, 21, 22, 25, 26, 28]]
    [7, 11, 19, 35, 13, 21, 37, 25, 41, 49]
    """
    result = 0
    r = 1 << r - 1
    while n:
        if not n & 1:
            result |= r
        r >>= 1
        n >>= 1
    if r:
        result |= (r << 1) -1
    return result


_registry = {}


def bitset(name, members, cached=None):
    """Return concrete BitSet subclass with given name and members."""
    if (name, members, cached) in _registry:
        cls = _registry[(name, members, cached)]
    elif cached is None:  # try first match
        matching = [cls for (cname, cmembers, cid), cls in _registry.iteritems()
            if cname == name and cmembers == members]
        if len(matching) == 1:
            cls = matching[0]
        elif matching:
            raise RuntimeError('Multiple classes matching %r' % matching)
        else:
            cls = BitSet._make_subclass(name, members, cached)
    else:
        cls = BitSet._make_subclass(name, members, cached)
    return cls


class BitSetMeta(type):

    def _make_subclass(self, name, members, id=None):
        if hasattr(self, '_members'):
            raise RuntimeError('%r attempt _make_subclass' % self)

        dct = {'__slots__': self.__slots__, '_members': members}
        if id:
            dct['_id'] = id
        return type(name, (self,), dct)

    def __init__(self, name, bases, dct):
        if '__metaclass__' in dct:
            return
        self._len = len(self._members)
        self._atoms = tuple(self.from_int(1 << i) for i in range(self._len))
        self._map = {i: s for i, s in izip(self._members, self._atoms)}
        self.infimum = self.from_int(0)
        self.supremum = self.from_int((1 << self._len) - 1)

        if not hasattr(self, '_id'):
            self._id = id(self)

        _registry[(name, self._members, self._id)] = self

    def __repr__(self):
        if not hasattr(self, '_members'):
            return type.__repr__(self)
        return '<class %s.bitset(%r, %r, %#x)>' % (self.__module__,
            self.__name__, self._members, self._id)

    def __reduce__(self):
        if not hasattr(self, '_members'):
            return self.__name__
        return bitset, (self.__name__, self._members, self._id)


copy_reg.pickle(BitSetMeta, BitSetMeta.__reduce__)


class BitSet(long):
    """Ordered collection of unique elements from a predefined finite domain.

    >>> Numbers = bitset('Numbers', tuple(range(1, 7)))

    >>> Numbers('100011').real == 49
    True

    >>> [x.members() for x in sorted(n for n in Numbers.supremum.powerset() if n.count() == 3)[:3]]
    [(1, 2, 3), (1, 2, 4), (1, 3, 4)]
    """

    __metaclass__ = BitSetMeta

    __slots__ = ()

    _indexes = indexes
    _reinverted = reinverted

    @classmethod
    def from_members(cls, members):
        """Create a set from an iterable of members or a comma/space separated string.

        >>> Numbers.from_members([1, 5, 6])
        Numbers('100011')
        """
        if isinstance(members, basestring):
            members = members.replace(',', ' ').split()
        return cls.from_int(sum(imap(cls._map.__getitem__, set(members))))

    @classmethod
    def from_bools(cls, bools):
        """Create a set from an iterable of boolean evaluable items.

        >>> Numbers.from_bools([True, '', None, 0, 'yes', 5])
        Numbers('100011')
        """
        return cls.from_int(sum(compress(cls._atoms, bools)))

    from_int = classmethod(long.__new__)

    def __new__(cls, bits):
        """Create a set from a binary string.

        >>> Numbers('100011') == Numbers.from_int(49)
        True
        """
        if len(bits) > cls._len:
            raise ValueError(bits)
        return cls.from_int(bits[::-1], 2)

    def members(self):
        """Return the set members tuple.

        >>> Numbers('100011').members()
        (1, 5, 6)
        """
        return tuple(imap(self._members.__getitem__, self._indexes()))

    def bools(self):
        """Return the boolean sequence of set membership.

        >>> Numbers('100011').bools()
        (True, False, False, False, True, True)
        """
        return tuple(not not self & a for a in self._atoms)

    def bits(self):
        """Return the binary string of set membership.

        >>> Numbers('100011').bits()
        '100011'
        """
        return '{0:0{1}b}'.format(self, self._len)[::-1]

    def atoms(self):
        """Return the member singleton list.

        >>> Numbers('100011').atoms()
        [Numbers('100000'), Numbers('000010'), Numbers('000001')]
        """
        return [a for a in self._atoms if self & a]

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.bits())

    def count(self):
        """Returns the number of items in the set (cardinality).

        >>> Numbers('100011').count()
        3
        """
        return bin(self).count('1')

    def all(self):
        """Return True iff all bits are set (the set is the universe)."""
        return self == self.supremum

    def any(self):
        """Return True iff any bit is set (the set is nonempty)."""
        return self != self.infimum

    def shortcolex(self):
        """Return sort key for short colexicographical order."""
        return bin(self).count('1'), self

    def shortlex(self):
        """Return sort key for short lexicographical order."""
        return bin(self).count('1'), self._reinverted(self._len)

    def longcolex(self):
        """Return sort key for long colexicographical order."""
        return -bin(self).count('1'), self

    def longlex(self):
        """Return sort key for long lexicographical order."""
        return -bin(self).count('1'), self._reinverted(self._len)

    def powerset(self, start=None, excludestart=False):
        """Yield combinations from start to self in short lexicographic order.

        >>> [n.members() for n in list(Numbers.supremum.powerset())[22:25]]
        [(1, 2, 3), (1, 2, 4), (1, 2, 5)]
        """
        if start is None:
            start = self.infimum
            other = [a for a in self._atoms if self & a]
        else:
            if self | start != self:
                raise ValueError('%r is no proper subset of %r' % (start, self))
            other = self & ~start
            other = [a for a in self._atoms if a & other]
        queue = collections.deque([(start, other)])
        if not excludestart:
            yield start
        Result = self.from_int
        while queue:
            current, other = queue.popleft()
            while other:
                first, other = other[0], other[1:]
                result = Result(current | first)
                yield result
                if other:
                    queue.append((result, other))


def _test(verbose=False):
    global Numbers, Letters
    Numbers = bitset('Numbers', tuple(range(1, 7)))
    Letters = bitset('Letters', tuple('abcdefghijklmnopqrstuvwxyz'))

    import doctest
    doctest.testmod(verbose=verbose, extraglobs=locals())

if __name__ == '__main__':
    _test()
