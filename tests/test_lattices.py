# test_lattices.py

import unittest
import pickle

from concepts.contexts import Context


class TestLattice(unittest.TestCase):

    source = '''
       |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    1sg| X|  |  | X|  | X|  X|   |   |  X|
    1pl| X|  |  | X|  | X|   |  X|  X|   |
    2sg|  | X| X|  |  | X|  X|   |   |  X|
    2pl|  | X| X|  |  | X|   |  X|  X|   |
    3sg|  | X|  | X| X|  |  X|   |   |  X|
    3pl|  | X|  | X| X|  |   |  X|  X|   |
    '''

    @classmethod
    def setUpClass(cls, source=None):
        if source is None:
            source = cls.source
        context = Context.fromstring(source)
        cls.lattice = context.lattice

    @classmethod
    def tearDownClass(cls):
        del cls.lattice

    def test_pickling(self):
        result = pickle.loads(pickle.dumps(self.lattice))
        self.assertEqual(result._context, self.lattice._context)
        self.assertEqual([tuple(c) for c in result._concepts],
            [tuple(c) for c in self.lattice._concepts])

    def test_len(self):
        self.assertEqual(len(self.lattice), 22)

    def test_unicode(self):
        assert all(ord(c) < 128 for c in str(self.lattice))
        self.assertEqual(u'%s' % self.lattice, '%s' % self.lattice)

    def test_upset_union(self):
        l = self.lattice
        self.assertEqual(list(l.upset_union([l[('+1',)], l[('+2',)]])),
            [l[('+1',)], l[('+2',)],
             l[('-3',)], l[('-2',)], l[('-1',)],
             l.supremum])

    def test_downset_union(self):
        l = self.lattice
        self.assertEqual(list(l.downset_union([l[('+1',)], l[('+2',)]])),
            [l[('+1',)], l[('+2',)],
             l[('+1', '+sg')], l[('+1', '+pl')],
             l[('+2', '+sg')], l[('+2', '+pl')],
             l.infimum])

    def test_upset_generalization(self):
        l = self.lattice
        self.assertEqual(list(l.upset_generalization(
            [l[('+1', '+sg')], l[('+2', '+sg')], l[('+3', '+sg')]])),
            [l[('+1', '+sg')], l[('+2', '+sg')], l[('+3', '+sg')],
             l[('-3', '+sg')], l[('-2', '+sg')], l[('-1', '+sg')],
             l[('+sg',)]])


class TestInfimum(TestLattice):

    def test_minimal(self):
        self.assertEqual(self.lattice.infimum.minimal(),
            ('+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl'))


class TestSmallest(unittest.TestCase):

    def test_minimum(self):
        l = Context(('spam',), ('ham',), [(True,)]).lattice
        self.assertEqual(len(l), 1)
        self.assertIs(l.infimum, l.supremum)
        self.assertEqual(l.atoms, ())

    def test_trivial(self):
        l = Context(('spam',), ('ham',), [(False,)]).lattice
        self.assertEqual(len(l), 2)
        self.assertIsNot(l.infimum, l.supremum)
        self.assertEqual(l.atoms, (l.supremum,))

    def test_nonatomic(self):
        m = Context(('spam', 'eggs'), ('ham',), [(True,), (True,)]).lattice
        self.assertEqual([tuple(c) for c in m],
            [(('spam', 'eggs'), ('ham',))])
        t = Context(('spam', 'eggs'), ('ham',), [(False,), (False,)]).lattice
        self.assertEqual([tuple(c) for c in t],
            [((), ('ham',)), (('spam', 'eggs'), ())])
