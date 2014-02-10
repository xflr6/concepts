# junctors.py - logical relations between contingent boolean vectors

"""Logical relations between sequences of truth conditions.

http://commons.wikimedia.org/wiki/File:Logical_connectives_Hasse_diagram.svg
http://en.wikiversity.org/wiki/File:Logic_matrix;_operations.svg
"""

from itertools import izip, combinations

__all__ = ['relations']


class relations(list):
    """Logical relations between items from their contingent truth condition sequences.

    >>> relations(['+1', '-2 -3'], [(True, False, False), (True, False, False)])
    [<'+1' Equivalent '-2 -3'>]

    >>> relations(['+1', '-1'], [(True, False, False), (False, True, True)])
    [<'+1' Complement '-1'>]

    >>> relations(['+1', '+3'], [(True, False, False), (False, False, True)])
    [<'+1' Incompatible '+3'>]

    >>> relations(['+1', '-3'], [(True, False, False), (True, True, False)])
    [<'+1' Implication '-3'>]

    >>> relations(['-1', '-3'], [(False, True, True), (True, True, False)])
    [<'-1' Subcontrary '-3'>]

    >>> relations(['+1', 'sg'], [(True, True, False, False), (True, False, True, False)])
    [<'+1' Orthogonal 'sg'>]
    """

    def __init__(self, items, booleans):
        """Filter out items with tautological or contradictory booleans."""
        unary = [Relation(i, None, bools)
            for i, bools in izip(items, booleans)]
        combos = combinations(((u.left, u.bools)
            for u in unary if u.__class__ is Contingency), 2)
        binary = (Relation(l, r, izip(lbools, rbools))
            for (l, lbools), (r, rbools) in combos)

        super(relations, self).__init__(binary)
        self.sort(key=lambda r: r.order)

    def __str__(self, full=True):
        tmpl = '%%-%ds %%-12s %%s' % max(len(str(r.left)) for r in self)
        if not full:
            self = (r for r in self if r.__class__ is not Orthogonal)
        return '\n'.join(tmpl % (r.left, r.kind, r.right) for r in self)


class RelationMeta(type):
    """Build and retrieve conrete relation subclasses from docstring tables."""

    __map = {}

    def __init__(self, name, bases, dct):
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
            pattern = frozenset(p for p, f in izip(properties,flags) if f)
            ns = {'index': index, 'order': int(order),
                'kind': name.lower(), 'symbol': symbol, 'pattern': pattern}
            cls = type(name, (self,), ns)
            globals()[cls.__name__] = self.__map[pattern] = cls
            __all__.append(cls.__name__)

    def __call__(self, left, right, pairs):
        self = self.__map[frozenset(pairs)]
        if not self.binary:
            right = pairs
        elif self is Replication:
            self = Implication
            left, right = right, left
        return super(RelationMeta, self).__call__(left, right)


class Relation(object):
    """Logical characteristics of truth condition sequences."""

    __metaclass__ = RelationMeta


class Unary(Relation):
    """Logical property of a single truth condition sequence.

                      |T|F|
    Contingency   ~ 0 |X|X|
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
        return '<%r %s>' % (self.left, self.__class__.__name__)


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
        return '<%r %s %r>' % (self.left, self.__class__.__name__, self.right)
