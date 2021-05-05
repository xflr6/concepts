from concepts import algorithms
from concepts import formats


def test_concept_list_tofile(tmp_path, context):
    target = tmp_path / 'ConceptList-intents.dat'

    concept_list = algorithms.get_concepts(context)

    concept_list.tofile(target)

    result = list(formats.read_concepts_dat(target))

    expected = [c.intent_index_set() for c in concept_list]

    assert result == expected
