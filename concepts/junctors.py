# junctors.py - logical relations between contingent boolean vectors

"""Logical relations between sequences of truth conditions.

https://en.wikipedia.org/wiki/Template:Logical_connectives_table_and_Hasse_diagram

https://commons.wikimedia.org/wiki/File:Logical_connectives_Hasse_diagram.svg
https://commons.wikimedia.org/wiki/File:Logical_connectives_table.svg
https://commons.wikimedia.org/wiki/File:Logic_matrix;_operations.svg
"""

from itertools import combinations, chain

from ._compat import zip, with_metaclass

__all__ = ['Relations']


class Relations(list):
    """Logical relations between items from their contingent truth condition sequences.

    >>> Relations(['+1', '-2 -3'], [(True, False, False), (True, False, False)])
    [<Equivalent('+1', '-2 -3')>]

    >>> Relations(['+1', '-1'], [(True, False, False), (False, True, True)])
    [<Complement('+1', '-1')>]

    >>> Relations(['+1', '+3'], [(True, False, False), (False, False, True)])
    [<Incompatible('+1', '+3')>]

    >>> Relations(['+1', '-3'], [(True, False, False), (True, True, False)])
    [<Implication('+1', '-3')>]

    >>> Relations(['-1', '-3'], [(False, True, True), (True, True, False)])
    [<Subcontrary('-1', '-3')>]

    >>> Relations(['+1', 'sg'], [(True, True, False, False), (True, False, True, False)])
    [<Orthogonal('+1', 'sg')>]


    >>> r = Relations(['Never', 'Always', 'Possibly', 'Maybe'],
    ...     [(False, False), (True, True), (True, False), (True, False)],
    ...     include_unary=True)

    >>> r  # doctest: +NORMALIZE_WHITESPACE
    [<Contradiction('Never')>, <Tautology('Always')>,
     <Contingency('Possibly')>, <Contingency('Maybe')>,
     <Equivalent('Possibly', 'Maybe')>]

    >>> print(r)  # noqa: W291
    Never    contradiction 
    Always   tautology    
    Possibly contingency  
    Maybe    contingency  
    Possibly equivalent   Maybe

    >>> print(r[0])
    Never contradiction

    >>> print(r[-1])
    Possibly equivalent Maybe
    """

    def __init__(self, items, booleans, include_unary=False):
        """Filter out items with tautological or contradictory booleans."""
        unary = [Relation(i, None, bools)
                 for i, bools in zip(items, booleans)]
        combos = combinations(((u.left, u.bools)
                               for u in unary if u.__class__ is Contingency), 2)
        binary = (Relation(l, r, zip(lbools, rbools))
                  for (l, lbools), (r, rbools) in combos)

        members = chain(unary, binary) if include_unary else binary

        super(Relations, self).__init__(members)
        self.sort(key=lambda r: r.order)

    def __str__(self):
        return self.tostring(exclude_orthogonal=True)

    def tostring(self, exclude_orthogonal=False):
        tmpl = '%%-%ds %%-12s %%s' % max(len(str(r.left)) for r in self)
        if exclude_orthogonal:
            self = (r for r in self if r.__class__ is not Orthogonal)
        return '\n'.join(tmpl % (r.left, r.kind, r.right) for r in self)


class RelationMeta(type):
    """Build and retrieve conrete ``Relation`` subclasses from docstring tables."""

    __map = {}

    def __init__(self, name, bases, dct):  # noqa: N804
        if 'binary' not in dct:
            return

        table = self.__doc__.strip().partition('\n\n')[2].strip().splitlines()
        flags = {'T': True, 'F': False}
        if self.binary:
            def get_prop(fg):
                return tuple(flags[f] for f in fg.strip())
        else:
            def get_prop(fg):
                return flags[fg.strip()]

        properties = [get_prop(fg) for fg in table[0].strip('|').split('|')]
        obj_flags = [(obj.split(), [bool(p.strip()) for p in props.split('|')])
            for obj, props in (l.strip('|').partition('|')[::2] for l in table[1:])]

        for index, ((name, symbol, order), flags) in enumerate(obj_flags):
            pattern = frozenset(p for p, f in zip(properties, flags) if f)
            ns = {'index': index, 'order': int(order),
                  'kind': name.lower(), 'symbol': symbol, 'pattern': pattern}
            cls = type(name, (self,), ns)
            globals()[cls.__name__] = self.__map[pattern] = cls
            __all__.append(cls.__name__)

    def __call__(self, left, right, pairs):  # noqa: N804
        self = self.__map[frozenset(pairs)]
        if not self.binary:
            right = pairs
        elif self is Replication:
            self = Implication
            left, right = right, left
        return super(RelationMeta, self).__call__(left, right)


class Relation(with_metaclass(RelationMeta, object)):
    """Logical characteristics of truth condition sequences."""


class Unary(Relation):
    """Logical property of a single truth condition sequence.

                      |T|F|
    Contingency   ~  0|X|X|
    Contradiction t -2| |X|
    Tautology     f -1|X| |
    """

    binary = False

    right = ''

    def __init__(self, left, bools):
        self.left = left
        self.bools = bools

    def __str__(self):
        return '%s %s' % (self.left, self.kind)

    def __repr__(self):
        return '<%s(%r)>' % (self.__class__.__name__, self.left)


class Binary(Relation):
    """Logical relation between two contingent truth condition sequences.

                      |TT|TF|FT|FF|
    Orthogonal   ~   7| X| X| X| X|
    Subcontrary  v   6| X| X| X|  |
    Implication  ->  4| X|  | X| X|
    Replication  <-  5| X| X|  | X|
    Equivalent   <-> 1| X|  |  | X|
    Incompatible !   3|  | X| X| X|
    Complement   >-< 2|  | X| X|  |
    """

    binary = True

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __str__(self):
        return '%s %s %s' % (self.left, self.kind, self.right)

    def __repr__(self):
        return '<%s(%r, %r)>' % (self.__class__.__name__, self.left, self.right)
