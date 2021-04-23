# test_contexts.py

import pytest

from concepts.contexts import Context


def test_empty_objects():
    with pytest.raises(ValueError, match=r'empty objects'):
        Context((), ('spam',), [(False,)])


def test_empty_properies():
    with pytest.raises(ValueError, match=r'empty properties'):
        Context(('spam',), (), [(False,)])


def test_duplicate_object():
    with pytest.raises(ValueError, match=r'duplicate objects'):
        Context(('spam', 'spam'), ('ham', 'eggs'),
                [(True, False), (False, True)])


def test_duplicate_property():
    with pytest.raises(ValueError, match=r'duplicate properties'):
        Context(('spam', 'eggs'), ('ham', 'ham'),
                [(True, False), (False, True)])


def test_object_property_overlap():
    with pytest.raises(ValueError, match=r'overlap'):
        Context(('spam', 'eggs'), ('eggs', 'ham'),
                [(True, False), (False, True)])


def test_invalid_bools_1():
    with pytest.raises(ValueError, match=r'bools is not 2 items of length 2'):
        Context(('spam', 'eggs'), ('camelot', 'launcelot'), [(True, False)])


def test_invalid_bools_2():
    with pytest.raises(ValueError, match=r'bools is not 2 items of length 2'):
        Context(('spam', 'eggs'), ('camelot', 'launcelot'),
                [(True, False, False), (False, True)])


def test_init():
    c = Context(('spam', 'eggs'), ('camelot', 'launcelot'),
                [(True, False), (False, True)])

    assert c.objects == ('spam', 'eggs')
    assert c.properties == ('camelot', 'launcelot')
    assert c.bools == [(True, False), (False, True)]


def test_eq_noncontext(context):
    assert not (context == object())


def test_eq_true(context):
    assert context == Context(context.objects, context.properties,
                              context.bools)


def test_eq_false(context):
    d = context.definition()
    d.move_object('3pl', 0)
    assert not context == Context(*d)


def test_ne_concontext(context):
    assert context != object()


def test_ne_true(context):
    d = context.definition()
    d.move_object('3pl', 0)
    assert context != Context(*d)


def test_ne_false(context):
    assert not context != Context(context.objects, context.properties,
                                  context.bools)


def test_crc32(context):
    assert context.crc32() == 'b9d20179' == context.definition().crc32()


def test_minimize_infimum(context):
    assert list(context._minimize((), context.properties)) == [context.properties]


def test_raw(context):
    Extent, Intent = context._Extent, context._Intent  # noqa: N806
    assert context.intension(['1sg', '1pl'], raw=True) == Intent('1001010000')
    assert context.extension(['+1', '+sg'], raw=True) == Extent('100000')
    assert context.neighbors(['1sg'], raw=True) == \
        [(Extent('110000'), Intent('1001010000')),
         (Extent('101000'), Intent('0000011001')),
         (Extent('100010'), Intent('0001001001'))]


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
    assert context.definition() == (context.objects, context.properties,
                                    context.bools)
