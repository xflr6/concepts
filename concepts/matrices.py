# matrices.py - boolean matrices as row bitsets and column bitsets

"""Boolean matrices as collections of row and column vectors."""

import bitsets

from ._compat import zip

__all__ = ['Relation']


Vector = bitsets.bases.MemberBits
"""Single row or column of a boolean matrix as bit vector."""


class Vectors(bitsets.series.Tuple):
    """Paired collection of rows or columns of a boolean matrix relation."""

    def _pair_with(self, relation, index, other):
        if hasattr(self, 'prime'):
            raise RuntimeError('%r attempt _pair_with %r' % (self, other))

        self.relation = relation
        self.relation_index = index

        Prime = other.BitSet.supremum  # noqa: N806
        Double = self.BitSet.supremum  # noqa: N806

        _prime = other.BitSet.fromint
        _double = self.BitSet.fromint

        def prime(bitset):
            """FCA derivation operator (extent->intent, intent->extent)."""
            prime = Prime
            for o in other:
                if bitset & 1:
                    prime &= o
                bitset >>= 1
                if not bitset:
                    break
            return _prime(prime)

        def double(bitset):
            """FCA double derivation operator (extent->extent, intent->intent)."""
            prime = Prime
            for o in other:
                if bitset & 1:
                    prime &= o
                bitset >>= 1
                if not bitset:
                    break
            double = Double
            for s in self:
                if prime & 1:
                    double &= s
                prime >>= 1
                if not prime:
                    break
            return _double(double)

        def doubleprime(bitset):
            """FCA single and double derivation (extent->extent+intent, intent->intent+extent)."""
            prime = Prime
            for o in other:
                if bitset & 1:
                    prime &= o
                bitset >>= 1
                if not bitset:
                    break
            bitset = prime
            double = Double
            for s in self:
                if bitset & 1:
                    double &= s
                bitset >>= 1
                if not bitset:
                    break
            return _double(double), _prime(prime)

        self.prime = self.BitSet.prime = prime
        self.double = self.BitSet.double = double
        self.doubleprime = self.BitSet.doubleprime = doubleprime

    def __reduce__(self):
        return self.relation, (self.relation_index,)


class Relation(tuple):
    """Binary relation as interconnected pair of bitset collections.

    >>> br = Relation('Condition', 'Symbol',
    ... ('TT', 'TF', 'FT', 'FF'), ('->', '<-'),
    ... [(True, False, True, True), (True, True, False, True)])

    >>> br
    <Relation(ConditionVectors('1011', '1101'), SymbolVectors('11', '01', '10', '11'))>

    >>> br[1].BitSet.frommembers(('->', '<-')).prime().members()
    ('TT', 'FF')
    """

    __slots__ = ()

    def __new__(cls, xname, yname, xmembers, ymembers, xbools, _ids=None):
        if _ids is not None:  # unpickle reconstruction
            xid, yid = _ids
            X = bitsets.meta.bitset(xname, xmembers, xid, Vector, None, Vectors)  # noqa: N806
            Y = bitsets.meta.bitset(yname, ymembers, yid, Vector, None, Vectors)  # noqa: N806
        else:
            X = bitsets.bitset(xname, xmembers, Vector, tuple=Vectors)  # noqa: N806
            Y = bitsets.bitset(yname, ymembers, Vector, tuple=Vectors)  # noqa: N806

        x = X.Tuple.frombools(xbools)
        y = Y.Tuple.frombools(zip(*x.bools()))

        self = super(Relation, cls).__new__(cls, (x, y))

        x._pair_with(self, 0, y)
        y._pair_with(self, 1, x)

        return self

    __call__ = tuple.__getitem__

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self[0], self[1])

    def __reduce__(self):
        X, Y = (v.BitSet for v in self)  # noqa: N806
        bools = self[0].bools()
        ids = (X._id, Y._id)
        args = (X.__name__, Y.__name__, X._members, Y._members, bools, ids)
        return self.__class__, args
