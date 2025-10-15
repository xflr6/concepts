import pytest

from concepts import matrices


@pytest.fixture(scope='module')
def relation():
    xname = 'Condition'
    yname = 'Symbol'
    xmembers = 'TT', 'TF', 'FT', 'FF'
    ymembers = '->', '<-'
    xbools = [(True, False, True, True), (True, True, False, True)]
    return matrices.Relation(xname, yname, xmembers, ymembers, xbools)


def test_pair_with(relation):
    (vx, vy) = relation
    with pytest.raises(RuntimeError, match=r'attempt _pair_with'):
        vx._pair_with(relation, 1, vy)


def test_prime_infimum(relation):
    vx, vy = relation

    assert vx.prime(0) == vy.BitSet.supremum
    assert vy.prime(0) == vx.BitSet.supremum
