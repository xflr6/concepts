# contexts.py - create FCA context and provide derivation and neighbors

"""Formal Concept Analysis contexts."""

import heapq

from ._compat import py3_unicode_to_str

from . import formats, matrices, junctors, tools, lattices

__all__ = ['Context']


@py3_unicode_to_str
class Context(object):
    """Formal context defining a relation between objects and properties.

    >>> c = Context.fromstring('''
    ...    |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    ... 1sg| X|  |  | X|  | X|  X|   |   |  X|
    ... 1pl| X|  |  | X|  | X|   |  X|  X|   |
    ... 2sg|  | X| X|  |  | X|  X|   |   |  X|
    ... 2pl|  | X| X|  |  | X|   |  X|  X|   |
    ... 3sg|  | X|  | X| X|  |  X|   |   |  X|
    ... 3pl|  | X|  | X| X|  |   |  X|  X|   |
    ... ''')

    >>> print(c)  # doctest: +ELLIPSIS
    <Context object mapping 6 objects to 10 properties at 0x...>
           |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
        1sg|X |  |  |X |  |X |X  |   |   |X  |
        1pl|X |  |  |X |  |X |   |X  |X  |   |
        2sg|  |X |X |  |  |X |X  |   |   |X  |
        2pl|  |X |X |  |  |X |   |X  |X  |   |
        3sg|  |X |  |X |X |  |X  |   |   |X  |
        3pl|  |X |  |X |X |  |   |X  |X  |   |


    >>> c.objects
    ('1sg', '1pl', '2sg', '2pl', '3sg', '3pl')

    >>> c.properties
    ('+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl')

    >>> c.bools  # doctest: +NORMALIZE_WHITESPACE
    [(True, False, False, True, False, True, True, False, False, True),
     (True, False, False, True, False, True, False, True, True, False),
     (False, True, True, False, False, True, True, False, False, True),
     (False, True, True, False, False, True, False, True, True, False),
     (False, True, False, True, True, False, True, False, False, True),
     (False, True, False, True, True, False, False, True, True, False)]


    >>> c.intension(['1sg'])
    ('+1', '-2', '-3', '+sg', '-pl')

    >>> c.extension(['+1'])
    ('1sg', '1pl')


    >>> c.neighbors(['1sg', '1pl', '2pl'])
    [(('1sg', '1pl', '2sg', '2pl', '3sg', '3pl'), ())]


    >>> c[('1sg', '1pl', '2pl')]
    (('1sg', '1pl', '2sg', '2pl'), ('-3',))

    >>> c[('-1', '-sg')]
    (('2pl', '3pl'), ('-1', '+pl', '-sg'))


    >>> print(c.relations())
    +sg equivalent   -pl
    +pl equivalent   -sg
    +1  complement   -1
    +2  complement   -2
    +3  complement   -3
    +sg complement   +pl
    +sg complement   -sg
    +pl complement   -pl
    -sg complement   -pl
    +1  incompatible +2
    +1  incompatible +3
    +2  incompatible +3
    +1  implication  -2
    +1  implication  -3
    +2  implication  -1
    +3  implication  -1
    +2  implication  -3
    +3  implication  -2
    -1  subcontrary  -2
    -1  subcontrary  -3
    -2  subcontrary  -3
    """

    Lattice = lattices.Lattice

    @classmethod
    def fromstring(cls, source, frmat='table', **kwargs):
        """Return a new context from string source in given format."""
        frmat = formats.Format[frmat]
        objects, properties, bools = frmat.loads(source, **kwargs)
        return cls(objects, properties, bools)

    @classmethod
    def fromfile(cls, filename, frmat='cxt', encoding=None, **kwargs):
        """Return a new context from file source in given format."""
        frmat = formats.Format[frmat]
        objects, properties, bools = frmat.load(filename, encoding, **kwargs)
        return cls(objects, properties, bools)

    def __init__(self, objects, properties, bools):
        """Create context from objects, properties, and correspondence."""
        objects = tuple(objects)
        properties = tuple(properties)

        if len(set(objects)) != len(objects):
            raise ValueError('%r duplicate objects: %r' % (
                self.__class__, objects))
        if len(set(properties)) != len(properties):
            raise ValueError('%r duplicate properties: %r' % (
                self.__class__, properties))
        if not set(objects).isdisjoint(properties):
            raise ValueError('%r objects and properties overlap: %r' % (
                self.__class__, set(objects) & set(properties)))
        if (len(bools) != len(objects)
            or {len(b) for b in bools} != {len(properties)}):
            raise ValueError('%r bools is not %d items of length %d' % (
                self.__class__, len(objects), len(properties)))

        self._intents, self._extents = matrices.Relation('Intent', 'Extent',
            properties, objects, bools)

        self._Intent = self._intents.BitSet
        self._Extent = self._extents.BitSet

    def __getstate__(self):
        """Pickle as context as (intents, extents) tuple."""
        return self._intents, self._extents

    def __setstate__(self, state):
        """Unpickle context from (intents, extents) tuple."""
        self._intents, self._extents = state
        self._Intent = self._intents.BitSet
        self._Extent = self._extents.BitSet

    def __eq__(self, other):
        if not isinstance(other, Context):
            raise TypeError('can only compare to a context.')
        return (self.objects == other.objects and self.properties == other.properties
            and self.bools == other.bools)

    def __ne__(self, other):
        return not self == other

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

    def _neighbors(self, objects):
        """Yield upper neighbors from extent (in colex order?).

        cf. C. Lindig. 2000. Fast Concept Analysis.
        """
        doubleprime = self._extents.doubleprime
        minimal = ~objects
        for add in self._Extent.atomic(minimal):
            objects_ = objects | add
            extent, intent = doubleprime(objects_)
            if minimal & extent & ~objects_:
                minimal &= ~add
            else:
                yield extent, intent

    def _lattice(self, infimum=()):
        """Return list of (extent, indent, upper, lower) in short lexicographic order.

        cf. C. Lindig. 2000. Fast Concept Analysis.
        """
        extent, intent = self._Extent.frommembers(infimum).doubleprime()
        concept = (extent, intent, [], [])
        result = []
        heap = [(extent.shortlex(), concept)]
        mapping = {extent: concept}
        push, pop = heapq.heappush, heapq.heappop
        while heap:
            concept = pop(heap)[1]
            result.append(concept)
            for extent, intent in self._neighbors(concept[0]):
                if extent in mapping:
                    neighbor = mapping[extent]
                else:
                    neighbor = mapping[extent] = (extent, intent, [], [])
                    push(heap, (extent.shortlex(), neighbor))
                concept[2].append(neighbor[0])
                neighbor[3].append(concept[0])
        return result

    def intension(self, objects, raw=False):
        """Return all properties shared by the given objects."""
        intent = self._Extent.frommembers(objects).prime()
        if raw:
            return intent
        return intent.members()

    def extension(self, properties, raw=False):
        """Return all objects sharing the given properties."""
        extent = self._Intent.frommembers(properties).prime()
        if raw:
            return extent
        return extent.members()

    def neighbors(self, objects, raw=False):
        """Return the upper neighbors of the concept having all given objects."""
        objects = self._Extent.frommembers(objects).double()
        if raw:
            return list(self._neighbors(objects))
        return [(extent.members(), intent.members())
            for extent, intent in self._neighbors(objects)]

    def __getitem__(self, items, raw=False):
        """Return (extension, intension) pair by shared objects or properties."""
        try:
            extent = self._Extent.frommembers(items)
        except KeyError:
            intent = self._Intent.frommembers(items)
            intent, extent = intent.doubleprime()
        else:
            extent, intent = extent.doubleprime()
        if raw:
            return extent, intent
        return extent.members(), intent.members()

    def __str__(self):
        return '%r\n%s' % (self, self.tostring(escape=True, indent=4))

    def __unicode__(self):
        return '%r\n%s' % (self, self.tostring(indent=4))

    def __repr__(self):
        return '<%s object mapping %d objects to %d properties at %#x>' % (
            self.__class__.__name__, len(self._Extent._members),
            len(self._Intent._members), id(self))

    def tostring(self, frmat='table', **kwargs):
        """Return the context serialized in the given string-based format."""
        frmat = formats.Format[frmat]
        return frmat.dumps(self._Extent._members, self._Intent._members,
            self._intents.bools(), **kwargs)

    def tofile(self, filename, frmat='cxt', encoding='utf8', **kwargs):
        """Save the context serialized to file in the given format."""
        frmat = formats.Format[frmat]
        return frmat.dump(filename, self._Extent._members, self._Intent._members,
            self._intents.bools(), encoding, **kwargs)

    @property
    def objects(self):
        """(Names of the) objects described by the context."""
        return self._Extent._members

    @property
    def properties(self):
        """(Names of the) properties that describe the objects."""
        return self._Intent._members

    @property
    def bools(self):
        """Row-wise boolean relation matrix between objects and properties."""
        return self._intents.bools()

    def relations(self):
        """Return the logical relations between the context properties."""
        return junctors.Relations(self.properties, self._extents.bools())

    @tools.lazyproperty
    def lattice(self):
        """Return the concept lattice of the formal context."""
        return self.Lattice(self)
