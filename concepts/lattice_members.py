"""Formal Concept Analysis concepts."""

import operator
import typing

__all__ = ['Concept',
           'Infimum', 'Atom', 'Supremum']

from . import algorithms


class Concept:
    """Formal concept as pair of extent and intent.

    Usage:

    >>> import concepts
    >>> l = concepts.Context.fromstring(concepts.EXAMPLE).lattice

    >>> c = l['+1',]

    >>> c.index, c.dindex
    (7, 6)

    >>> c.objects
    ()

    >>> c.properties
    ('+1',)


    >>> c.atoms  # doctest: +NORMALIZE_WHITESPACE
    (<Atom {1sg} <-> [+1 -2 -3 +sg -pl] <=> 1sg>,
     <Atom {1pl} <-> [+1 -2 -3 +pl -sg] <=> 1pl>)

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


    >>> l['+1',] <= l['-3',] <= l['-3',] <= l[()]
    True

    >>> l['+1',] <= l['+sg',] or l['+sg',] <= l['+1',]
    False

    >>> l['+1',] >= l['+1', '+sg'] >= l['+1', '+sg'] >= l['+1', '-1']
    True

    >>> l['+1',] >= l['+sg',] or l['+sg',] >= l['+1',]
    False

    >>> l['+1',] < l['-3',] < l[()]
    True

    >>> l['+1',] > l['+1', '+sg'] > l['+1', '-1']
    True


    >>> l['+1',] | l['+2',]
    <Concept {1sg, 1pl, 2sg, 2pl} <-> [-3] <=> -3>

    >>> l['-1', '-2'] & l['-pl',]
    <Atom {3sg} <-> [-1 -2 +3 +sg -pl] <=> 3sg>


    >>> l['+1',].incompatible_with(l['+3',])
    True

    >>> l['+1',].incompatible_with(l['+sg',])
    False

    >>> l['+1',].complement_of(l['-1',])
    True

    >>> l['+1',].complement_of(l['+3',])
    False

    >>> l['-1',].subcontrary_with(l['-3',])
    True

    >>> l['-1',].subcontrary_with(l['+sg',])
    False

    >>> l['+1',].orthogonal_to(l['+sg',])
    True

    >>> l['+1',].orthogonal_to(l['+3',])
    False
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

    def __str__(self):
        extent = ', '.join(self._extent.members())
        intent = ' '.join(self._intent.members())
        objects = ' <=> {}'.format(' '.join(self.objects)) if self.objects else ''
        properties = ' <=> {}'.format(' '.join(self.properties)) if self.properties else ''
        return f'{{{extent}}} <-> [{intent}]{objects}{properties}'

    def __repr__(self):
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
        """
        return algorithms.iterunion([self], _sortkey, _next_concepts)

    def downset(self,
                _sortkey=operator.attrgetter('dindex'),
                _next_concepts=operator.attrgetter('lower_neighbors')):
        """Yield subsumed concepts including ``self``.

        Yields:
            :class:`.Concept` instances.
        """
        return algorithms.iterunion([self], _sortkey, _next_concepts)

    def implies(self, other):
        """Implication comparison.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` implies ``other`` else ``False``.
        """
        return self._extent & other._extent == self._extent

    def subsumes(self, other):
        """Subsumption comparison.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` subsumes ``other`` else ``False``.
        """
        return self._extent | other._extent == self._extent

    __le__ = implies
    __ge__ = subsumes

    def properly_implies(self, other):
        """Proper implication comparison.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` properly implies ``other`` else ``False``.
        """
        return self._extent & other._extent == self._extent != other._extent

    def properly_subsumes(self, other):
        """Proper subsumption comparison.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` properly subsumes ``other`` else ``False``.
        """
        return self._extent | other._extent == self._extent != other._extent

    __lt__ = properly_implies
    __gt__ = properly_subsumes

    def join(self, other):
        """Least upper bound, supremum, or, generalization.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            Concept: :class:`.Concept` instance from the same lattice.
        """
        common = self._extent | other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice._mapping[extent]

    def meet(self, other):
        """Greatest lower bound, infimum, and, unification.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            Concept: :class:`.Concept` instance from the same lattice.
        """
        common = self._extent & other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice._mapping[extent]

    __or__ = join
    __and__ = meet

    def incompatible_with(self, other):
        """Infimum meet comparison.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` is incompatible with ``other`` else ``False``.
        """
        return not self._extent & other._extent

    def complement_of(self, other):
        """Infimum meet and supremum join comparison.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` is the complement of ``other`` else ``False``.
        """
        return (not self._extent & other._extent
                and (self._extent | other._extent) == self.lattice.supremum._extent)

    def subcontrary_with(self, other):
        """Non-infimum meet and supremum join comparison.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` is the subcontrary to ``other`` else ``False``.
        """
        return (self._extent & other._extent
                and (self._extent | other._extent) == self.lattice.supremum._extent)

    def orthogonal_to(self, other):
        """Non-infimum meet, incomparable, and non-supremum join comparison.

        Args:
            other (Concept): :class:`.Concept` instance from the same lattice.

        Returns:
            bool: ``True`` if ``self`` is orthogonal to ``other`` else ``False``.
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
