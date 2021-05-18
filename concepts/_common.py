import typing

from . import formats
from . import matrices

__all__ = ['Shape',
           'Concept',
           'ConceptList']


class Shape(typing.NamedTuple):
    """Tuple of ``len(objects)`` and  ``len(properties))``.

    Example:
        >>> import concepts
        >>> c = concepts.Context.fromstring(concepts.EXAMPLE)
        >>> c.shape
        Shape(objects=6, properties=10)
        >>> n_objects, n_properties = c.shape
        >>> n_objects, n_properties
        (6, 10)
    """

    objects: int

    properties: int


    @classmethod
    def _from_pair(cls, objects, properties):
        return cls(len(objects), len(properties))

    def __repr__(self):
        return (f'{self.__class__.__name__}'
                f'(objects={self.objects:_d},'
                f' properties={self.properties:_d})')

    @property
    def rows(self) -> int:
        """The number of (object) rows.

        Example:
        >>> import concepts
        >>> c = concepts.Context.fromstring(concepts.EXAMPLE)
        >>> c.shape.rows
        6
        """
        return self.objects

    @property
    def columns(self) -> int:
        """The number of (property) columns.

        Example:
        >>> import concepts
        >>> c = concepts.Context.fromstring(concepts.EXAMPLE)
        >>> c.shape.columns
        10
        """
        return self.properties


class Concept(typing.NamedTuple):
    """Pair of raw extent and raw intent.

    >>> import concepts
    >>> context = concepts.make_context(concepts.EXAMPLE)

    >>> node = context.lattice[12]
    >>> node
    <Concept {2sg, 2pl} <-> [-1 +2 -3] <=> +2>

    >>> c = Concept(node._extent, node._intent)
    >>> c
    Concept(extent=Objects('001100'), intent=Properties('0110010000'))

    >>> print(c)
    001100 <-> 0110010000

    >>> c.objects
    ('2sg', '2pl')

    >>> c.properties
    ('-1', '+2', '-3')

    >>> c.n_objects, c.n_properties
    (2, 3)

    >>> c.index_sets()
    ((2, 3), (1, 2, 5))

    >>> c.index_sets(as_set=True)
    (frozenset({2, 3}), frozenset({1, 2, 5}))
    """
    extent: matrices.Vector

    intent: matrices.Vector

    @property
    def objects(self) -> typing.Tuple[str]:
        """The objects subsumed by the concept."""
        return self.extent.members()

    @property
    def properties(self) -> typing.Tuple[str]:
        """The properties implied by the concept."""
        return self.intent.members()

    @property
    def n_objects(self) -> int:
        return self.extent.count()

    @property
    def n_properties(self) -> int:
        return self.intent.count()

    def __str__(self) -> str:
        return f'{self.extent.bits()} <-> {self.intent.bits()}'

    def index_sets(self, *, as_set: bool = False):
        return self.extent_index_set(as_set=as_set), self.intent_index_set(as_set=as_set)

    def extent_index_set(self, *, as_set: bool = False):
        cls = frozenset if as_set else tuple
        return cls(self.extent.iter_set())

    def intent_index_set(self, *, as_set: bool = False):
        cls = frozenset if as_set else tuple
        return cls(self.intent.iter_set())


class ConceptList(list):
    """List of (raw extent, raw intent) pairs."""

    @classmethod
    def frompairs(cls, iterconcepts) -> 'ConceptList':
        return cls(map(Concept._make, iterconcepts))

    def tofile(self, filename,
               *, frmat: str = 'fimi',
               **kwargs) -> None:
        if frmat != 'fimi':  # pragma: no cover
            raise NotImplementedError(f'tofile(frmat={frmat!r})')
        formats.write_concepts_dat(filename, self, **kwargs)
