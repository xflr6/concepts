"""Fast Concept Analysis.

cf. C. Lindig.
Fast Concept Analysis.
In Gerhard Stumme, editor,
Working with Conceptual Structures - Contributions to ICCS 2000,
Shaker Verlag, Aachen, Germany, 2000.
http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.143.948
"""

import functools
import heapq

__all__ = ['lattice', 'neighbors']


def lattice(Objects, *, infimum):
    """Yield ``(extent, indent, upper, lower)`` in short lexicographic order."""
    extent, intent = Objects.frommembers(infimum).doubleprime()

    concept = (extent, intent, [], [])

    mapping = {extent: concept}

    heap = [(extent.shortlex(), concept)]

    push = functools.partial(heapq.heappush, heap)
    pop = functools.partial(heapq.heappop, heap)

    while heap:
        _, concept = pop()

        extent, _, upper, _ = concept

        for n_extent, n_intent in neighbors(extent, Objects=Objects):
            upper.append(n_extent)

            if n_extent in mapping:
                mapping[n_extent][3].append(extent)
            else:
                mapping[n_extent] = neighbor = (n_extent, n_intent, [], [extent])
                push((n_extent.shortlex(), neighbor))

        yield concept  # concept[3] keeps growing until exhaustion


def neighbors(objects, *, Objects):
    """Yield upper neighbors from extent (in colex order?)."""
    doubleprime = Objects.doubleprime

    minimal = ~objects

    for add in Objects.atomic(minimal):
        objects_and_add = objects | add

        extent, intent = doubleprime(objects_and_add)

        if extent & ~objects_and_add & minimal:
            minimal &= ~add
        else:
            yield extent, intent
