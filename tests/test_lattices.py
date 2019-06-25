# test_lattices.py

import pickle
import functools

import pytest

from concepts.contexts import Context
from concepts.lattices import Concept


def test_eq_nonlattice(lattice):
    assert not lattice == object()


def test_eq(lattice):
    assert lattice == lattice

    d = lattice._context.definition()
    assert lattice == Context(*d).lattice

    d.move_object('3pl', 0)
    assert not lattice == Context(*d).lattice


def test_eq_mapping(lattice):
    other = Context(*lattice._context.definition()).lattice
    k, v = other._mapping.popitem()
    assert not other == lattice

    k = k.__class__.frommembers(['1sg', '3pl'])
    other._mapping[k] = v
    assert not other == lattice


def test_eq_concepts(lattice):
    other = Context(*lattice._context.definition()).lattice
    c = other[16]

    for attname in ('index', 'dindex'):
        i = getattr(c, attname)
        setattr(c, attname, -1)
        assert not other == lattice
        setattr(c, attname, i)

    for attname in ('atoms', 'properties', 'objects'):
        t = tuple(getattr(c, attname))
        if attname == 'objects':
            setattr(c, attname, ('spam',))
        else:
            setattr(c, attname, tuple(reversed(t)))
        assert not other == lattice
        setattr(c, attname, t)


def test_ne_nonlattice(lattice):
    assert lattice != object()


def test_ne(lattice):
    assert not lattice != lattice


def test_concept_eq_nonconcept(lattice):
    assert lattice[1]._eq(object()) is NotImplemented


def test_concept_eq(lattice):
    assert lattice[5]._eq(lattice[5])
    assert not lattice[1]._eq(lattice[7])


def test_concept_eq_neighors(lattice):
    c = lattice[7]
    mock_concept = functools.partial(Concept, c.lattice, c._extent, c._intent)
    assert not c._eq(mock_concept(c.upper_neighbors[1:], c.lower_neighbors))
    assert not c._eq(mock_concept(c.upper_neighbors, c.lower_neighbors[1:]))
    assert not c._eq(mock_concept(tuple(reversed(c.upper_neighbors)),
                                  c.lower_neighbors))
    assert not c._eq(mock_concept(c.upper_neighbors,
                                  tuple(reversed(c.lower_neighbors))))


def test_pickling(lattice):
    result = pickle.loads(pickle.dumps(lattice))
    assert result._context, lattice._context
    assert [tuple(c) for c in result._concepts] == \
           [tuple(c) for c in lattice._concepts]


def test_len(lattice):
    assert len(lattice) == 22


def test_unicode(lattice):
    assert all(ord(c) < 128 for c in str(lattice))
    assert u'%s' % lattice == '%s' % lattice


@pytest.mark.parametrize('concepts, expected', [
    ([('+1',), ('+2',)], [('+1',), ('+2',),
                          ('-3',), ('-2',), ('-1',),
                          ()]),
])
def test_upset_union(lattice, concepts, expected):
    concepts, expected = ([lattice[a] for a in arg] for arg in (concepts, expected))
    assert list(lattice.upset_union(concepts)) == expected


@pytest.mark.parametrize('concepts, expected', [
    ([('+1',), ('+2',)], [('+1',), ('+2',),
                          ('+1', '+sg'), ('+1', '+pl'),
                          ('+2', '+sg'), ('+2', '+pl'),
                          ('+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl')]),
])
def test_downset_union(lattice, concepts, expected):
    concepts, expected = ([lattice[a] for a in arg]
                          for arg in (concepts, expected))
    assert list(lattice.downset_union(concepts)) == expected


@pytest.mark.parametrize('concepts, expected', [
    ([('+1', '+sg'), ('+2', '+sg'), ('+3', '+sg')],
     [('+1', '+sg'), ('+2', '+sg'), ('+3', '+sg'),
      ('-3', '+sg'), ('-2', '+sg'), ('-1', '+sg'),
      ('+sg',)]),
])
def test_upset_generalization(lattice, concepts, expected):
    concepts, expected = ([lattice[a] for a in arg]
                          for arg in (concepts, expected))
    assert list(lattice.upset_generalization(concepts)) == expected


def test_minimal(lattice):
    assert lattice.infimum.minimal() == ('+1', '-1', '+2', '-2', '+3', '-3',
                                         '+sg', '+pl', '-sg', '-pl')


def test_minimum():
    l = Context(('spam',), ('ham',), [(True,)]).lattice
    assert len(l) == 1
    assert l.infimum is l.supremum
    assert l.atoms == ()


def test_trivial():
    l = Context(('spam',), ('ham',), [(False,)]).lattice
    assert len(l) == 2
    assert l.infimum is not l.supremum
    assert l.atoms == (l.supremum,)


def test_nonatomic():
    m = Context(('spam', 'eggs'), ('ham',), [(True,), (True,)]).lattice
    assert [tuple(c) for c in m] == [(('spam', 'eggs'), ('ham',))]
    t = Context(('spam', 'eggs'), ('ham',), [(False,), (False,)]).lattice
    assert [tuple(c) for c in t] == [((), ('ham',)), (('spam', 'eggs'), ())]
