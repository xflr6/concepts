# test_matrices.py

import unittest

from concepts.matrices import Relation


class TestVectors(unittest.TestCase):

    xname = 'Condition'
    yname = 'Symbol'
    xmembers = 'TT', 'TF', 'FT', 'FF'
    ymembers = '->', '<-'
    xbools = [(True, False, True, True), (True, True, False, True)]

    @classmethod
    def setUpClass(cls):
        cls.relation = Relation(cls.xname, cls.yname, cls.xmembers, cls.ymembers, cls.xbools)

    def test_pair_with(self):
        vx, vy = self.relation
        with self.assertRaises(RuntimeError):
            vx._pair_with(self.relation, 1, vy)
