"""Formal Concept Analysis concept lattices from contexts."""

import heapq
import operator
import typing

from . import algorithms
from . import contexts
from .lattice_members import Concept, Infimum, Atom, Supremum
from . import tools
from . import visualize

__all__ = ['Lattice']


class Data:
    """Formal concept lattice as context, list of concepts, and mapping."""

    @staticmethod
    def _longlex(concept):
        return concept._extent.longlex()

    @staticmethod
    def _shortlex(concept):
        return concept._extent.shortlex()

    @classmethod
    def _fromlist(cls, context, lattice, unordered) -> 'Lattice':
        make_objects = context._Objects.fromint
        make_properties = context._Properties.fromint
        inst = object.__new__(cls)
        concepts = [Concept(inst,
                            make_objects(sum(1 << e for e in ex)),
                            make_properties(sum(1 << i for i in in_)),
                            up, lo)
                    for ex, in_, up, lo in lattice]

        if unordered:
            index_map = dict(enumerate(concepts))
            shortlex = inst._shortlex
            longlex = inst._longlex
            concepts.sort(key=shortlex)
            for index, c in enumerate(concepts):
                c.index = index
                upper = (index_map[i] for i in c.upper_neighbors)
                lower = (index_map[i] for i in c.lower_neighbors)
                c.upper_neighbors = tuple(sorted(upper, key=shortlex))
                c.lower_neighbors = tuple(sorted(lower, key=longlex))
        else:
            # assume sorted(concepts, key=shortlex)
            # assume sorted(upper_neighbors, key=shortlex)
            # assume sorted(lower_neighbors, key=longlex)
            for index, c in enumerate(concepts):
                c.index = index
                c.upper_neighbors = tuple(concepts[i] for i in c.upper_neighbors)
                c.lower_neighbors = tuple(concepts[i] for i in c.lower_neighbors)

        cls._init(inst, context, concepts)
        return inst

    def __init__(self, context: 'contexts.Context', infimum=()) -> None:
        """Create lattice from context."""
        concepts = [Concept(self, *args)
                    for args in context._lattice(infimum)]
        mapping = self._make_mapping(concepts)

        shortlex = self._shortlex
        longlex = self._longlex
        for index, c in enumerate(concepts):
            c.index = index
            upper = (mapping[u] for u in c.upper_neighbors)
            lower = (mapping[l] for l in c.lower_neighbors)
            c.upper_neighbors = tuple(sorted(upper, key=shortlex))
            c.lower_neighbors = tuple(sorted(lower, key=longlex))

        self._init(self, context, concepts, mapping=mapping)

    @staticmethod
    def _make_mapping(concepts):
        return {c._extent: c for c in concepts}

    @staticmethod
    def _init(inst,
              context: 'contexts.Context',
              concepts,
              mapping=None, unpickle=False) -> None:
        inst._context = context
        inst._concepts = concepts

        if mapping is None:
            mapping = inst._make_mapping(inst._concepts)
        inst._mapping = mapping

        if unpickle:
            return

        # downward
        atoms = inst.atoms
        for dindex, c in enumerate(sorted(inst._concepts, key=inst._longlex)):
            c.dindex = dindex
            e = c._extent
            c.atoms = tuple(a for a in atoms if e | a._extent == e)

        inst._annotate(inst._context, inst._mapping)

        for a in inst.atoms:
            a.__class__ = Atom
        inst.supremum.__class__ = Supremum
        inst.infimum.__class__ = Infimum

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
        context, concepts = state
        self._init(self, context, concepts, unpickle=True)

    def _tolist(self):
        return [(tuple(c._extent.iter_set()),
                 tuple(c._intent.iter_set()),
                 tuple(u.index for u in c.upper_neighbors),
                 tuple(l.index for l in c.lower_neighbors))
                for c in self._concepts]

    def _eq(self, other) -> typing.Union[type(NotImplemented), bool]:
        """Return ``True`` if two lattices are equivalent.

        Note:
            Does not compares their context objects.
            Lattice-equivalence comparison is present mainly for unit-tests
            (not meant to be efficient). Context-comparison should be superior
            in most cases.
        """
        if not isinstance(other, Lattice):
            return NotImplemented

        if (len(other._concepts) != len(self._concepts)
            or not all(s._eq(o) for s, o in zip(self._concepts, other._concepts))):
            return False

        if (len(other._mapping) != len(self._mapping)
            or {e.members() for e in other._mapping}
            != {e.members() for e in self._mapping}):
            return False

        for s, o in zip(self._concepts, other._concepts):
            if (o.index != s.index or o.dindex != s.dindex
                or [a._extent.members() for a in o.atoms]
                != [a._extent.members() for a in s.atoms]
                or o.objects != s.objects or o.properties != s.properties):
                return False

        return True


class FormattingMixin:
    """Lattice formatting methods."""

    def __str__(self) -> str:
        """Return the full string representation of the lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> print(lattice)  # doctest: +ELLIPSIS
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
        """
        concepts = '\n'.join(f'    {c}' for c in self._concepts)
        return f'{self!r}\n{concepts}'

    def __repr__(self) -> str:
        """Return the debug string representation of the lattice.

        Example:
            >>> lattice = contexts.Context.fromstring('''
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
            >>> lattice  # doctest: +ELLIPSIS
            <Lattice object of 11 atoms 65 concepts 6 coatoms at 0x...>
        """
        return (f'<{self.__class__.__name__} object'
                f' of {len(self.atoms)} atoms'
                f' {len(self)} concepts'
                f' {len(self.supremum.lower_neighbors)} coatoms'
                f' at {id(self):#x}>')


class CollectionMixin:
    """Formal concept lattice as collection of concepts."""

    def __call__(self, properties: typing.Tuple[str]) -> Concept:
        """Return concept having all given ``properties`` as intension.

        Args:
            properties: Tuple of property names.

        Returns:
            :class:`.Concept` instance from this lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice(['+1', '-sg'])
            <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>
        """
        extent = self._context.extension(properties, raw=True)
        return self._mapping[extent]

    def __getitem__(self, key: typing.Union[int, typing.Tuple[str, ...]]
                    ) -> Concept:
        """Return concept by index, intension, or extension.

        Args:
            key: Integer index, properties tuple, or objects tuple.

        Returns:
            :class:`.Concept` instance from this lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice[1:3]  # doctest: +NORMALIZE_WHITESPACE
            [<Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
             <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>]
            >>> lattice['-1', '-sg']
            <Concept {2pl, 3pl} <-> [-1 +pl -sg]>
            >>> lattice['1sg', '1pl', '2pl']
            <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>
        """
        if isinstance(key, (int, slice)):
            return self._concepts[key]

        if not key:
            return self.supremum

        extent, intent = self._context.__getitem__(key, raw=True)
        return self._mapping[extent]

    def __iter__(self) -> typing.Iterator[Concept]:
        """Yield all concepts of the lattice.

        Yields:
            All :class:`.Concept` instances from this lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> iterconcepts = iter(lattice)
            >>> next(iterconcepts)
            <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>
            >>> next(iterconcepts)
            <Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>
        """
        return iter(self._concepts)

    def __len__(self) -> int:
        """Return the number of concepts in the lattice.

        Returns:
            Number of lattice concepts.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> len(lattice)
            22
        """
        return len(self._concepts)


class AggregagtionMixin:
    """Lattice generalized (n-ary) join and meet operations."""

    def join(self, concepts: typing.Iterable[Concept]) -> Concept:
        """Return the nearest concept that subsumes all given concepts.

        Args:
            concepts: :class:`.Concept` instances from this lattice.

        Returns:
            :class:`.Concept` instance from this lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice.join([])
            <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>
            >>> lattice.join([lattice['1sg',], lattice['1pl',], lattice['2sg',]])
            <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>
        """
        extents = (c._extent for c in concepts)
        join = self._context._Objects.reduce_or(extents)
        return self._mapping[join.double()]

    def meet(self, concepts: typing.Iterable[Concept]) -> Concept:
        """Return the nearest concept that implies all given concepts.

        Args:
            concepts: :class:`.Concept` instances from this lattice.

        Returns:
            :class:`.Concept` instance from this lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice.meet([])
            <Supremum {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []>
            >>> lattice.meet([lattice['-1',], lattice['-2',], lattice['-pl',]])
            <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>
        """
        extents = (c._extent for c in concepts)
        meet = self._context._Objects.reduce_and(extents)
        return self._mapping[meet.double()]


class NavigateableMixin:
    """Iterators over concept neighbor unions."""

    def upset_union(self, concepts: typing.Iterable[Concept],
                    _sortkey=operator.attrgetter('index'),
                    _next_concepts=operator.attrgetter('upper_neighbors')
                    ) -> typing.Iterator[Concept]:
        """Yield all concepts that subsume any of the given ones.

        Args:
            concepts: :class:`.Concept` instances from this lattice.

        Yields:
            :class:`.Concept` instances from this lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> list(lattice.upset_union([lattice['+1',], lattice['+2',]]))  # doctest: +NORMALIZE_WHITESPACE
            [<Concept {1sg, 1pl} <-> [+1 -2 -3] <=> +1>,
             <Concept {2sg, 2pl} <-> [-1 +2 -3] <=> +2>,
             <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>,
             <Concept {1sg, 1pl, 3sg, 3pl} <-> [-2] <=> -2>,
             <Concept {2sg, 2pl, 3sg, 3pl} <-> [-1] <=> -1>,
             <Supremum {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []>]
        """
        concepts = tools.maximal(concepts, comparison=Concept.properly_subsumes)
        return algorithms.iterunion(concepts, _sortkey, _next_concepts)

    def downset_union(self, concepts: typing.Iterable[Concept],
                    _sortkey=operator.attrgetter('dindex'),
                    _next_concepts=operator.attrgetter('lower_neighbors')
                      ) -> typing.Iterator[Concept]:
        """Yield all concepts that imply any of the given ones.

        Args:
            concepts: :class:`.Concept` instances from this lattice.

        Yields:
            :class:`.Concept` instances from this lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> list(lattice.downset_union([lattice['+1',], lattice['+2',]]))  # doctest: +NORMALIZE_WHITESPACE
            [<Concept {1sg, 1pl} <-> [+1 -2 -3] <=> +1>,
             <Concept {2sg, 2pl} <-> [-1 +2 -3] <=> +2>,
             <Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
             <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>,
             <Atom {2sg} <-> [-1 +2 -3 +sg -pl] <=> 2sg>,
             <Atom {2pl} <-> [-1 +2 -3 +pl -sg] <=> 2pl>,
             <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>]
        """
        concepts = tools.maximal(concepts, comparison=Concept.properly_implies)
        return algorithms.iterunion(concepts, _sortkey, _next_concepts)

    def upset_generalization(self, concepts: typing.Iterable[Concept]
                             ) -> typing.Iterator[Concept]:
        """Yield all concepts that subsume only the given ones.

        Args:
            concepts: :class:`.Concept` instances from this lattice.

        Yields:
            :class:`.Concept` instances from this lattice.

        Note:
            This method is EXPERIMENTAL and might change without notice.
        """
        heap = [(c.index, c)
                for c in tools.maximal(concepts,
                                       comparison=Concept.properly_subsumes)]
        heapq.heapify(heap)
        push, pop = heapq.heappush, heapq.heappop
        extents = (c._extent for i, c in heap)
        target = self._context._Objects.reduce_or(extents)
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


class VisualizableMixin:
    """Visualization methods."""

    def graphviz(self, filename=None, directory=None,
                 render: bool = False,
                 view: bool = False,
                 make_object_label=' '.join,
                 make_property_label=' '.join,
                 **kwargs) -> 'graphviz.Digraph':
        """Return DOT source for visualizing the lattice graph.

        Args:
            filename: Path to the DOT source file for the Digraph.
            directory: (Sub)directory for DOT source saving and rendering.
            render: Call ``.render()`` on the result.
            view: Call ``.render(view=True)`` on the result.
            make_object_label: Callable with iterable of objects argument
                               returning a string to be used as object label.
            make_property_label: Callable with iterable of properties argument
                                 returning a string to be used as object label.
        Returns:
            A ``graphviz.Digraph`` instance.
        """
        return visualize.lattice(self, filename, directory, render, view,
                                 make_object_label=make_object_label,
                                 make_property_label=make_property_label,
                                 **kwargs)


class Lattice(VisualizableMixin, NavigateableMixin, AggregagtionMixin,
              CollectionMixin, FormattingMixin, Data):
    """Formal concept lattice as directed acyclic graph of concepts.

    Example:
        >>> import concepts
        >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
        >>> lattice
        <Lattice object of 6 atoms 22 concepts 5 coatoms at 0x...>
    """

    @property
    def infimum(self) -> Infimum:
        """The most specific concept of the lattice.

        Returns:
            Infimum concept of the lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice.infimum
            <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>
        """
        return self._concepts[0]

    @property
    def supremum(self) -> Supremum:
        """The most general concept of the lattice.

        Returns:
            Supremum concept of the lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice.supremum
            <Supremum {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []>
        """
        return self._concepts[-1]

    @property
    def atoms(self) -> typing.Tuple[Atom, ...]:
        """The minimal non-infimum concepts of the lattice.

        Returns:
            Atom concepts of the lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice.atoms  # doctest: +NORMALIZE_WHITESPACE
            (<Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
             <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>,
             <Atom {2sg} <-> [-1 +2 -3 +sg -pl] <=> 2sg>,
             <Atom {2pl} <-> [-1 +2 -3 +pl -sg] <=> 2pl>,
             <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>,
             <Atom {3pl} <-> [-1 -2 +3 +pl -sg] <=> 3pl>)
        """
        return self.infimum.upper_neighbors
