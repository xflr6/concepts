# test_matrices.py

import pytest

from concepts.matrices import Relation


@pytest.fixture(scope='module')
def relation():
    xname = 'Condition'
    yname = 'Symbol'
    xmembers = 'TT', 'TF', 'FT', 'FF'
    ymembers = '->', '<-'
    xbools = [(True, False, True, True), (True, True, False, True)]
    return Relation(xname, yname, xmembers, ymembers, xbools)


def test_pair_with(relation):
    vx, vy = relation
    with pytest.raises(RuntimeError):
        vx._pair_with(relation, 1, vy)
