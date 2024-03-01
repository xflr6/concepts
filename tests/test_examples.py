import pytest

import concepts


def test_load_dataset():
    context = concepts.load_dataset('livingbeings_en')

    assert len(context.objects) == 8
    assert len(context.properties) == 9
