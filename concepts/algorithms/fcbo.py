"""Fast Close by One.

cf. J. Outrata, and V. Vychodil.
Fast algorithm for computing fixpoints of Galois connections induced by object-attribute relational data.
Information Sciences 185.1 (2012): 114-127.
https://doi.org/10.1016/j.ins.2011.09.023
"""

__all__ = ['fast_generate_from', 'fcbo_dual']


def fast_generate_from(context):
    """Yield ``(extent, intent)`` pairs from ``context`` (by intents).

    Example:
        >>> from concepts import make_context

        >>> context = make_context('''
        ...  |0|1|2|3|4|5|
        ... A|X|X|X| | | |
        ... B|X| |X|X|X|X|
        ... C|X|X| | |X| |
        ... D| |X|X| | | |''')

        >>> [(''.join(extent.members()),  # doctest: +NORMALIZE_WHITESPACE
        ...   ''.join(intent.members()))
        ...  for extent, intent in fast_generate_from(context)]
        [('ABCD', ''),
         ('ABC', '0'),
         ('AC', '01'),
         ('A', '012'),
         ('', '012345'),
         ('C', '014'),
         ('AB', '02'),
         ('B', '02345'),
         ('BC', '04'),
         ('ACD', '1'),
         ('AD', '12'),
         ('ABD', '2')]
    """
    n_properties = context.shape.properties

    Properties = context._Properties

    j_atom = list(enumerate(Properties.supremum.atoms()))

    Objects = context._Objects

    prime = Objects.prime

    stack = [(Objects.supremum.doubleprime(), 0, [Properties.infimum] * n_properties)]

    while stack:
        concept, property_index, property_sets = stack.pop()

        yield concept

        (extent, intent) = concept

        if property_index == n_properties or not extent:
            continue

        next_property_sets = property_sets.copy()

        for j, j_property in reversed(j_atom[property_index:]):
            if j_property & intent:
                continue

            j_mask = j_property - 1

            x = next_property_sets[j] & j_mask

            if x & intent == x:
                j_extent = extent & context._extents[j]

                j_intent = prime(j_extent)

                j_lower = j_intent & j_mask

                if j_lower & intent == j_lower:
                    concept = (Objects.fromint(j_extent), Properties.fromint(j_intent))
                    stack.append((concept, j + 1, next_property_sets))
                else:
                    next_property_sets[j] = j_intent


def fcbo_dual(context):
    """Yield ``(extent, intent)`` pairs from ``context`` (by extents).

    Example:
        >>> from concepts import make_context

        >>> context = make_context('''
        ...  |0|1|2|3|4|5|
        ... A|X|X|X| | | |
        ... B|X| |X|X|X|X|
        ... C|X|X| | |X| |
        ... D| |X|X| | | |''')

        >>> [(''.join(extent.members()),  # doctest: +NORMALIZE_WHITESPACE
        ...   ''.join(intent.members()))
        ...  for extent, intent in fcbo_dual(context)]
        [('', '012345'),
         ('A', '012'),
         ('AB', '02'),
         ('ABC', '0'),
         ('ABCD', ''),
         ('ABD', '2'),
         ('AC', '01'),
         ('ACD', '1'),
         ('AD', '12'),
         ('B', '02345'),
         ('BC', '04'),
         ('C', '014')]
    """
    n_objects = context.shape.objects

    Objects = context._Objects

    j_atom = list(enumerate(Objects.supremum.atoms()))

    Properties = context._Properties

    prime = Properties.prime

    stack = [(Objects.infimum.doubleprime(), 0, [Objects.infimum] * n_objects)]

    while stack:
        concept, object_index, object_sets = stack.pop()

        yield concept

        (extent, intent) = concept

        if object_index == n_objects or not intent:
            continue

        next_object_sets = object_sets.copy()

        for j, j_object in reversed(j_atom[object_index:]):
            if extent & j_object:
                continue

            j_mask = j_object - 1

            x = next_object_sets[j] & j_mask

            if x & extent == x:
                j_intent = intent & context._intents[j]

                j_extent = prime(j_intent)

                j_lower = j_extent & j_mask

                if j_lower & extent == j_lower:
                    concept = (Objects.fromint(j_extent), Properties.fromint(j_intent))
                    stack.append((concept, j + 1, next_object_sets))
                else:
                    next_object_sets[j] = j_extent
