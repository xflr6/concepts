"""Covering Edges

cf. Carpineto, Claudio, and Giovanni Romano.
Concept data analysis: Theory and applications.
John Wiley & Sons, 2004.
"""

import multiprocessing
import itertools
import collections

from .fcbo import fast_generate_from


def covering_edges(concept_list, context, concept_index=None):
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

    if not concept_index:
        concept_index = dict(concept_list)

    for extent, intent in concept_list:
        candidate_counter = collections.Counter()

        property_candidates = Properties.fromint(Properties.supremum & ~intent)

        for atom in property_candidates.atoms():
            extent_candidate = Objects.fromint(extent & atom.prime())
            intent_candidate = concept_index[extent_candidate]
            candidate_counter[extent_candidate] += 1

            if (intent_candidate.count() - intent.count()) == candidate_counter[extent_candidate]:
                yield (extent, intent), (extent_candidate, intent_candidate)


def _return_edges(batch, concept_index, context):
    return list(covering_edges(batch, concept_index, context))


def lattice_fcbo(context, n_of_processes=1):
    """Returns tuple of tuples in form of ``(extent, intent, upper, lower)`` in short lexicographic order."""
    concepts = list(fast_generate_from(context))
    concepts.sort(key=lambda concept: concept[0].shortlex())
    concept_index = dict(concepts)

    if n_of_processes == 1:
        edges = covering_edges(concepts, context, concept_index=concept_index)
    else:
        batches = [concepts[i::n_of_processes] for i in range(0, n_of_processes)]

        with multiprocessing.Pool(n_of_processes) as p:
            results = [p.apply_async(_return_edges, (batch, context, concept_index)) for batch in batches]
            edges = itertools.chain.from_iterable([result.get() for result in results])

    mapping = dict([(extent, (extent, intent, [], [])) for extent, intent in concepts])

    for concept, lower_neighbor in edges:
        extent, _ = concept
        lower_extent, _ = lower_neighbor

        mapping[extent][3].append(lower_extent)
        mapping[lower_extent][2].append(extent)

    return tuple(mapping.values())