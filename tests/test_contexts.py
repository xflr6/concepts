import pytest

import concepts


def test_empty_objects():
    with pytest.raises(ValueError, match=r'empty objects'):
        concepts.Context((), ('spam',), [(False,)])


def test_empty_properies():
    with pytest.raises(ValueError, match=r'empty properties'):
        concepts.Context(('spam',), (), [(False,)])


def test_duplicate_object():
    with pytest.raises(ValueError, match=r'duplicate objects'):
        concepts.Context(('spam', 'spam'),
                         ('ham', 'eggs'),
                         [(True, False), (False, True)])


def test_duplicate_property():
    with pytest.raises(ValueError, match=r'duplicate properties'):
        concepts.Context(('spam', 'eggs'),
                         ('ham', 'ham'),
                         [(True, False), (False, True)])


def test_object_property_overlap():
    with pytest.raises(ValueError, match=r'overlap'):
        concepts.Context(('spam', 'eggs'),
                         ('eggs', 'ham'),
                         [(True, False), (False, True)])


def test_invalid_bools_1():
    with pytest.raises(ValueError, match=r'bools is not 2 items of length 2'):
        concepts.Context(('spam', 'eggs'),
                         ('camelot', 'launcelot'),
                         [(True, False)])


def test_invalid_bools_2():
    with pytest.raises(ValueError, match=r'bools is not 2 items of length 2'):
        concepts.Context(('spam', 'eggs'),
                         ('camelot', 'launcelot'),
                         [(True, False, False), (False, True)])


def test_init():
    c = concepts.Context(('spam', 'eggs'),
                         ('camelot', 'launcelot'),
                         [(True, False), (False, True)])

    assert c.objects == ('spam', 'eggs')
    assert c.properties == ('camelot', 'launcelot')
    assert c.bools == [(True, False), (False, True)]


def test_copy(context):
    context = concepts.Context(context.objects,
                               context.properties,
                               context.bools)
    assert context.lattice is not None

    copy = context.copy()

    assert copy == context
    assert 'lattice' not in copy.__dict__


def test_eq_noncontext(context):
    assert not (context == object())


def test_eq_true(context):
    assert context == concepts.Context(context.objects,
                                       context.properties,
                                       context.bools)


def test_eq_false(context):
    d = context.definition()
    d.move_object('3pl', 0)
    assert not context == concepts.Context(*d)


def test_ne_concontext(context):
    assert context != object()


def test_ne_true(context):
    d = context.definition()
    d.move_object('3pl', 0)
    assert context != concepts.Context(*d)


def test_ne_false(context):
    assert not context != concepts.Context(context.objects,
                                           context.properties,
                                           context.bools)


def test_crc32(context):
    assert context.crc32() == 'b9d20179' == context.definition().crc32()


def test_minimize_infimum(context):
    assert list(context._minimize((), context.properties)) == [context.properties]


def test_raw(context):
    Objects = context._Objects  # noqa: N806
    Properties = context._Properties  # noqa: N806
    assert context.intension(['1sg', '1pl'], raw=True) == Properties('1001010000')
    assert context.extension(['+1', '+sg'], raw=True) == Objects('100000')
    assert context.neighbors(['1sg'], raw=True) == \
        [(Objects('110000'), Properties('1001010000')),
         (Objects('101000'), Properties('0000011001')),
         (Objects('100010'), Properties('0001001001'))]


def test_tofile(tmp_path, context, filename='context.cxt', encoding='utf-8'):
    filepath = tmp_path / filename
    context.tofile(str(filepath), encoding=encoding)
    assert filepath.read_text(encoding=encoding) == '''\
B

6
10

1sg
1pl
2sg
2pl
3sg
3pl
+1
-1
+2
-2
+3
-3
+sg
+pl
-sg
-pl
X..X.XX..X
X..X.X.XX.
.XX..XX..X
.XX..X.XX.
.X.XX.X..X
.X.XX..XX.
'''


def test_definition(context):
    assert context.definition() == (context.objects,
                                    context.properties,
                                    context.bools)
