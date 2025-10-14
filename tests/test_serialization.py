import ast
import io
import random

import pytest

from concepts import Context, Definition
from concepts.lattices import Lattice

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


@pytest.mark.parametrize(
    'source, filename, includes_lattice',
    [(repr(SERIALIZED), None, True),
     (repr(SERIALIZED_NOLATTICE), None, False),
     (repr(SERIALIZED), 'example-serialized-lattice.py', True),
     (repr(SERIALIZED_NOLATTICE), 'example-serialized-lattice.py', False)])
def test_fromstring_serialized(tmp_path, source, filename, includes_lattice):
    if filename is None:
        context = Context.fromstring(source, frmat='python-literal')
    else:
        target = tmp_path / filename
        kwargs = {'encoding': 'utf-8'}
        target.write_text(source, **kwargs)
        context = Context.fromfile(str(target), frmat='python-literal', **kwargs)

    assert context.objects == SERIALIZED['objects']
    assert context.properties == SERIALIZED['properties']
    assert context.bools == [
        (True, False, False, True, False, True, True, False, False, True),
        (True, False, False, True, False, True, False, True, True, False),
        (False, True, True, False, False, True, True, False, False, True),
        (False, True, True, False, False, True, False, True, True, False),
        (False, True, False, True, True, False, True, False, False, True),
        (False, True, False, True, True, False, False, True, True, False)]

    if includes_lattice:
        assert 'lattice' in context.__dict__
    else:
        assert 'lattice' not in context.__dict__


@pytest.fixture(params=[SERIALIZED, SERIALIZED_NOLATTICE])
def d(request):
    return request.param


def test_todict(context, d):
    assert 'lattice' not in context.__dict__
    if 'lattice' in d:
        context = Context(context.objects, context.properties, context.bools)
        assert 'lattice' not in context.__dict__

        for ignore_lattice in (False, None):
            assert context.todict(ignore_lattice=ignore_lattice) == d
        assert 'lattice' in context.__dict__
    else:
        for ignore_lattice in (True, None):
            assert context.todict(ignore_lattice=ignore_lattice) == d
        assert 'lattice' not in context.__dict__


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
    with pytest.raises(ValueError, match=rf'missing .*{missing}'):
        Context.fromdict(d_invalid, require_lattice=(missing == 'lattice'))


@pytest.mark.parametrize('nonstring', ['objects', 'properties'])
def test_fromdict_nonstring(d_invalid, nonstring):
    d_invalid[nonstring] = (42,) + d_invalid[nonstring][1:]
    with pytest.raises(ValueError, match=rf'non-string {nonstring}'):
        Context.fromdict(d_invalid)


@pytest.mark.parametrize('short', ['objects', 'context'])
def test_fromdict_mismatch(d_invalid, short):
    d_invalid[short] = d_invalid[short][1:]
    lens = (5, 6) if short == 'objects' else (6, 5)
    match = r'mismatch: {:d} objects with {:d} context'.format(*lens)
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
def ignore_lattice(request):
    return request.param


@pytest.fixture(params=[False, True])
def raw(request):
    return request.param


def test_fromdict(context, lattice, d, require_lattice, ignore_lattice, raw):
    if require_lattice and 'lattice' not in d:
        return

    result = Context.fromdict(d,
                              require_lattice=require_lattice,
                              ignore_lattice=ignore_lattice,
                              raw=raw)

    assert result == context

    if ignore_lattice or 'lattice' not in d:
        assert 'lattice' not in result.__dict__
    else:
        assert 'lattice' in result.__dict__
        assert result.lattice._eq(lattice)


def test_fromdict_raw(context, lattice, d, raw):
    def shuffled(items):
        result = list(items)
        random.shuffle(result)
        return result

    _lattice = d.get('lattice')
    d = {'objects': d['objects'], 'properties': d['properties'],
         'context': [shuffled(intent) for intent in d['context']]}

    if _lattice is not None:
        pairs = shuffled(enumerate(_lattice))
        index_map = {old: new for new, (old, _) in enumerate(pairs)}
        d['lattice'] = [(shuffled(ex), shuffled(in_),
                         shuffled(index_map[i] for i in up),
                         shuffled(index_map[i] for i in lo))
                        for _, (ex, in_, up, lo) in pairs]

    result = Context.fromdict(d, raw=raw)

    assert isinstance(result, Context)
    assert result == context
    if _lattice is not None:
        if raw:
            assert result.lattice._eq(lattice)
        else:
            # instance broken by shuffled(d['lattice'])
            assert not result.lattice._eq(lattice)


@pytest.mark.parametrize('ignore_lattice', [True, None, False])
def test_dict_roundtrip(context, ignore_lattice):
    context = Context(context.objects, context.properties, context.bools)
    assert 'lattice' not in context.__dict__

    d = context.todict(ignore_lattice=ignore_lattice)

    assert isinstance(d, dict) and d
    assert all(d[k] for k in ('objects', 'properties', 'context'))
    if ignore_lattice or ignore_lattice is None:
        assert 'lattice' not in context.__dict__
        assert 'lattice' not in d
    else:
        assert 'lattice' in context.__dict__
        assert d['lattice']

    result = Context.fromdict(d)

    assert isinstance(result, Context)
    assert result == context

    if ignore_lattice or ignore_lattice is None:
        assert 'lattice' not in result.__dict__
    else:
        assert 'lattice' in result.__dict__
        assert result.lattice._eq(context.lattice)


@pytest.mark.parametrize('to_file', [False, True])
@pytest.mark.parametrize(
    'with_lattice, expected_doc, expected_str',
    [(False, SERIALIZED_NOLATTICE,
     '''\
{
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
}
'''),
     (True, SERIALIZED,
     '''\
{
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
''')])
def test_tostring_python_literal(test_output, context, with_lattice,
                                 expected_doc, expected_str, to_file):
    if with_lattice:
        context = context.copy()
        assert context.lattice is not None

    if to_file:
        modifier = '-lattice' if with_lattice else ''
        path = test_output / f'example-serialized{modifier}.py'
        context.tofile(path, frmat='python-literal')
        result = path.read_text(encoding='utf-8')
    else:
        expected_str = expected_str.rstrip()
        result = context.tostring(frmat='python-literal')

    assert result is not None
    assert isinstance(result, str)
    assert result

    doc = ast.literal_eval(result)

    assert doc is not None
    assert isinstance(doc, dict)
    assert doc
    assert doc == expected_doc

    assert result == expected_str


def test_json_roundtrip(context, path_or_fileobj, encoding):
    context = Context(context.objects, context.properties, context.bools)
    assert 'lattice' not in context.__dict__

    is_fileobj = hasattr(path_or_fileobj, 'seek')
    kwargs = {'encoding': encoding} if encoding is not None else {}

    context.tojson(path_or_fileobj, ignore_lattice=True, **kwargs)
    if is_fileobj:
        path_or_fileobj.seek(0)
    assert 'lattice' not in context.__dict__

    deserialized = Context.fromjson(path_or_fileobj, **kwargs)
    if is_fileobj:
        path_or_fileobj.seek(0)
    assert 'lattice' not in deserialized.__dict__

    assert deserialized == context

    assert isinstance(context.lattice, Lattice)
    assert 'lattice' in context.__dict__

    context.tojson(path_or_fileobj, ignore_lattice=None, **kwargs)
    if is_fileobj:
        path_or_fileobj.seek(0)

    deserialized = Context.fromjson(path_or_fileobj, **kwargs)
    assert 'lattice' in deserialized.__dict__

    assert deserialized == context
    assert deserialized.lattice._eq(context.lattice)


def test_tojson_indent4(context, encoding):
    assert 'lattice' not in context.__dict__
    kwargs = {'encoding': encoding} if encoding is not None else {}

    with io.StringIO() as f:
        context.tojson(f, indent=4, sort_keys=True, ignore_lattice=True, **kwargs)
        assert 'lattice' not in context.__dict__

        serialized = f.getvalue()

    assert serialized.startswith('{\n    "context": [')


def test_tojson_newlinedelmited(context, encoding):
    assert 'lattice' not in context.__dict__
    kwargs = {'encoding': encoding} if encoding is not None else {}

    with io.StringIO() as f:
        context.tojson(f, sort_keys=True, ignore_lattice=True, **kwargs)
        assert 'lattice' not in context.__dict__
        f.write(str('\n'))
        serialized = f.getvalue()

        assert serialized.startswith('{"context": [')

        context.tojson(f, sort_keys=True, ignore_lattice=True, **kwargs)
        assert 'lattice' not in context.__dict__
        f.write(str('\n'))
        second = f.getvalue()

    assert second == serialized * 2


@pytest.fixture(scope='module')
def nonascii_context(abba=('Agneta F\xe4ltskog', 'Anni-Frid Lyngstat',
                           'Benny Andersson', 'Bj\xf6rn Ulvaeus')):
    d = Definition()
    for o in abba:
        d.add_object(o, ['human', 'singer'])
    d.add_property('female', abba[:2])
    d.add_property('male', abba[2:])
    d.add_property('keyboarder', [abba[2]])
    d.add_property('guitarrist', [abba[3]])
    d.add_property('sch\xf6n', abba[::2])

    return Context(*d)


def test_json_roundtrip_nonascii_context(nonascii_context, encoding):
    assert isinstance(nonascii_context.lattice, Lattice)
    assert 'lattice' in nonascii_context.__dict__
    kwargs = {'encoding': encoding} if encoding is not None else {}

    with io.StringIO() as f:
        nonascii_context.tojson(f, **kwargs)
        serialized = f.getvalue()
        f.seek(0)

        deserialized = Context.fromjson(f, **kwargs)

    assert 'lattice' in deserialized.__dict__
    assert deserialized == nonascii_context
    assert deserialized.lattice._eq(nonascii_context.lattice)

    assert '"Agneta F\\u00e4ltskog"' in serialized
    assert '"Bj\\u00f6rn Ulvaeus"' in serialized
    assert '"sch\\u00f6n"' in serialized
