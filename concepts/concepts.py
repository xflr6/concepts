import typing

from . import matrices

__all__ = ['ConceptList']


class Concept(typing.NamedTuple):

    extent: matrices.Vector

    intent: matrices.Vector


class ConceptList(list):

    @classmethod
    def frompairs(cls, iterconcepts):
        return cls(map(Concept._make, iterconcepts))
