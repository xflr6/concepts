# lattices.py - build FCA concepts lattice from context

"""Formal Concept Analysis concept lattices."""

from itertools import izip
import heapq
import collections
import functools

import bitsets

import graphviz

__all__ = ['Lattice']


class Lattice(object):
    """Formal concept lattice as directed acyclic graph of concepts.

    >>> l = Lattice('''
    ...    |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    ... 1sg| X|  |  | X|  | X|  X|   |   |  X|
    ... 1pl| X|  |  | X|  | X|   |  X|  X|   |
    ... 2sg|  | X| X|  |  | X|  X|   |   |  X|
    ... 2pl|  | X| X|  |  | X|   |  X|  X|   |
    ... 3sg|  | X|  | X| X|  |  X|   |   |  X|
    ... 3pl|  | X|  | X| X|  |   |  X|  X|   |
    ... ''')

    >>> l.infimum
    <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>

    >>> l.supremum
    <Supremum {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []>

    >>> l.atoms[0]
    <Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>
    """

    def __init__(self, context, infimum=()):
        if isinstance(context, basestring):  # mainly for doctests
            from contexts import Context
            context = Context.from_string(context)
            context.__dict__['lattice'] = self

        self._context = context

        extent, intent = context.__getitem__(infimum, raw=True)
        infimum = Infimum(self, extent, intent, intent)

        self._concepts, self._map = self._build(context, infimum)
        self._Concepts = self._link(self._concepts)
        self._annotate(context, self._concepts)

        self.infimum = self._concepts[0]
        self.supremum = self._concepts[-1]
        self.supremum.__class__ = Supremum
        for a in self.infimum.upper_neighbors:
            a.__class__ = Atom

    def _build(self, context, concept):
        """Return the list of concept in short lexicographic order
        (cf. C. Lindig. 2000. Fast Concept Analysis)."""
        concepts = []
        mapping = {concept._extent: concept}
        heap = [(concept._extent.shortlex(), concept)]
        push, pop = heapq.heappush, heapq.heappop
        get_neighbors = context._neighbors
        get_minimal = context._minimal
        index = 0
        while heap:
            concept = pop(heap)[1]
            concepts.append(concept)
            concept.index = index
            index += 1
            for extent, intent in get_neighbors(concept._extent):
                if extent in mapping:
                    neighbor = mapping[extent]
                else:
                    minimal = get_minimal(extent, intent)
                    neighbor = Concept(self, extent, intent, minimal)
                    mapping[extent] = neighbor
                    push(heap, (extent.shortlex(), neighbor))
                concept._upper_neighbors.append(neighbor)
                neighbor._lower_neighbors.append(concept)
        return concepts, mapping

    @staticmethod
    def _link(concepts):
        """Connect each concept with its neighbors and indirect neighbors."""
        Concepts = bitsets.bitset('Concepts', tuple(concepts),
            base=bitsets.bases.MemberBits)
        BitSet = Concepts.from_members

        for i, c in enumerate(concepts):
            c._upper_neighbors = BitSet(c._upper_neighbors)
            c._lower_neighbors = BitSet(c._lower_neighbors)
            e = c._extent
            c._upset = BitSet(u for u in concepts[i:] if e & u._extent == e)

        downward = sorted(concepts, key=lambda c: c._extent.longlex())
        for i, c in enumerate(downward):
            e = c._extent
            c._downset = BitSet(d for d in downward[i:] if e | d._extent == e)

        return Concepts

    @staticmethod
    def _annotate(context, concepts):
        """Annotate object/attribute concepts with their objects/properties."""
        labels = collections.defaultdict(lambda: ([], []))

        Extent = context._Extent.from_members
        for o in context.objects:
            labels[Extent([o]).double()][0].append(o)

        Intent = context._Intent.from_members
        for p in context.properties:
            labels[Intent([p]).prime()][1].append(p)

        for c in concepts:
            if c._extent in labels:
                c.objects, c.properties = (tuple(l) for l in labels.pop(c._extent))
            else:
                c.objects = c.properties = ()

    def __getstate__(self):
        concepts = [(c._extent, c._intent, c._minimal,
            c._upper_neighbors.real, c._lower_neighbors.real,
            c._upset.real, c._downset.real) for c in self._concepts]
        return self._context, concepts

    def __setstate__(self, state):
        self._context, state = state
        self._concepts = [Concept(self, *s[:3]) for s in state]
        self._Concepts = bitsets.bitset('Concepts', tuple(self._concepts),
            base=bitsets.bases.MemberBits)
        BitSet = self._Concepts.from_int
        self._map = mapping = {}
        for c, s in izip(self._concepts, state):
            (c._upper_neighbors, c._lower_neighbors,
             c._upset, c._downset) = (BitSet(x) for x in s[3:])
            mapping[c._extent] = c

        self._annotate(self._context, self._concepts)

        self.infimum = self._concepts[0]
        self.infimum.__class__ = Infimum
        self.supremum = self._concepts[-1]
        self.supremum.__class__ = Supremum
        for a in self.infimum.upper_neighbors:
            a.__class__ = Atom

    def __getitem__(self, key):
        """Return concept by index, intension, or extension.

        >>> l['1sg 1pl 2pl']
        <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>

        >>> l['-1 -sg']
        <Concept {2pl, 3pl} <-> [-1 +pl -sg]>
        """
        if isinstance(key, (int, slice)):
            return self._concepts[key]
        if not key:
            return self.supremum
        extent, intent = self._context.__getitem__(key, raw=True)
        return self._map[extent]

    def __call__(self, properties):
        """Return concept having all given properties as intension.

        >>> l('+1 -sg')
        <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>
        """
        extent = self._context._Intent.from_members(properties).prime()
        return self._map[extent]

    def __iter__(self):
        return iter(self._concepts)

    def __len__(self):
        return len(self._concepts)

    def __repr__(self):
        return '<%s object of %d atoms %d concepts %d coatoms at %X>' % (
            self.__class__.__name__, len(self.infimum.upper_neighbors),
            len(self._concepts), len(self.supremum.lower_neighbors), id(self))

    def __str__(self):
        return '%r\n%s' % (self, '\n'.join('    %s' % c for c in self._concepts))

    @property
    def atoms(self):
        return self.infimum.upper_neighbors

    def join(self, concepts):
        """Return the nearest concept that subsumes all given concepts.

        >>> l.join([l['1sg'], l['1pl'], l['2sg']])
        <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>
        """
        common = functools.reduce(long.__or__, (c._extent for c in concepts))
        extent = self._context._extents.double(common)
        return self._map[extent]

    def meet(self, concepts):
        """Return the nearest concept that implies all given concepts.

        >>> l.meet([l['-1'], l['-2'], l['-pl']])
        <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>
        """
        common = functools.reduce(long.__and__, (c._extent for c in concepts))
        extent = self._context._extents.double(common)
        return self._map[extent]        

    def graphviz(self, save=False, compile=False, view=False):
        """Return graphviz source for visualizing the lattice graph."""
        dot = graphviz.Digraph(comment=self, key=self.__class__.__name__,
            node_attr=dict(shape='circle', width='.15', style='filled'),
            edge_attr=dict(dir='none', labeldistance='1.5'))
        for concept in self._concepts[::-1]:
            key = ' '.join(concept.minimal)
            dot.node(key, '')
            attributes = {}
            if concept.objects:
                attributes.update(
                    headlabel='"%s"' % ' '.join(concept.objects),
                    labelangle='270',
                    color='transparent')
            if concept.properties:
                attributes.update(
                    taillabel='"%s"' % ' '.join(concept.properties),
                    labelangle='90',
                    color='transparent')
            if attributes:
                dot.edge(key, key, _attributes=attributes)
            dot.edges((key, ' '.join(c.minimal))
                for c in concept.lower_neighbors)
        if save or compile or view:
            dot.save(compile=compile, view=view)
        return dot


class Concept(object):
    """Formal concept as pair of extent and intent."""

    def __init__(self, lattice, extent, intent, minimal):
        self.lattice = lattice
        self._extent = extent
        self._intent = intent
        self._minimal = minimal
        # these lists get replaced by bitsets in Lattice._link
        self._upper_neighbors = []
        self._lower_neighbors = []

    def __iter__(self):
        yield self._extent.members()
        yield self._intent.members()

    @property
    def extent(self):
        return self._extent.members()

    @property
    def intent(self):
        return self._intent.members()

    @property
    def minimal(self):
        return self._minimal.members()

    @property
    def upper_neighbors(self):
        return self._upper_neighbors.members()

    @property
    def lower_neighbors(self):
        return self._lower_neighbors.members()

    @property
    def upset(self):
        return self._upset.members()

    @property
    def downset(self):
        return self._downset.members()

    @property
    def atoms(self):
        atoms = self._downset & self.lattice.infimum._upper_neighbors
        return self.lattice._Concepts.from_int(atoms).members()

    @property
    def attributes(self):
        minimize = self.lattice._context._minimize(self._extent, self._intent)
        return [i.members() for i in minimize]

    def implies(self, other):
        return self._extent & other._extent == self._extent

    def subsumes(self, other):
        return self._extent | other._extent == self._extent

    def properly_implies(self, other):
        return self._extent & other._extent == self._extent != other._extent

    def properly_subsumes(self, other):
        return self._extent | other._extent == self._extent != other._extent

    __le__ = implies
    __ge__ = subsumes
    __lt__ = properly_implies
    __gt__ = properly_subsumes

    def join(self, other):
        """Least upper bound, supremum, or, intersection.

        >>> l['+1'] | l['+2']
        <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>
        """
        common = self._extent | other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice._map[extent]

    def meet(self, other):
        """Greatest lower bound, infimum, and, unification.

        >>> l['-1 -2'] & l['-pl']
        <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>
        """
        common = self._extent & other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice._map[extent]

    __or__ = join
    __and__ = meet

    def incompatible_with(self, other):
        return not self._extent & other._extent

    def complement_of(self, other):
        return (not self._extent & other._extent and
            (self._extent | other._extent) == self.lattice.supremum._extent)

    def subcontrary_with(self, other):
        return (self._extent & other._extent and
            (self._extent | other._extent) == self.lattice.supremum._extent)

    def __str__(self):
        extent = ', '.join(self._extent.members())
        intent = ' '.join(self._intent.members())
        objects = ' <=> %s' % ' '.join(self.objects) if self.objects else ''
        properties = ' <=> %s' % ' '.join(self.properties) if self.properties else ''
        return '{%s} <-> [%s]%s%s' % (extent, intent, objects, properties)

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self)

    def __reduce__(self):
        return self.lattice, (self.intent,)


class Infimum(Concept):
    """Contradiction with empty extent and universal intent."""


class Atom(Concept):
    """Concept which is a minimal non-zero element in its lattice."""


class Supremum(Concept):
    """Tautology with universal extent and empty intent."""


def _test(verbose=False):
    l = Lattice('''
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

def _test_misc():
    global l
    l = Lattice('''
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
    assert len(l.supremum.lower_neighbors) == 6
    print l

if __name__ == '__main__':
    _test()
    _test_misc()
