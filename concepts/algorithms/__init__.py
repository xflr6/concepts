from collections.abc import Iterator

from .._common import Concept, ConceptList

from .common import iterunion
from .fcbo import fast_generate_from, fcbo_dual
from .lindig import lattice, neighbors

__all__ = ['iterunion',
           'fast_generate_from', 'fcbo_dual',
           'lattice', 'neighbors'
           'iterconcepts', 'get_concepts']


def iterconcepts(context) -> Iterator[Concept]:
    iterconcepts = fast_generate_from(context)
    return map(Concept._make, iterconcepts)


def get_concepts(context) -> list[Concept]:
    iterconcepts = fast_generate_from(context)
    return ConceptList.frompairs(iterconcepts)
