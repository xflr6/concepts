import collections
import functools
import heapq

__all__ = ['lattice', 'neighbors',
           'iterunion',
           'fcbo']


def lattice(Extent, *, infimum):
    """Yield ``(extent, indent, upper, lower)`` in short lexicographic order.

    cf. C. Lindig.
    Fast Concept Analysis.
    In Gerhard Stumme, editor,
    Working with Conceptual Structures - Contributions to ICCS 2000,
    Shaker Verlag, Aachen, Germany, 2000.
    http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.143.948
    """
    extent, intent = Extent.frommembers(infimum).doubleprime()

    concept = (extent, intent, [], [])

    mapping = {extent: concept}

    heap = [(extent.shortlex(), concept)]

    push = functools.partial(heapq.heappush, heap)
    pop = functools.partial(heapq.heappop, heap)

    while heap:
        concept = pop()[1]

        for extent, intent in neighbors(concept[0], Extent=Extent):
            if extent in mapping:
                neighbor = mapping[extent]
            else:
                neighbor = mapping[extent] = (extent, intent, [], [])
                push((extent.shortlex(), neighbor))

            concept[2].append(neighbor[0])
            neighbor[3].append(concept[0])

        yield concept  # concept[3] keeps growing until exhaustion


def neighbors(objects, *, Extent):
    """Yield upper neighbors from extent (in colex order?).

    cf. C. Lindig.
    Fast Concept Analysis.
    In Gerhard Stumme, editor,
    Working with Conceptual Structures - Contributions to ICCS 2000,
    Shaker Verlag, Aachen, Germany, 2000.
    http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.143.948
    """
    doubleprime = Extent.doubleprime

    minimal = ~objects

    for add in Extent.atomic(minimal):
        objects_and_add = objects | add

        extent, intent = doubleprime(objects_and_add)

        if extent & ~objects_and_add & minimal:
            minimal &= ~add
        else:
            yield extent, intent


def iterunion(concepts, sortkey, next_concepts):
    heap = [(sortkey(c), c) for c in concepts]
    heapq.heapify(heap)

    push = functools.partial(heapq.heappush, heap)
    pop = functools.partial(heapq.heappop, heap)

    seen = -1

    while heap:
        index, concept = pop()
        # requires sortkey to be an extension of the lattice order
        # (a toplogical sort of it) in the direction of next_concepts
        # assert index >= seen
        if index > seen:
            seen = index
            yield concept
            for c in next_concepts(concept):
                push((sortkey(c), c))


def fcbo(context):
    """Yield ``(extent, intent)`` pairs from ``context``.

    cf. J. Outrata, and V. Vychodil.
    Fast algorithm for computing fixpoints of Galois connections induced by object-attribute relational data.
    Information Sciences 185.1 (2012): 114-127.
    https://doi.org/10.1016/j.ins.2011.09.023
    """
    Extent = context._Extent
    Intent = context._Intent

    n_attributes = len(context.properties)
    attribute_sets = [Intent.infimum] * n_attributes

    concept = Extent.supremum, Intent.infimum

    stack = [(concept, 0, attribute_sets)]

    while stack:
        concept, attribute_index, attribute_sets = stack.pop()

        yield concept

        extent, intent = concept

        if extent == Extent.infimum or attribute_index >= n_attributes:
            continue

        for j in reversed(range(attribute_index, n_attributes)):
            j_attribute = 1 << j

            if j_attribute & intent:
                continue

            mask = j_attribute - 1

            next_attribute_sets = attribute_sets.copy()

            x = next_attribute_sets[j] & mask

            if x & intent == x:
                j_extent = extent & context._extents[j]
                j_intent = Extent.prime(j_extent)

                if j_intent & mask == intent & mask:
                    concept = (Extent.fromint(j_extent), Intent.fromint(j_intent))
                    stack.append((concept, j + 1, next_attribute_sets))
                else:
                    next_attribute_sets[j] = j_intent


def fcbo_dual(context):
    Extent = context._Extent
    Intent = context._Intent

    n_objects = len(context.objects)
    object_sets = [Extent.infimum] * n_objects

    concept = Extent.infimum, Intent.supremum

    stack = [(concept, 0, object_sets)]

    while stack:
        concept, obj_index, object_sets = stack.pop()

        yield concept

        extent, intent = concept

        if extent == Extent.supremum or obj_index >= n_objects:
            continue

        for j in reversed(range(obj_index, n_objects)):
            j_object = 1 << j

            if extent & j_object:
                continue

            mask = j_object - 1

            next_object_sets = object_sets.copy()

            x = next_object_sets[j] & mask

            if x & extent == x:
                j_intent = intent & context._intents[j]
                j_extent = Intent.prime(j_intent)

                if j_extent & mask == extent & mask:
                    concept = (Extent.fromint(j_extent), Intent.fromint(j_intent))
                    stack.append((concept, j + 1, next_object_sets))
                else:
                    next_object_sets[j] = j_extent
