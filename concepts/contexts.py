# contexts.py - create FCA context and provide derivation and neighbors

"""Formal Concept Analysis contexts."""

import formats
import matrices
import lattices
import relations
from tools import lazyproperty

__all__ = ['Context']


class Context(object):
    """Formal context defining a relation between objects and properties.

    >>> c = Context.from_string('''
    ...    |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    ... 1sg| X|  |  | X|  | X|  X|   |   |  X|
    ... 1pl| X|  |  | X|  | X|   |  X|  X|   |
    ... 2sg|  | X| X|  |  | X|  X|   |   |  X|
    ... 2pl|  | X| X|  |  | X|   |  X|  X|   |
    ... 3sg|  | X|  | X| X|  |  X|   |   |  X|
    ... 3pl|  | X|  | X| X|  |   |  X|  X|   |
    ... ''')

    >>> c.objects
    ('1sg', '1pl', '2sg', '2pl', '3sg', '3pl')

    >>> c.properties
    ('+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl')
    """

    @classmethod
    def from_string(cls, source, frmat='table'):
        """Return a new context from string source in given format."""
        frmat = formats.Format[frmat]
        objects, properties, bools = frmat.loads(source)
        return cls(objects, properties, bools)

    def __init__(self, objects, properties, bools):
        objects = tuple(objects)
        properties = tuple(properties)

        if len(set(objects)) != len(objects):
            raise ValueError('%r duplicate objects: %r' % (self.__class__, objects))
        if len(set(properties)) != len(properties):
            raise ValueError('%r duplicate properties: %r' % (self.__class__, properties))
        if not set(objects).isdisjoint(properties):
            raise ValueError('%r objects and properties overlap: %r' % (self.__class__, set(objects) & set(properties)))
        if (len(bools) != len(objects)
            or {len(b) for b in bools} != {len(properties)}):
            raise ValueError('%r bools is not %d items of length %d' % (self.__class__, len(objects), len(properties)))

        self._intents, self._extents = matrices.relation('Intent', 'Extent',
            properties, objects, bools)

        self._Intent = self._intents.BitSet
        self._Extent = self._extents.BitSet

    def _minimal(self, extent, intent):
        """Return short lexicograpically minimum intent generating extent."""
        return next(self._minimize(extent, intent))

    def _minimize(self, extent, intent):
        """Yield short lexicograpically ordered extent generating intents."""
        if not extent:
            yield intent
            return
        for it in intent.powerset():
            if it.prime() == extent:
                yield it

    def _neighbors(self, objects):  # TODO: check order
        """Yield upper neighbors from extent (cf. C. Lindig. 2000. Fast Concept Analysis)."""
        Extent = self._Extent.from_int
        minimal = ~objects
        remaining = [a for a in self._Extent._atoms if a & minimal]
        for add in remaining:
            objects_ = Extent(objects | add)
            intent = objects_.prime()
            extent = intent.prime()
            if minimal & (extent & ~objects_):
                minimal &= ~add
            else:
                yield extent, intent

    def __getitem__(self, items, raw=False):
        """Return (extension, intension) pair by shared objects or properties.

        >>> c['1sg 1pl 2pl']
        (('1sg', '1pl', '2sg', '2pl'), ('-3',))

        >>> c['-1 -sg']
        (('2pl', '3pl'), ('-1', '+pl', '-sg'))
        """
        try:
            extent = self._Extent.from_members(items)
        except KeyError:
            intent = self._Intent.from_members(items)
            extent = intent.prime()
            intent = extent.prime()
        else:
            intent = extent.prime()
            extent = intent.prime()
        if raw:
            return extent, intent
        return extent.members(), intent.members()

    def intension(self, objects):
        """Return all properties shared by the given objects.

        >>> c.intension('1sg')
        ('+1', '-2', '-3', '+sg', '-pl')
        """
        return self._Extent.from_members(objects).prime().members()

    def extension(self, properties):
        """Return all objects sharing the given properties.

        >>> c.extension('+1')
        ('1sg', '1pl')
        """
        return self._Intent.from_members(properties).prime().members()

    def neighbors(self, objects):
        """Return the upper neighbors of the concept having all given objects.

        >>> c.neighbors('1sg 1pl 2pl')
        [(('1sg', '1pl', '2sg', '2pl', '3sg', '3pl'), ())]
        """
        objects = self._Extent.from_members(objects).double()
        return [(extent.members(), intent.members())
            for extent, intent in self._neighbors(objects)]

    def __repr__(self):
        return '<%s object mapping %d objects to %d properties at %X>' % (
            self.__class__.__name__, len(self._Extent._members), len(self._Intent._members),
            id(self))

    def __str__(self):
        return '%r\n%s' % (self, self.to_string(indent=4))

    def to_string(self, frmat='table', **kwargs):
        """Return the context serialized in the given string-based format."""
        frmat = formats.Format[frmat]
        return frmat.dumps(self._Extent._members, self._Intent._members,
            self._intents.bools(), **kwargs)

    @property
    def objects(self):
        return self._Extent._members

    @property
    def properties(self):
        return self._Intent._members

    @property
    def bools(self):
        return self._intents.bools()

    @lazyproperty
    def lattice(self):
        """Return the concept lattice of the formal context."""
        return lattices.Lattice(self)

    def relations(self):
        """Return the logical relations between the context properties."""
        return relations.relations(self.properties, self._extents.bools())


def _test(verbose=False):
    global c
    c = Context.from_string('''
       |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    1sg| X|  |  | X|  | X|  X|   |   |  X|
    1pl| X|  |  | X|  | X|   |  X|  X|   |
    2sg|  | X| X|  |  | X|  X|   |   |  X|
    2pl|  | X| X|  |  | X|   |  X|  X|   |
    3sg|  | X|  | X| X|  |  X|   |   |  X|
    3pl|  | X|  | X| X|  |   |  X|  X|   |
    ''')

    import doctest
    doctest.testmod(verbose=verbose, extraglobs=locals())

    c = Context.from_string('''
       |+1|-1|+2|-2|+3|-3|+sg|+du|+pl|-sg|-du|-pl|
    1s | X|  |  | X|  | X|  X|   |   |   |  X|  X|
    1de| X|  |  | X|  | X|   |  X|   |  X|   |  X|
    1pe| X|  |  | X|  | X|   |   |  X|  X|  X|   |
    1di| X|  | X|  |  | X|   |  X|   |  X|   |  X|
    1pi| X|  | X|  |  | X|   |   |  X|  X|  X|   |
    2s |  | X| X|  |  | X|  X|   |   |   |  X|  X|
    2d |  | X| X|  |  | X|   |  X|   |  X|   |  X|
    2p |  | X| X|  |  | X|   |   |  X|  X|  X|   |
    3s |  | X|  | X| X|  |  X|   |   |   |  X|  X|
    3d |  | X|  | X| X|  |   |  X|   |  X|   |  X|
    3p |  | X|  | X| X|  |   |   |  X|  X|  X|   |
    ''')
    print c


if __name__ == '__main__':
    _test()
