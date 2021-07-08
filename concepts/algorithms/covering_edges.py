"""Covering Edges

cf. Carpineto, Claudio, and Giovanni Romano.
Concept data analysis: Theory and applications.
John Wiley & Sons, 2004.
"""

from collections import Counter

from .fcbo import fast_generate_from


def lattice(context):
    concepts = tuple(fast_generate_from(context))
    edges = covering_edges(concepts, context)

    mapping = dict([(extent, (extent, intent, [], [])) for extent, intent in concepts])

    for concept, lower_neighbor in edges:
        extent, _ = concept
        lower_extent, _ = lower_neighbor

        mapping[extent][3].append(lower_extent)
        mapping[lower_extent][2].append(extent)

    return mapping.values()


def covering_edges(concept_list, context):
    """Yield mapping edge as ``((extent, intent), (lower_extent, lower_intent))``
    pairs (concept and it's lower neighbor) from ``context`` and ``concept_list``

    Example:
        >>> from concepts import make_context, ConceptList
        >>> from concepts._common import Concept

        >>> context = make_context('''
        ...  |0|1|2|3|4|5|
        ... A|X|X|X| | | |
        ... B|X| |X|X|X|X|
        ... C|X|X| | |X| |
        ... D| |X|X| | | |''')

        >>> concepts = [('ABCD', ''),
        ...             ('ABC', '0'),
        ...             ('AC', '01'),
        ...             ('A', '012'),
        ...             ('', '012345'),
        ...             ('C', '014'),
        ...             ('AB', '02'),
        ...             ('B', '02345'),
        ...             ('BC', '04'),
        ...             ('ACD', '1'),
        ...             ('AD', '12'),
        ...             ('ABD', '2')]

        >>> concept_list = ConceptList.frompairs(
        ...     map(lambda c: (context._Objects.frommembers(c[0]),
        ...                    context._Properties.frommembers(c[1])),
        ...         concepts))

        >>> edges = covering_edges(concept_list, context)

        >>> [(''.join(concept[0].members()), # doctest: +NORMALIZE_WHITESPACE
        ...   ''.join(lower[0].members()))
        ...  for concept, lower in edges]
        [('ABCD', 'ABC'),
         ('ABCD', 'ACD'),
         ('ABCD', 'ABD'),
         ('ABC', 'AC'),
         ('ABC', 'AB'),
         ('ABC', 'BC'),
         ('AC', 'A'),
         ('AC', 'C'),
         ('A', ''),
         ('C', ''),
         ('AB', 'A'),
         ('AB', 'B'),
         ('B', ''),
         ('BC', 'C'),
         ('BC', 'B'),
         ('ACD', 'AC'),
         ('ACD', 'AD'),
         ('AD', 'A'),
         ('ABD', 'AB'),
         ('ABD', 'AD')]
    """
    Objects = context._Objects
    Properties = context._Properties

    concept_index = dict(concept_list)

    for extent, intent in concept_index.items():
        candidate_counter = Counter()

        property_candidates = Properties.fromint(Properties.supremum & ~intent)

        for atom in property_candidates.atoms():
            extent_candidate = Objects.fromint(extent & atom.prime())
            intent_candidate = concept_index[extent_candidate]
            candidate_counter[extent_candidate] += 1

            if (intent_candidate.count() - intent.count()) == candidate_counter[extent_candidate]:
                yield (extent, intent), (extent_candidate, intent_candidate)