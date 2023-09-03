import typing

from .._common import Concept, ConceptList

from .common import iterunion
from .fcbo import fast_generate_from, fcbo_dual
from .lindig import lattice, neighbors
from .covering_edges import lattice_fcbo

__all__ = ['iterunion',
           'fast_generate_from', 'fcbo_dual',
           'lattice', 'neighbors', 'lattice_fcbo',
           'iterconcepts', 'get_concepts']


def iterconcepts(context) -> typing.Iterator[Concept]:
    iterconcepts = fast_generate_from(context)
    return map(Concept._make, iterconcepts)


def get_concepts(context) -> typing.List[Concept]:
    iterconcepts = fast_generate_from(context)
    return ConceptList.frompairs(iterconcepts)
