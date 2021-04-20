# matrices.py - boolean matrices as row bitsets and column bitsets

"""Boolean matrices as collections of row and column vectors."""

import bitsets

__all__ = ['Relation']


Vector = bitsets.bases.MemberBits
"""Single row or column of a boolean matrix as bit vector."""


class Vectors(bitsets.series.Tuple):
    """Paired collection of rows or columns of a boolean matrix relation.

    Trailing zeros see https://stackoverflow.com/q/63917579/3456664
    """

    def _pair_with(self, relation, index, other):
        if hasattr(self, 'prime'):
            raise RuntimeError(f'{self!r} attempt _pair_with {other!r}')

        self.relation = relation
        self.relation_index = index

        Prime = other.BitSet.supremum  # noqa: N806
        Double = self.BitSet.supremum  # noqa: N806

        _prime = other.BitSet.fromint
        _double = self.BitSet.fromint

        def prime(bitset):
            """FCA derivation operator (extent->intent, intent->extent)."""
            prime = Prime

            i = 0
            while bitset:
                trailing_zeros = (bitset & -bitset).bit_length() - 1
                if trailing_zeros:
                    shift = trailing_zeros
                else:
                    prime &= other[i]
                    shift = 1
                bitset >>= shift
                i += shift

            return _prime(prime)

        def double(bitset):
            """FCA double derivation operator (extent->extent, intent->intent)."""
            prime = Prime

            i = 0
            while bitset:
                trailing_zeros = (bitset & -bitset).bit_length() - 1
                if trailing_zeros:
                    shift = trailing_zeros
                else:
                    prime &= other[i]
                    shift = 1
                bitset >>= shift
                i += shift

            double = Double

            i = 0
            while prime:
                trailing_zeros = (prime & -prime).bit_length() - 1
                if trailing_zeros:
                    shift = trailing_zeros
                else:
                    double &= self[i]
                    shift = 1
                prime >>= shift
                i += shift

            return _double(double)

        def doubleprime(bitset):
            """FCA single and double derivation (extent->extent+intent, intent->intent+extent)."""
            prime = Prime

            i = 0
            while bitset:
                trailing_zeros = (bitset & -bitset).bit_length() - 1
                if trailing_zeros:
                    shift = trailing_zeros
                else:
                    prime &= other[i]
                    shift = 1
                bitset >>= shift
                i += shift

            bitset = prime
            double = Double

            i = 0
            while bitset:
                trailing_zeros = (bitset & -bitset).bit_length() - 1
                if trailing_zeros:
                    shift = trailing_zeros
                else:
                    double &= self[i]
                    shift = 1
                bitset >>= shift
                i += shift

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

        self = super().__new__(cls, (x, y))

        x._pair_with(self, 0, y)
        y._pair_with(self, 1, x)

        return self

    __call__ = tuple.__getitem__

    def __repr__(self):
        return f'<{self.__class__.__name__}({self[0]!r}, {self[1]!r})>'

    def __reduce__(self):
        X, Y = (v.BitSet for v in self)  # noqa: N806
        bools = self[0].bools()
        ids = (X._id, Y._id)
        args = (X.__name__, Y.__name__, X._members, Y._members, bools, ids)
        return self.__class__, args
