# test_lattices.py

import unittest

import pickle

from concepts.contexts import Context

CONTEXT = '''
   |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
1sg| X|  |  | X|  | X|  X|   |   |  X|
1pl| X|  |  | X|  | X|   |  X|  X|   |
2sg|  | X| X|  |  | X|  X|   |   |  X|
2pl|  | X| X|  |  | X|   |  X|  X|   |
3sg|  | X|  | X| X|  |  X|   |   |  X|
3pl|  | X|  | X| X|  |   |  X|  X|   |
'''


def setUpModule():
    global lattice
    lattice = Context.fromstring(CONTEXT).lattice


def tearDownModule():
    global lattice
    del lattice


class TestLattice(unittest.TestCase):

    def test_pickling(self):
        result = pickle.loads(pickle.dumps(lattice))
        self.assertEqual(result._context, lattice._context)
        self.assertEqual([tuple(c) for c in result._concepts],
            [tuple(c) for c in lattice._concepts])

    def test_len(self):
        self.assertEqual(len(lattice), 22)

    def test_upset_union(self):
        self.assertEqual(list(lattice.upset_union(
            [lattice[('+1',)], lattice[('+2',)]])),
            [lattice[('+1',)], lattice[('+2',)],
             lattice[('-3',)], lattice[('-2',)], lattice[('-1',)],
             lattice.supremum])

    def test_downset_union(self):
        self.assertEqual(list(lattice.downset_union(
            [lattice[('+1',)], lattice[('+2',)]])),
            [lattice[('+1',)], lattice[('+2',)],
             lattice[('+1', '+sg')], lattice[('+1', '+pl')],
             lattice[('+2', '+sg')], lattice[('+2', '+pl')],
             lattice.infimum])

    def test_upset_generalization(self):
        self.assertEqual(list(lattice.upset_generalization(
            [lattice[('+1', '+sg')], lattice[('+2', '+sg')], lattice[('+3', '+sg')]])),
            [lattice[('+1', '+sg')], lattice[('+2', '+sg')], lattice[('+3', '+sg')],
             lattice[('-3', '+sg')], lattice[('-2', '+sg')], lattice[('-1', '+sg')],
             lattice[('+sg',)]])


class TestInfimum(unittest.TestCase):

    def setUp(self):
        self.infimum = lattice.infimum

    def test_minimal(self):
        self.assertEqual(self.infimum.minimal(),
            ('+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl'))
