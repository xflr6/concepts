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
