# matrices.py - boolean matrices as row bitsets and column bitsets

"""Boolean matrices as collections of row and column vectors."""

from itertools import imap, izip

import bitsets

__all__ = ['relation']


def from_members(cls, members=()):
    """Create a set from an iterable of members or a space/comma separated string."""
    if isinstance(members, basestring):
        members = members.replace(',', ' ').split()
    return cls.from_int(sum(imap(cls._map.__getitem__, set(members))))


class Vectors(bitsets.series.Tuple):
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
    <relation(ConditionVectors('1011', '1101'), SymbolVectors('11', '01', '10', '11'))>

    >>> br[1].BitSet.from_members('-> <-').prime().members()
    ('TT', 'FF')
    """ 

    __slots__ = ()

    def __new__(cls, xname, yname, xmembers, ymembers, xbools, _ids=None):
        base = bitsets.bases.MemberBits
        if _ids is not None:
            # unpickle reconstruction
            xid, yid = _ids
            X = bitsets.meta.bitset(xname, xmembers, xid, base, None, Vectors)
            Y = bitsets.meta.bitset(yname, ymembers, yid, base, None, Vectors)
        else:
            X = bitsets.bitset(xname, xmembers, base, tuple=Vectors)
            Y = bitsets.bitset(yname, ymembers, base, tuple=Vectors)

        # attach string splitting constructor method
        X.from_members = Y.from_members = classmethod(from_members)

        x = X.Tuple.from_bools(xbools)
        y = Y.Tuple.from_bools(izip(*x.bools()))

        self = super(relation, cls).__new__(cls, (x, y))

        x._pair_with(y, self, 0)
        y._pair_with(x, self, 1)

        return self

    __call__ = tuple.__getitem__

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self[0], self[1])

    def __reduce__(self):
        X, Y = (v.BitSet for v in self)
        bools = self[0].bools()
        ids = (X._id, Y._id)
        args = (X.__name__, Y.__name__, X._members, Y._members, bools, ids)
        return relation, args
        

def _test(verbose=False):
    import doctest
    doctest.testmod(verbose=verbose)

if __name__ == '__main__':
    _test()
