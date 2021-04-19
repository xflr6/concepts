import collections
import functools
import heapq

__all__ = ['lattice', 'neighbors',
           'iterunion',
           'fcbo']


def lattice(Extent, *, infimum):
    """Yield ``(extent, indent, upper, lower)`` in short lexicographic order.

    cf. C. Lindig. 2000. Fast Concept Analysis.
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

    cf. C. Lindig. 2000. Fast Concept Analysis.
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
    """Yield ``(extent, intent)`` pairs from ``context``."""
    Extent = context._Extent
    Intent = context._Intent

    concept = Extent.infimum.doubleprime()

    n_objects = len(context.objects)
    object_sets = [Extent.infimum] * n_objects

    queue = collections.deque([(concept, 0, object_sets)])

    while queue:
        (extent, intent), obj_index, object_sets = queue.popleft()

        yield Extent.fromint(extent), Intent.fromint(intent)

        if extent == Extent.supremum or obj_index >= n_objects:
            continue

        next_object_sets = object_sets.copy()

        for j in range(obj_index, n_objects):
            yj = 1 << j

            if extent & yj:
                continue

            yj -= 1

            x = object_sets[j] & yj

            y = extent & yj

            if x & y == x:
                c = intent & context._intents[j]
                d = Intent.prime(c)

                k = extent & yj

                l = d & yj

                if k == l:
                    queue.append(((d, c), j + 1, next_object_sets))
                else:
                    next_object_sets[j] = d
