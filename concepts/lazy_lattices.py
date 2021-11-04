import typing

from . import lattices
from . import contexts
from .algorithms import lindig

from .lattice_members import OrderableMixin


class LazyPair:    
    def __init__(self,
                 lattice,
                 extent,
                 intent,
                 upper=None,
                 lower=None) -> None:
        self.lattice = lattice
        self._extent = extent
        self._intent = intent
        self._upper_neighbors = upper
        self._lower_neighbors = lower
    
    @property
    def upper_neighbors(self):
        if self._upper_neighbors is None:
            neighbors = lindig.neighbors(self._extent, Objects=self.lattice._context._Objects)
            
            shortlex = self.lattice._shortlex

            upper = (self.lattice[extent.members()] for extent, _ in neighbors)
            self._upper_neighbors = tuple(sorted(upper, key=shortlex))

        return self._upper_neighbors
    
    @property
    def lower_neighbors(self):
        if self._lower_neighbors is None:
            neighbors = lindig.neighbors(self._intent, Objects=self.lattice._context._Properties)
            
            longlex = self.lattice._longlex

            lower = (self.lattice[extent.members()] for _, extent in neighbors)
            self._lower_neighbors = tuple(sorted(lower, key=longlex))

        return self._lower_neighbors
    
    def _eq(self, other):
        if not isinstance(other, LazyConcept):
            return NotImplemented

        if (other._extent.members() != self._extent.members()
            or other._intent.members() != self._intent.members()):
            return False

        return True


class LazyRelationsMixin:
    def incompatible_with(self, other: 'LazyConcept') -> bool:
        return not self._extent & other._extent
    

class LazyTransformableMixin:
    def join(self, other: 'LazyConcept') -> 'LazyConcept':
        common = self._extent | other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice[extent.members()]

    __or__ = join

    def meet(self, other: 'LazyConcept') -> 'LazyConcept':
        common = self._extent & other._extent
        extent = self.lattice._context._extents.double(common)
        return self.lattice[extent.members()]

    __and__ = meet


class LazyFormattingMixin:
    def __str__(self) -> str:
        extent = ', '.join(self._extent.members())
        intent = ' '.join(self._intent.members())
        return f'{{{extent}}} <-> [{intent}]'

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} {self}>'


class LazyConcept(LazyRelationsMixin, OrderableMixin, LazyFormattingMixin, LazyPair):
    def minimal(self) -> typing.Tuple[str, ...]:
        return self.lattice._context._minimal(self._extent,
                                              self._intent).members()

    def attributes(self) -> typing.Iterator[typing.Tuple[str]]:
        minimize = self.lattice._context._minimize(self._extent, self._intent)
        return (i.members() for i in minimize)
 

class LazyLattice(lattices.CollectionMixin, lattices.FormattingMixin):
    @staticmethod
    def _longlex(concept):
        return concept._extent.longlex()

    @staticmethod
    def _shortlex(concept):
        return concept._extent.shortlex()

    def __init__(self, context: 'contexts.Context'):
        self._context = context
        self._concepts = []
        self._mapping = {}

    def __repr__(self) -> str:
        return (f'<{self.__class__.__name__} object'
                f' {len(self)} concepts'
                f' at {id(self):#x}>')
    
    def __getitem__(self, key: typing.Tuple[str, ...]) -> LazyConcept:
        if not key:
            key = self._context._Objects.supremum.members()

        extent, intent = self._context.__getitem__(key, raw=True)

        if extent not in self:
            new_concept = LazyConcept(self, extent, intent)
            self._mapping[extent] = new_concept
            self._concepts.append(new_concept)

        return self._mapping[extent]


    

