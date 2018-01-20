# lattices.py - build FCA concepts lattice from context

"""Formal Concept Analysis concept lattices."""

import heapq

from ._compat import py3_unicode_to_str

from . import tools, visualize

__all__ = ['Lattice']


@py3_unicode_to_str
class Lattice(object):
    """Formal concept lattice as directed acyclic graph of concepts.

    Usage:

    >>> from concepts import contexts

    >>> l = contexts.Context.fromstring('''
    ...    |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    ... 1sg| X|  |  | X|  | X|  X|   |   |  X|
    ... 1pl| X|  |  | X|  | X|   |  X|  X|   |
    ... 2sg|  | X| X|  |  | X|  X|   |   |  X|
    ... 2pl|  | X| X|  |  | X|   |  X|  X|   |
    ... 3sg|  | X|  | X| X|  |  X|   |   |  X|
    ... 3pl|  | X|  | X| X|  |   |  X|  X|   |
    ... ''').lattice

    >>> print(l)  # doctest: +ELLIPSIS
    <Lattice object of 6 atoms 22 concepts 5 coatoms at 0x...>
        {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]
        {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg
        {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl
        {2sg} <-> [-1 +2 -3 +sg -pl] <=> 2sg
        {2pl} <-> [-1 +2 -3 +pl -sg] <=> 2pl
        {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg
        {3pl} <-> [-1 -2 +3 +pl -sg] <=> 3pl
        {1sg, 1pl} <-> [+1 -2 -3] <=> +1
        {1sg, 2sg} <-> [-3 +sg -pl]
        {1sg, 3sg} <-> [-2 +sg -pl]
        {1pl, 2pl} <-> [-3 +pl -sg]
        {1pl, 3pl} <-> [-2 +pl -sg]
        {2sg, 2pl} <-> [-1 +2 -3] <=> +2
        {2sg, 3sg} <-> [-1 +sg -pl]
        {2pl, 3pl} <-> [-1 +pl -sg]
        {3sg, 3pl} <-> [-1 -2 +3] <=> +3
        {1sg, 2sg, 3sg} <-> [+sg -pl] <=> +sg -pl
        {1pl, 2pl, 3pl} <-> [+pl -sg] <=> +pl -sg
        {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3
        {1sg, 1pl, 3sg, 3pl} <-> [-2] <=> -2
        {2sg, 2pl, 3sg, 3pl} <-> [-1] <=> -1
        {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []


    >>> l.infimum
    <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>

    >>> l.supremum
    <Supremum {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []>

    >>> l.atoms  # doctest: +NORMALIZE_WHITESPACE
    (<Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
     <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>,
     <Atom {2sg} <-> [-1 +2 -3 +sg -pl] <=> 2sg>,
     <Atom {2pl} <-> [-1 +2 -3 +pl -sg] <=> 2pl>,
     <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>,
     <Atom {3pl} <-> [-1 -2 +3 +pl -sg] <=> 3pl>)


    >>> l[('1sg', '1pl', '2pl')]
    <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>

    >>> l[('-1', '-sg')]
    <Concept {2pl, 3pl} <-> [-1 +pl -sg]>

    >>> l(['+1', '-sg'])
    <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>


    >>> l.join([l[('1sg',)], l[('1pl',)], l[('2sg',)]])
    <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>

    >>> l.join([])
    <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>

    >>> l.meet([l[('-1',)], l[('-2',)], l[('-pl',)]])
    <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>

    >>> l.meet([])
    <Supremum {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []>


    >>> l = contexts.Context.fromstring('''
    ...    |+1|-1|+2|-2|+3|-3|+sg|+du|+pl|-sg|-du|-pl|
    ... 1s | X|  |  | X|  | X|  X|   |   |   |  X|  X|
    ... 1de| X|  |  | X|  | X|   |  X|   |  X|   |  X|
    ... 1pe| X|  |  | X|  | X|   |   |  X|  X|  X|   |
    ... 1di| X|  | X|  |  | X|   |  X|   |  X|   |  X|
    ... 1pi| X|  | X|  |  | X|   |   |  X|  X|  X|   |
    ... 2s |  | X| X|  |  | X|  X|   |   |   |  X|  X|
    ... 2d |  | X| X|  |  | X|   |  X|   |  X|   |  X|
    ... 2p |  | X| X|  |  | X|   |   |  X|  X|  X|   |
    ... 3s |  | X|  | X| X|  |  X|   |   |   |  X|  X|
    ... 3d |  | X|  | X| X|  |   |  X|   |  X|   |  X|
    ... 3p |  | X|  | X| X|  |   |   |  X|  X|  X|   |
    ... ''').lattice

    >>> l  # doctest: +ELLIPSIS
    <Lattice object of 11 atoms 65 concepts 6 coatoms at 0x...>
    """

    def __init__(self, context, infimum=()):
        """Create lattice from context."""
        concepts = [Concept(self, *args) for args in context._lattice(infimum)]
        mapping = {c._extent: c for c in concepts}

        shortlex = lambda c: c._extent.shortlex()
        for index, c in enumerate(concepts):
            c.index = index
            upper = (mapping[u] for u in c.upper_neighbors)
            c.upper_neighbors = tuple(sorted(upper, key=shortlex))

        longlex = lambda c: c._extent.longlex()
        atoms = concepts[0].upper_neighbors
        for dindex, c in enumerate(sorted(concepts, key=longlex)):  # downward
            c.dindex = dindex
            lower = (mapping[l] for l in c.lower_neighbors)
            c.lower_neighbors = tuple(sorted(lower, key=longlex))
            e = c._extent
            c.atoms = tuple(a for a in atoms if e | a._extent == e)

        self._annotate(context, mapping)

        self._context = context
        self._concepts = concepts
        self._map = mapping

        self.infimum = self._concepts[0]  #: The most specific concept of the lattice.
        self.infimum.__class__ = Infimum
        self.supremum = self._concepts[-1]  #: The most general concept of the lattice.
        self.supremum.__class__ = Supremum
        for a in self.infimum.upper_neighbors:
            a.__class__ = Atom

    @staticmethod
    def _annotate(context, mapping):
        """Annotate object/attribute concepts with their objects/properties."""
        touched = set()
        for o in context.objects:
            extent = context.extension(context.intension([o]), raw=True)
            c = mapping[extent]
            if c.objects:
                c.objects.append(o)
            else:
                c.objects = [o]
                touched.add(c)

        for c in touched:
            c.objects = tuple(c.objects)

        touched = set()
        for p in context.properties:
            extent = context.extension([p], raw=True)
            c = mapping[extent]
            if c.properties:
                c.properties.append(p)
            else:
                c.properties = [p]
                touched.add(c)

        for c in touched:
            c.properties = tuple(c.properties)

    def __getstate__(self):
        """Pickle lattice as ``(context, concepts)`` tuple."""
        return self._context, self._concepts

    def __setstate__(self, state):
        """Unpickle lattice from ``(context, concepts)`` tuple."""
        self._context, self._concepts = state
        self._map = {c._extent: c for c in self._concepts}
        self.infimum = self._concepts[0]
        self.supremum = self._concepts[-1]

    def __call__(self, properties):
        """Return concept having all given ``properties`` as intension."""
        extent = self._context.extension(properties, raw=True)
        return self._map[extent]

    def __getitem__(self, key):
        """Return concept by index, intension, or extension."""
        if isinstance(key, (int, slice)):
            return self._concepts[key]
        if not key:
            return self.supremum
        extent, intent = self._context.__getitem__(key, raw=True)
        return self._map[extent]

    def __iter__(self):
        """Yield all concepts of the lattice."""
        return iter(self._concepts)

    def __len__(self):
        """Return the number of concepts in the lattice."""
        return len(self._concepts)

    def __str__(self):
        return '%r\n%s' % (self, '\n'.join('    %s' % c for c in self._concepts))

    def __unicode__(self):
        return '%r\n%s' % (self, '\n'.join(u'    %s' % c for c in self._concepts))

    def __repr__(self):
        return '<%s object of %d atoms %d concepts %d coatoms at %#x>' % (
            self.__class__.__name__, len(self.infimum.upper_neighbors),
            len(self._concepts), len(self.supremum.lower_neighbors), id(self))

    @property
    def atoms(self):
        """The minimal non-infimum concepts of the lattice."""
        return self.infimum.upper_neighbors

    def join(self, concepts):
        """Return the nearest concept that subsumes all given concepts."""
        extents = (c._extent for c in concepts)
        join = self._context._Extent.reduce_or(extents)
        return self._map[join.double()]

    def meet(self, concepts):
        """Return the nearest concept that implies all given concepts."""
        extents = (c._extent for c in concepts)
        meet = self._context._Extent.reduce_and(extents)
        return self._map[meet.double()]

    def upset_union(self, concepts):
        """Yield all concepts that subsume any of the given ones."""
        heap = [(c.index, c) for c in tools.maximal(concepts,
            comparison=Concept.properly_subsumes)]
        heapq.heapify(heap)
        push, pop = heapq.heappush, heapq.heappop
        seen = -1
        while heap:
            index, concept = pop(heap)
            if index > seen:
                seen = index
                yield concept
                for c in concept.upper_neighbors:
                    push(heap, (c.index, c))

    def downset_union(self, concepts):
        """Yield all concepts that imply any of the given ones."""
        heap = [(c.dindex, c) for c in tools.maximal(concepts,
            comparison=Concept.properly_implies)]
        heapq.heapify(heap)
        push, pop = heapq.heappush, heapq.heappop
        seen = -1
        while heap:
            index, concept = pop(heap)
            if index > seen:
                seen = index
                yield concept
                for c in concept.lower_neighbors:
                    push(heap, (c.dindex, c))

    def upset_generalization(self, concepts):  # EXPERIMENTAL
        """Yield all concepts that subsume only the given ones."""
        heap = [(c.index, c) for c in tools.maximal(concepts,
            comparison=Concept.properly_subsumes)]
        heapq.heapify(heap)
        push, pop = heapq.heappush, heapq.heappop
        extents = (c._extent for i, c in heap)
        target = self._context._Extent.reduce_or(extents)
        seen = -1
        while heap:
            index, concept = pop(heap)
            if index > seen:
                seen = index
                if concept._extent | target == target:
                    yield concept
                    if concept._extent == target:
                        return
                    for c in concept.upper_neighbors:
                        push(heap, (c.index, c))

    def graphviz(self, filename=None, directory=None, render=False, view=False, **kwargs):
        """Return graphviz source for visualizing the lattice graph."""
        return visualize.lattice(self, filename, directory, render, view, **kwargs)


@py3_unicode_to_str
class Concept(object):
    """Formal concept as pair of extent and intent.

    Usage:

    >>> from concepts import contexts

    >>> l = contexts.Context.fromstring('''
    ...    |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    ... 1sg| X|  |  | X|  | X|  X|   |   |  X|
    ... 1pl| X|  |  | X|  | X|   |  X|  X|   |
    ... 2sg|  | X| X|  |  | X|  X|   |   |  X|
    ... 2pl|  | X| X|  |  | X|   |  X|  X|   |
    ... 3sg|  | X|  | X| X|  |  X|   |   |  X|
    ... 3pl|  | X|  | X| X|  |   |  X|  X|   |
    ... ''').lattice

    >>> c = l[('+1',)]

    >>> c
    <Concept {1sg, 1pl} <-> [+1 -2 -3] <=> +1>


    >>> c.index, c.dindex
    (7, 6)

    >>> c.extent
    ('1sg', '1pl')

    >>> c.intent
    ('+1', '-2', '-3')

    >>> c.objects
    ()

    >>> c.properties
    ('+1',)


    >>> c.atoms  # doctest: +NORMALIZE_WHITESPACE
    (<Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
     <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>)

    >>> c.minimal()
    ('+1',)

    >>> list(c.attributes())
    [('+1',), ('+1', '-2'), ('+1', '-3'), ('-2', '-3'), ('+1', '-2', '-3')]


    >>> c.upper_neighbors  # doctest: +NORMALIZE_WHITESPACE
    (<Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>,
     <Concept {1sg, 1pl, 3sg, 3pl} <-> [-2] <=> -2>)

    >>> c.lower_neighbors  # doctest: +NORMALIZE_WHITESPACE
    (<Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
     <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>)

    >>> list(c.upset())  # doctest: +NORMALIZE_WHITESPACE
    [<Concept {1sg, 1pl} <-> [+1 -2 -3] <=> +1>,
     <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>,
     <Concept {1sg, 1pl, 3sg, 3pl} <-> [-2] <=> -2>,
     <Supremum {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []>]

    >>> list(c.downset())  # doctest: +NORMALIZE_WHITESPACE
    [<Concept {1sg, 1pl} <-> [+1 -2 -3] <=> +1>,
     <Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
     <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>,
     <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>]


    >>> l[('+1',)] <= l[('-3',)] <= l[('-3',)] <= l[()]
    True

    >>> l[('+1',)] <= l[('+sg',)] or l[('+sg',)] <= l[('+1',)]
    False

    >>> l[('+1',)] >= l[('+1', '+sg')] >= l[('+1', '+sg')] >= l[('+1', '-1')]
    True

    >>> l[('+1',)] >= l[('+sg',)] or l[('+sg',)] >= l[('+1',)]
    False

    >>> l[('+1',)] < l[('-3',)] < l[()]
    True

    >>> l[('+1',)] > l[('+1', '+sg')] > l[('+1', '-1')]
    True


    >>> l[('+1',)] | l[('+2',)]
    <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>

    >>> l[('-1', '-2')] & l[('-pl',)]
    <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>


    >>> l[('+1',)].incompatible_with(l[('+3',)])
    True

    >>> l[('+1',)].incompatible_with(l[('+sg',)])
    False

    >>> l[('+1',)].complement_of(l[('-1',)])
    True

    >>> l[('+1',)].complement_of(l[('+3',)])
    False

    >>> l[('-1',)].subcontrary_with(l[('-3',)])
    True

    >>> l[('-1',)].subcontrary_with(l[('+sg',)])
    False

    >>> l[('+1',)].orthogonal_to(l[('+sg',)])
    True

    >>> l[('+1',)].orthogonal_to(l[('+3',)])
    False
    """

    objects = ()

    properties = ()

    def __init__(self, lattice, extent, intent, upper, lower):
        self.lattice = lattice  #: The lattice containing the concept.
        self._extent = extent
        self._intent = intent
        self.upper_neighbors = upper  #: The directly implied concepts.
        self.lower_neighbors = lower  #: The directly subsumed concepts.

    def __iter__(self):
        """Yield ``extent`` and ``intent`` (e.g. for pair unpacking)."""
        yield self._extent.members()
        yield self._intent.members()

    @property
    def extent(self):
        """The objects subsumed by the concept."""
        return self._extent.members()

    @property
    def intent(self):
        """The properties implied by the concept."""
        return self._intent.members()

    def minimal(self):
        """Shortlex minimal properties generating the concept."""
        return self.lattice._context._minimal(self._extent, self._intent).members()

    def attributes(self):
        """Shortlex ordered properties generating the concept."""
        minimize = self.lattice._context._minimize(self._extent, self._intent)
        return (i.members() for i in minimize)

    def upset(self):
        """Yield implied concepts including ``self``."""
        heap = [(self.index, self)]
        push, pop = heapq.heappush, heapq.heappop
        seen = -1
        while heap:
            index, concept = pop(heap)
            if index > seen:
                seen = index
                yield concept
                for c in concept.upper_neighbors:
                    push(heap, (c.index, c))

    def downset(self):
        """Yield subsumed concepts including ``self``."""
        heap = [(self.dindex, self)]
        push, pop = heapq.heappush, heapq.heappop
        seen = -1
        while heap:
            index, concept = pop(heap)
            if index > seen:
                seen = index
                yield concept
                for c in concept.lower_neighbors:
                    push(heap, (c.dindex, c))

    def implies(self, other):
        """Implication comparison."""
        return self._extent & other._extent == self._extent

    def subsumes(self, other):
        """Subsumption comparison."""
        return self._extent | other._extent == self._extent

    __le__ = implies
    __ge__ = subsumes

    def properly_implies(self, other):
        """Proper implication comparison."""
        return self._extent & other._extent == self._extent != other._extent

    def properly_subsumes(self, other):
        """Proper subsumption comparison."""
        return self._extent | other._extent == self._extent != other._extent

    __lt__ = properly_implies
    __gt__ = properly_subsumes

    def join(self, other):
        """Least upper bound, supremum, or, generalization."""
        common = self._extent | other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice._map[extent]

    def meet(self, other):
        """Greatest lower bound, infimum, and, unification."""
        common = self._extent & other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice._map[extent]

    __or__ = join
    __and__ = meet

    def incompatible_with(self, other):
        """Infimum meet comparison."""
        return not self._extent & other._extent

    def complement_of(self, other):
        """Infimum meet and supremum join comparison."""
        return (not self._extent & other._extent and
            (self._extent | other._extent) == self.lattice.supremum._extent)

    def subcontrary_with(self, other):
        """Non-infimum meet and supremum join comparison."""
        return (self._extent & other._extent and
            (self._extent | other._extent) == self.lattice.supremum._extent)

    def orthogonal_to(self, other):
        """Non-infimum meet, incomparable, and non-supremum join comparison."""
        meet = self._extent & other._extent
        return (not not meet and meet != self._extent and meet != other._extent
            and (self._extent | other._extent) != self.lattice.supremum._extent)

    def __str__(self):
        extent = ', '.join(self._extent.members()).encode('unicode_escape')
        intent = ' '.join(self._intent.members()).encode('unicode_escape')
        objects = (' <=> %s' % ' '.join(self.objects).encode('unicode_escape')
            if self.objects else '')
        properties = (' <=> %s' % ' '.join(self.properties).encode('unicode_escape')
            if self.properties else '')
        return '{%s} <-> [%s]%s%s' % (extent, intent, objects, properties)

    def __unicode__(self):
        extent = ', '.join(self._extent.members())
        intent = ' '.join(self._intent.members())
        objects = ' <=> %s' % ' '.join(self.objects) if self.objects else ''
        properties = ' <=> %s' % ' '.join(self.properties) if self.properties else ''
        return '{%s} <-> [%s]%s%s' % (extent, intent, objects, properties)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self)


class Infimum(Concept):
    """Contradiction with empty ``extent`` and universal ``intent``."""

    def minimal(self):
        return self._intent.members()


class Atom(Concept):
    """Concept which is a minimal non-zero element in its lattice."""


class Supremum(Concept):
    """Tautology with universal ``extent`` and empty ``intent``."""
