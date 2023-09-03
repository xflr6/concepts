import typing

from . import contexts
from .lazy_lattice_members import LazyConcept
 

class LazyFormattingMixin:
    def __str__(self) -> str:
        concepts = '\n'.join(f'    {c}' for c in self._concepts)
        return f'{self!r}\n{concepts}'

    def __repr__(self) -> str:
        return (f'<{self.__class__.__name__} object'
                f' {len(self)} concepts'
                f' at {id(self):#x}>')


class LazyLattice(LazyFormattingMixin):
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

        if extent not in self._mapping:
            new_concept = LazyConcept(self, extent, intent)
            self._mapping[extent] = new_concept
            self._concepts.append(new_concept)
            self._concepts.sort(key=self._shortlex)

        return self._mapping[extent]
    
    def __iter__(self) -> typing.Iterator[LazyConcept]:
        return iter(self._concepts)

    def __len__(self) -> int:
        return len(self._concepts)


    



    

