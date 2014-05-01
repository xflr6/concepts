# test_matrices.py

import unittest

from concepts.matrices import Relation


class TestVectors(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.relation = Relation('Condition', 'Symbol',
            ('TT', 'TF', 'FT', 'FF'), ('->', '<-'),
            [(True, False, True, True), (True, True, False, True)])

    def test_pair_with(self):
        with self.assertRaises(RuntimeError):
            self.relation[0]._pair_with(self.relation, 1, self.relation[1])
