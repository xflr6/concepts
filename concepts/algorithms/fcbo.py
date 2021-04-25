"""Fast Close by One.

cf. J. Outrata, and V. Vychodil.
Fast algorithm for computing fixpoints of Galois connections induced by object-attribute relational data.
Information Sciences 185.1 (2012): 114-127.
https://doi.org/10.1016/j.ins.2011.09.023
"""

__all__ = ['fast_generate_from', 'fcbo_dual']


def iter_j_atom_mask(n: int):
    j_atom = 1
    for j in range(n):
        yield j, j_atom, j_atom - 1
        j_atom <<= 1


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
    Extent = context._Extent
    Intent = context._Intent

    n_attributes = len(context.properties)

    j_attribute_mask = list(iter_j_atom_mask(n_attributes))

    attribute_sets = [Intent.infimum] * n_attributes

    concept = Extent.supremum, Intent.infimum

    stack = [(concept, 0, attribute_sets)]

    while stack:
        concept, attribute_index, attribute_sets = stack.pop()

        yield concept

        extent, intent = concept

        if extent == Extent.infimum or attribute_index == n_attributes:
            continue

        next_attribute_sets = attribute_sets.copy()

        for j, j_attribute, j_mask in reversed(j_attribute_mask[attribute_index:]):
            if j_attribute & intent:
                continue

            x = next_attribute_sets[j] & j_mask

            if x & intent == x:
                j_extent = extent & context._extents[j]
                j_intent = Extent.prime(j_extent)

                if j_intent & j_mask == intent & j_mask:
                    concept = (Extent.fromint(j_extent), Intent.fromint(j_intent))
                    stack.append((concept, j + 1, next_attribute_sets))
                else:
                    next_attribute_sets[j] = j_intent


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
    Extent = context._Extent
    Intent = context._Intent

    n_objects = len(context.objects)

    j_object_mask = list(iter_j_atom_mask(n_objects))

    object_sets = [Extent.infimum] * n_objects

    concept = Extent.infimum, Intent.supremum

    stack = [(concept, 0, object_sets)]

    while stack:
        concept, object_index, object_sets = stack.pop()

        yield concept

        extent, intent = concept

        if extent == Extent.supremum or object_index == n_objects:
            continue

        next_object_sets = object_sets.copy()

        for j, j_object, j_mask in reversed(j_object_mask[object_index:]):
            if extent & j_object:
                continue

            x = next_object_sets[j] & j_mask

            if x & extent == x:
                j_intent = intent & context._intents[j]
                j_extent = Intent.prime(j_intent)

                if j_extent & j_mask == extent & j_mask:
                    concept = (Extent.fromint(j_extent), Intent.fromint(j_intent))
                    stack.append((concept, j + 1, next_object_sets))
                else:
                    next_object_sets[j] = j_extent
