"""Formal Concept Analysis concepts."""

import operator
import typing

__all__ = ['Concept',
           'Infimum', 'Atom', 'Supremum']

from . import algorithms


class Concept:
    """Formal concept as pair of extent and intent.

    Example:

    >>> import concepts
    >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
    >>> concept = lattice['+1',]
    >>> concept.index, concept.dindex
    (7, 6)
    >>> concept.objects
    ()
    >>> concept.properties
    ('+1',)
    >>> concept.atoms  # doctest: +NORMALIZE_WHITESPACE
    (<Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
     <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>)
    >>> concept.upper_neighbors  # doctest: +NORMALIZE_WHITESPACE
    (<Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>,
     <Concept {1sg, 1pl, 3sg, 3pl} <-> [-2] <=> -2>)
    >>> concept.lower_neighbors  # doctest: +NORMALIZE_WHITESPACE
    (<Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
     <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>)
    """

    objects = ()

    properties = ()

    def __init__(self,
                 lattice,
                 extent,
                 intent,
                 upper,
                 lower) -> None:
        self.lattice = lattice  #: The lattice containing the concept.
        self._extent = extent
        self._intent = intent
        self.upper_neighbors = upper  #: The directly implied concepts.
        self.lower_neighbors = lower  #: The directly subsumed concepts.

    def __str__(self) -> str:
        extent = ', '.join(self._extent.members())
        intent = ' '.join(self._intent.members())
        objects = ' <=> {}'.format(' '.join(self.objects)) if self.objects else ''
        properties = ' <=> {}'.format(' '.join(self.properties)) if self.properties else ''
        return f'{{{extent}}} <-> [{intent}]{objects}{properties}'

    def __repr__(self) -> str:
        """

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',]
            <Concept {1sg, 1pl} <-> [+1 -2 -3] <=> +1>
        """
        return f'<{self.__class__.__name__} {self}>'

    def _eq(self, other):
        if not isinstance(other, Concept):
            return NotImplemented

        if (other._extent.members() != self._extent.members()
            or other._intent.members() != self._intent.members()):
            return False

        for attname in ('upper_neighbors', 'lower_neighbors'):
            s_neighbors = getattr(self, attname)
            o_neighbors = getattr(other, attname)
            if len(o_neighbors) != len(s_neighbors):
                return False
            for s, o in zip(s_neighbors, o_neighbors):
                if o._extent.members() != s._extent.members():
                    return False
        return True

    def __iter__(self):
        """Yield ``extent`` and ``intent`` (e.g. for pair unpacking)."""
        yield self._extent.members()
        yield self._intent.members()

    @property
    def extent(self) -> typing.Tuple[str, ...]:
        """The objects subsumed by the concept.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',].extent
            ('1sg', '1pl')
        """
        return self._extent.members()

    @property
    def intent(self) -> typing.Tuple[str, ...]:
        """The properties implied by the concept."

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',].intent
            ('+1', '-2', '-3')
        """
        return self._intent.members()

    def minimal(self) -> typing.Tuple[str, ...]:
        """Shortlex minimal properties generating the concept.

        Returns:
            Property name strings.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',].minimal()
            ('+1',)
        """
        return self.lattice._context._minimal(self._extent,
                                              self._intent).members()

    def attributes(self) -> typing.Iterator[typing.Tuple[str]]:
        """Yield properties generating the concept in shortlex order.

        Yields:
            Tuples of property name strings.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> list(lattice['+1',].attributes())
            [('+1',), ('+1', '-2'), ('+1', '-3'), ('-2', '-3'), ('+1', '-2', '-3')]
        """
        minimize = self.lattice._context._minimize(self._extent, self._intent)
        return (i.members() for i in minimize)

    def upset(self,
              _sortkey=operator.attrgetter('index'),
              _next_concepts=operator.attrgetter('upper_neighbors')):
        """Yield implied concepts including ``self``.

        Yields:
            :class:`.Concept` instances.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> list(lattice['+1',].upset())  # doctest: +NORMALIZE_WHITESPACE
            [<Concept {1sg, 1pl} <-> [+1 -2 -3] <=> +1>,
             <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>,
             <Concept {1sg, 1pl, 3sg, 3pl} <-> [-2] <=> -2>,
             <Supremum {1sg, 1pl, 2sg, 2pl, 3sg, 3pl} <-> []>]
        """
        return algorithms.iterunion([self], _sortkey, _next_concepts)

    def downset(self,
                _sortkey=operator.attrgetter('dindex'),
                _next_concepts=operator.attrgetter('lower_neighbors')):
        """Yield subsumed concepts including ``self``.

        Yields:
            :class:`.Concept` instances.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> list(lattice['+1',].downset())  # doctest: +NORMALIZE_WHITESPACE
            [<Concept {1sg, 1pl} <-> [+1 -2 -3] <=> +1>,
             <Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
             <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>,
             <Infimum {} <-> [+1 -1 +2 -2 +3 -3 +sg +pl -sg -pl]>]
        """
        return algorithms.iterunion([self], _sortkey, _next_concepts)

    def implies(self, other: 'Concept') -> bool:
        """Implication comparison.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` implies ``other`` else ``False``.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',] <= lattice['-3',] <= lattice['-3',] <= lattice[()]
            True
            >>> lattice['+1',] <= lattice['+sg',] or lattice['+sg',] <= lattice['+1',]
            False
        """
        return self._extent & other._extent == self._extent

    def subsumes(self, other: 'Concept') -> bool:
        """Subsumption comparison.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` subsumes ``other`` else ``False``.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',] >= lattice['+1', '+sg'] >= lattice['+1', '+sg'] >= lattice['+1', '-1']
            True
            >>> lattice['+1',] >= lattice['+sg',] or lattice['+sg',] >= lattice['+1',]
            False
        """
        return self._extent | other._extent == self._extent

    __le__ = implies

    __ge__ = subsumes

    def properly_implies(self, other: 'Concept') -> bool:
        """Proper implication comparison.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` properly implies ``other`` else ``False``.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',] < lattice['-3',] < lattice[()]
            True
        """
        return self._extent & other._extent == self._extent != other._extent

    def properly_subsumes(self, other: 'Concept') -> bool:
        """Proper subsumption comparison.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` properly subsumes ``other`` else ``False``.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',] > lattice['+1', '+sg'] > lattice['+1', '-1']
            True
        """
        return self._extent | other._extent == self._extent != other._extent

    __lt__ = properly_implies

    __gt__ = properly_subsumes

    def join(self, other: 'Concept') -> 'Concept':
        """Least upper bound, supremum, or, generalization.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            :class:`.Concept` instance from the same lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',].join(lattice['+2',])
            <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>
            >>> lattice['+2',] | lattice['+1',]
            <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>
        """
        common = self._extent | other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice._mapping[extent]

    def meet(self, other: 'Concept') -> 'Concept':
        """Greatest lower bound, infimum, and, unification.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            :class:`.Concept` instance from the same lattice.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['-1', '-2'].meet(lattice['-pl',])
            <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>
            >>> lattice['-pl',] & lattice['-1', '-2']
            <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>
        """
        common = self._extent & other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice._mapping[extent]

    __or__ = join

    __and__ = meet

    def incompatible_with(self, other: 'Concept') -> bool:
        """Infimum meet comparison.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` is incompatible with ``other`` else ``False``.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',].incompatible_with(lattice['+3',])
            True
            >>> lattice['+1',].incompatible_with(lattice['+sg',])
            False
        """
        return not self._extent & other._extent

    def complement_of(self, other: 'Concept') -> bool:
        """Infimum meet and supremum join comparison.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` is the complement of ``other`` else ``False``.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',].complement_of(lattice['-1',])
            True
            >>> lattice['+1',].complement_of(lattice['+3',])
            False
        """
        return (not self._extent & other._extent
                and (self._extent | other._extent) == self.lattice.supremum._extent)

    def subcontrary_with(self, other: 'Concept') -> bool:
        """Non-infimum meet and supremum join comparison.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` is the subcontrary to ``other`` else ``False``.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['-1',].subcontrary_with(lattice['-3',])
            True
            >>> lattice['-1',].subcontrary_with(lattice['+sg',])
            False
        """
        return (self._extent & other._extent
                and (self._extent | other._extent) == self.lattice.supremum._extent)

    def orthogonal_to(self, other: 'Concept') -> bool:
        """Non-infimum meet, incomparable, and non-supremum join comparison.

        Args:
            other: :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` is orthogonal to ``other`` else ``False``.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice['+1',].orthogonal_to(lattice['+sg',])
            True
            >>> lattice['+1',].orthogonal_to(lattice['+3',])
            False
        """
        meet = self._extent & other._extent
        return (not not meet and meet != self._extent and meet != other._extent
                and (self._extent | other._extent) != self.lattice.supremum._extent)


class Infimum(Concept):
    """Contradiction with empty ``extent`` and universal ``intent``."""

    def minimal(self) -> typing.Tuple[str, ...]:
        """Shortlex minimal properties generating the concept.

        Returns:
            Property name strings.

        Example:
            >>> import concepts
            >>> lattice = concepts.Context.fromstring(concepts.EXAMPLE).lattice
            >>> lattice.infimum.minimal()
            ('+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl')
        """
        return self._intent.members()


class Atom(Concept):
    """Concept which is a minimal non-zero element in its lattice."""


class Supremum(Concept):
    """Tautology with universal ``extent`` and empty ``intent``."""
