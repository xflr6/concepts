# test_definitions.py

import pytest

from concepts.definitions import Definition


def test_fromfile(filename='examples/gewaesser.cxt'):
    objects = ('Fluss', 'Bach', 'Kanal', 'Graben', 'See', 'Tuempel', 'Teich', 'Becken')
    properties = ('fliessend', 'stehend', 'natuerlich', 'kuenstlich', 'gross', 'klein')
    bools = [(True, False, True, False, True, False),
             (True, False, True, False, False, True),
             (True, False, False, True, True, False),
             (True, False, False, True, False, True),
             (False, True, True, False, True, False),
             (False, True, True, False, False, True),
             (False, True, False, True, True, False),
             (False, True, False, True, False, True)]
    assert Definition.fromfile(filename) == (objects, properties, bools)


def test_duplicate_object():
    with pytest.raises(ValueError, match=r'duplicate objects'):
        Definition(('spam', 'spam'), (), [])


def test_duplicate_property():
    with pytest.raises(ValueError, match=r'duplicate properties'):
        Definition((), ('spam', 'spam'), [])


@pytest.fixture(scope='module')
def definition():
    return Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])


def test_unicode(definition):
    assert all(ord(c) < 128 for c in str(definition))
    assert u'%s' % definition == '%s' % definition


def test_ne(definition):
    assert not (definition != definition)


def test_crc32(definition):
    assert definition.crc32() == 'ea62062b'


def test_getitem_int(definition):
    assert definition[0] == definition.objects
    assert definition[1] == definition.properties
    assert definition[2] == definition.bools


def test_getitem(definition):
    assert definition['spam', 'ni'] is True
    with pytest.raises(KeyError):
        definition['ham', 'spam']


def test_setitem_int(definition):
    with pytest.raises(ValueError):
        definition[0] = ('spam',)


def test_union_compatible():
    a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, True)])
    assert a.union(b) == Definition(('spam', 'eggs', 'ham'), ('ni', 'nini'),
                                    [(True, False), (False, False), (True, True)])


def test_union_conflicting():
    a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, False)])
    with pytest.raises(ValueError, match=r"\[\('spam', 'ni'\)\]"):
        a.union(b)


def test_union_ignoring():
    a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, False)])
    assert a.union(b, ignore_conflicts=True) == \
        Definition(('spam', 'eggs', 'ham'), ('ni', 'nini'),
                   [(True, False), (False, False), (True, True)])


def test_union_augmented():
    a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, True)])
    a |= b
    assert a == Definition(('spam', 'eggs', 'ham'), ('ni', 'nini'),
                           [(True, False), (False, False), (True, True)])


def test_inters_compatible():
    a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, True)])
    assert a.intersection(b) == Definition(['spam'], ['ni'], [(True,)])


def test_inters_conflicting():
    a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, False)])
    with pytest.raises(ValueError, match=r"\[\('spam', 'ni'\)\]"):
        a.intersection(b)


def test_inters_ignoring():
    a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, False)])
    assert a.intersection(b, ignore_conflicts=True) == Definition(['spam'],
                                                                  ['ni'],
                                                                  [(False,)])


def test_inters_augmented():
    a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, True)])
    a &= b
    assert a == Definition(['spam'], ['ni'], [(True,)])
