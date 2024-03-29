import pytest

import concepts


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

    assert concepts.Definition.fromfile(filename) == (objects,
                                                      properties,
                                                      bools)


def test_duplicate_object():
    with pytest.raises(ValueError, match=r'duplicate objects'):
        concepts.Definition(('spam', 'spam'), (), [])


def test_duplicate_property():
    with pytest.raises(ValueError, match=r'duplicate properties'):
        concepts.Definition((), ('spam', 'spam'), [])


@pytest.fixture(scope='module')
def definition():
    return concepts.Definition(('spam', 'eggs'),
                               ('ni',),
                               [(True,),
                                (False,)])


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


def test_getitem_missing(definition):
    with pytest.raises(KeyError):
        definition['ham', 'spam']


def test_setitem_int(definition):
    with pytest.raises(ValueError):
        definition[0] = ('spam',)


def test_union_compatible():
    a = concepts.Definition(('spam', 'eggs'),
                            ('ni',),
                            [(True,),
                             (False,)])

    b = concepts.Definition(('ham', 'spam'),
                            ('nini', 'ni'),
                            [(True, True),
                             (False, True)])

    assert a.union(b) == concepts.Definition(('spam', 'eggs', 'ham'),
                                             ('ni', 'nini'),
                                             [(True, False),
                                              (False, False),
                                              (True, True)])


def test_union_conflicting():
    a = concepts.Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
    b = concepts.Definition(('ham', 'spam'), ('nini', 'ni'),
                            [(True, True), (False, False)])
    with pytest.raises(ValueError, match=r"\[\('spam', 'ni'\)\]"):
        a.union(b)


def test_union_ignoring():
    a = concepts.Definition(('spam', 'eggs'),
                            ('ni',),
                            [(True,),
                             (False,)])

    b = concepts.Definition(('ham', 'spam'),
                            ('nini', 'ni'),
                            [(True, True),
                             (False, False)])

    assert a.union(b, ignore_conflicts=True) == \
        concepts.Definition(('spam', 'eggs', 'ham'),
                            ('ni', 'nini'),
                            [(True, False),
                             (False, False),
                             (True, True)])


def test_union_augmented():
    a = concepts.Definition(('spam', 'eggs'),
                            ('ni',),
                            [(True,), (False,)])

    b = concepts.Definition(('ham', 'spam'),
                            ('nini', 'ni'),
                            [(True, True),
                             (False, True)])

    a |= b

    assert a == concepts.Definition(('spam', 'eggs', 'ham'),
                                    ('ni', 'nini'),
                                    [(True, False),
                                     (False, False),
                                     (True, True)])


def test_inters_compatible():
    a = concepts.Definition(('spam', 'eggs'),
                            ('ni',),
                            [(True,),
                             (False,)])

    b = concepts.Definition(('ham', 'spam'),
                            ('nini', 'ni'),
                            [(True, True),
                             (False, True)])

    assert a.intersection(b) == concepts.Definition(['spam'],
                                                    ['ni'],
                                                    [(True,)])


def test_inters_conflicting():
    a = concepts.Definition(('spam', 'eggs'),
                            ('ni',),
                            [(True,), (False,)])

    b = concepts.Definition(('ham', 'spam'),
                            ('nini', 'ni'),
                            [(True, True),
                             (False, False)])

    with pytest.raises(ValueError, match=r"\[\('spam', 'ni'\)\]"):
        a.intersection(b)


def test_inters_ignoring():
    a = concepts.Definition(('spam', 'eggs'),
                            ('ni',),
                            [(True,),
                             (False,)])

    b = concepts.Definition(('ham', 'spam'),
                            ('nini', 'ni',),
                            [(True, True),
                             (False, False)])

    assert a.intersection(b, ignore_conflicts=True) == \
        concepts.Definition(['spam'], ['ni'], [(False,)])


def test_inters_augmented():
    a = concepts.Definition(('spam', 'eggs'),
                            ('ni',),
                            [(True,),
                             (False,)])

    b = concepts.Definition(('ham', 'spam'),
                            ('nini', 'ni',),
                            [(True, True),
                             (False, True)])

    a &= b

    assert a == concepts.Definition(['spam'], ['ni'], [(True,)])
