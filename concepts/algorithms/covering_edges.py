"""Covering Edges

cf. Carpineto, Claudio, and Giovanni Romano.
Concept data analysis: Theory and applications.
John Wiley & Sons, 2004.
"""


def covering_edges(concept_list, context):
    """Yield mapping edge as ``((extent, intent), (lower_extent, lower_intent))``
    pairs (concept and it's lower neighbor) from ``context`` and ``concept_list``"""
    Objects = context._Objects
    Properties = context._Properties

    concept_index = dict(concept_list)

    for extent, intent in concept_index.items():
        candidate_counter = dict.fromkeys(concept_index, 0)

        property_candidates = Properties.supremum - intent

        for atom in Properties.fromint(property_candidates).atoms():
            extent_candidate = Objects.fromint(extent & atom.prime())
            intent_candidate = concept_index[extent_candidate]
            candidate_counter[extent_candidate] += 1

            if (intent_candidate.count() - intent.count()) == candidate_counter[extent_candidate]:
                yield (extent, intent), (extent_candidate, intent_candidate)
