# test_serialization.py

import pytest

from concepts import Context


SERIALIZED = {
    'objects': (
        '1sg', '1pl', '2sg', '2pl', '3sg', '3pl',
    ),
    'properties': (
        '+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl',
    ),
    'context': [
        (0, 3, 5, 6, 9),
        (0, 3, 5, 7, 8),
        (1, 2, 5, 6, 9),
        (1, 2, 5, 7, 8),
        (1, 3, 4, 6, 9),
        (1, 3, 4, 7, 8),
    ],
    'lattice': [
        ((), (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), (1, 2, 3, 4, 5, 6), ()),
        ((0,), (0, 3, 5, 6, 9), (7, 8, 9), (0,)),
        ((1,), (0, 3, 5, 7, 8), (7, 10, 11), (0,)),
        ((2,), (1, 2, 5, 6, 9), (8, 12, 13), (0,)),
        ((3,), (1, 2, 5, 7, 8), (10, 12, 14), (0,)),
        ((4,), (1, 3, 4, 6, 9), (9, 13, 15), (0,)),
        ((5,), (1, 3, 4, 7, 8), (11, 14, 15), (0,)),
        ((0, 1), (0, 3, 5), (18, 19), (1, 2)),
        ((0, 2), (5, 6, 9), (16, 18), (1, 3)),
        ((0, 4), (3, 6, 9), (16, 19), (1, 5)),
        ((1, 3), (5, 7, 8), (17, 18), (2, 4)),
        ((1, 5), (3, 7, 8), (17, 19), (2, 6)),
        ((2, 3), (1, 2, 5), (18, 20), (3, 4)),
        ((2, 4), (1, 6, 9), (16, 20), (3, 5)),
        ((3, 5), (1, 7, 8), (17, 20), (4, 6)),
        ((4, 5), (1, 3, 4), (19, 20), (5, 6)),
        ((0, 2, 4), (6, 9), (21,), (8, 9, 13)),
        ((1, 3, 5), (7, 8), (21,), (10, 11, 14)),
        ((0, 1, 2, 3), (5,), (21,), (7, 8, 10, 12)),
        ((0, 1, 4, 5), (3,), (21,), (7, 9, 11, 15)),
        ((2, 3, 4, 5), (1,), (21,), (12, 13, 14, 15)),
        ((0, 1, 2, 3, 4, 5), (), (), (18, 19, 20, 16, 17)),
    ],
}

SERIALIZED_NOLATTICE = {'objects': SERIALIZED['objects'],
                        'properties': SERIALIZED['properties'],
                        'context': list(SERIALIZED['context'])}


@pytest.fixture(params=[SERIALIZED, SERIALIZED_NOLATTICE])
def d(request):
    return request.param


def test_todict(context, d):
    assert 'lattice' not in context.__dict__
    if 'lattice' not in d:
        assert context.todict() == context.todict(include_lattice=False) == d
        assert 'lattice' not in context.__dict__
    else:
        context = Context(context.objects, context.properties, context.bools)
        assert 'lattice' not in context.__dict__
        assert context.todict(include_lattice=True) == context.todict() == d
        assert 'lattice' in context.__dict__


@pytest.fixture
def d_invalid():
    return {'objects': SERIALIZED['objects'],
            'properties': SERIALIZED['properties'],
            'context': list(SERIALIZED['context']),
            'lattice': list(SERIALIZED['lattice'])}


@pytest.mark.parametrize('missing',
                         ['objects', 'properties', 'context', 'lattice'])
def test_fromdict_missing(d_invalid, missing):
    del d_invalid[missing]
    with pytest.raises(ValueError, match=r'missing .*%s' % missing):
        Context.fromdict(d_invalid, require_lattice=(missing == 'lattice'))


@pytest.mark.parametrize('nonstring', ['objects', 'properties'])
def test_fromdict_nonstring(d_invalid, nonstring):
    d_invalid[nonstring] = (42,) + d_invalid[nonstring][1:]
    with pytest.raises(ValueError, match=r'non-string %s' % nonstring):
        Context.fromdict(d_invalid)


@pytest.mark.parametrize('short', ['objects', 'context'])
def test_fromdict_mismatch(d_invalid, short):
    d_invalid[short] = d_invalid[short][1:]
    lens = (5, 6) if short == 'objects' else (6, 5)
    match = r'mismatch: %d objects with %d context' % lens
    with pytest.raises(ValueError, match=match):
        Context.fromdict(d_invalid)


def test_fromdict_context_duplicates(d_invalid):
    first = d_invalid['context'][0]
    d_invalid['context'][0] = (first[0], first[0]) + first[2:]
    with pytest.raises(ValueError, match='duplicate'):
        Context.fromdict(d_invalid)


def test_fromdict_context_invalid_index(d_invalid):
    first = d_invalid['context'][0]
    d_invalid['context'][0] = (42,) + first[1:]
    with pytest.raises(ValueError, match='invalid index'):
        Context.fromdict(d_invalid)


def test_fromdict_empty_lattice(d_invalid):
    d_invalid['lattice'] = []
    with pytest.raises(ValueError, match='empty lattice'):
        Context.fromdict(d_invalid)


@pytest.fixture(params=[False, True])
def require_lattice(request):
    return request.param


@pytest.fixture(params=[False, True])
def exclude_lattice(request):
    return request.param


@pytest.fixture(params=[False, True])
def raw(request):
    return request.param


def test_fromdict(context, d, require_lattice, exclude_lattice, raw):
    if require_lattice and 'lattice' not in d:
        return

    result = Context.fromdict(d,
                              require_lattice=require_lattice,
                              exclude_lattice=exclude_lattice,
                              raw=raw)

    assert result == context

    if exclude_lattice or 'lattice' not in d:
        assert 'lattice' not in result.__dict__
    else:
        assert 'lattice' in result.__dict__
        assert result.lattice


@pytest.mark.parametrize('include_lattice', [False, None, True])
def test_roundtrip(context, include_lattice):
    context = Context(context.objects, context.properties, context.bools)
    assert 'lattice' not in context.__dict__

    d = context.todict(include_lattice=include_lattice)

    assert isinstance(d, dict) and d
    assert all(d[k] for k in ('objects', 'properties', 'context'))
    if include_lattice:
        assert 'lattice' in context.__dict__
        assert d['lattice']
    else:
        assert 'lattice' not in context.__dict__
        assert 'lattice' not in d
