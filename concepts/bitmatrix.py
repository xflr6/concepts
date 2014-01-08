# bitmatrix.py - boolean matrix as row bitsets and column bitsets

"""Collections of bitsets and boolean matrices as row and column vectors."""

from itertools import izip, imap
import copy_reg

import bitsets

__all__ = ['relation']


def bitset_collection(name, members, cached=None, base=None):
    """Return concrete BitSets subclass."""
    cls = bitsets.bitset(name, members, cached)
    if (name, members, cached) not in bitsets._registry:  # created
        if base is None:
            base = BitSets
        cls.BitSets = base._make_subclass(name, cls)
    return cls.BitSets


class BitSetsMeta(type):

    def _make_subclass(self, name, cls):
        dct = {'BitSet': cls}
        if '__slots__' in self.__dict__:
            dct['__slots__'] = self.__slots__
        return type('%ss' % name, (self,), dct)

    def __repr__(self):
        if not hasattr(self, 'BitSet'):
            return type.__repr__(self)
        return '<class %s.bitset_collection(%r, %r, id=%#x)>' % (self.__module__,
            self.BitSet.__name__, self.BitSet._members, self.BitSet._id)

    def __reduce__(self):
        if not hasattr(self, 'BitSet'):
            return self.__name__
        return bitset_collection, (self.BitSet.__name__, self.BitSet._members, self.BitSet._id)


copy_reg.pickle(BitSetsMeta, BitSetsMeta.__reduce__)


class BitSets(tuple):
    """Immutable ordered collection of bitsets.

    >>> Numberss = bitset_collection('Numbers', tuple(range(1, 7)))

    >>> Numberss.from_bools([(True, False, True), (True, True, False)])
    Numberss('101000', '110000')

    >>> Numberss('101000').bools()
    [(True, False, True, False, False, False)]
    """

    __metaclass__ = BitSetsMeta

    __slots__ = ()

    @classmethod
    def from_bools(cls, bools):
        """Bitset collection from iterable of boolean evaluable iterables."""
        return cls.from_bitsets(imap(cls.BitSet.from_bools, bools))

    from_bitsets = classmethod(tuple.__new__)

    def __new__(cls, *bits):
        return cls.from_bitsets(imap(cls.BitSet, bits))

    def bools(self):
        """Return the collection as list of boolean set membership sequences."""
        return [b.bools() for b in self]

    def iterbools(self):
        atoms = self.BitSet._atoms
        return ((not not b & a for a in atoms) for b in self)

    def __repr__(self):
        items = ', '.join('%r' % b.bits() for b in self)
        return '%s(%s)' % (self.__class__.__name__, items)


class Vectors(BitSets):
    """Paired row or column vector collection of a relation as boolean matrix."""

    def _pair_with(self, other, relation, index):
        if hasattr(self, 'prime'):
            raise RuntimeError('%r attempt _pair_with' % self)

        self.twin = other
        self.relation = relation
        self.index = index

        _prime = other.BitSet.from_bools
        _double = self.BitSet.from_bools

        def prime(bitset):
            """FCA derivation operator (extent->intent, intent->extent)."""
            return _prime(bitset & b == bitset for b in self)

        def double(bitset):
            """FCA double derivation operator (extent->extent, intent->intent)."""
            prime = _prime(bitset & b == bitset for b in self)
            return _double(prime & b == prime for b in other)

        self.prime = self.BitSet.prime = prime
        self.double = self.BitSet.double = double

    def __reduce__(self):
        return self.relation, (self.index,)
    

class relation(tuple):
    """Binary relation as interconnected pair of bitset collections.

    >>> br = relation('Condition', 'Symbol',
    ... ('TT', 'TF', 'FT', 'FF'), ('->', '<-'),
    ... [(True, False, True, True), (True, True, False, True)])

    >>> br
    <relation(Conditions('1011', '1101'), Symbols('11', '01', '10', '11'))>

    >>> br[1].BitSet.from_members('-> <-').prime().members()
    ('TT', 'FF')
    """ 

    __slots__ = ()

    def __new__(cls, xname, yname, xmembers, ymembers, xbools, xcached=False, ycached=False):
        X = bitset_collection(xname, xmembers, xcached, Vectors)
        Y = bitset_collection(yname, ymembers, ycached, Vectors)

        x = X.from_bools(xbools)
        y = Y.from_bools(izip(*x.bools()))

        self = super(relation, cls).__new__(cls, (x, y))

        x._pair_with(y, self, 0)
        y._pair_with(x, self, 1)

        return self

    __call__ = tuple.__getitem__

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self[0], self[1])

    def __reduce__(self):
        X, Y = (twin.BitSet for twin in self)
        args = (X.__name__, Y.__name__, X._members, Y._members, self[0].bools(),
            X._id, Y._id)
        return relation, args
        

def _test(verbose=False):
    import doctest
    doctest.testmod(verbose=verbose)

if __name__ == '__main__':
    _test()
