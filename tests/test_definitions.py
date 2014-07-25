# test_definitions.py

import unittest

from concepts.definitions import Definition


class TestBaseDefinition(unittest.TestCase):

    def test_fromfile(self, filename='examples/gewaesser.cxt'):
        d = Definition.fromfile(filename)
        self.assertEqual(d,
            (('Fluss', 'Bach', 'Kanal', 'Graben', 'See', 'Tuempel', 'Teich', 'Becken'),
             ('fliessend', 'stehend', 'natuerlich', 'kuenstlich', 'gross', 'klein'),
             [(True, False, True, False, True, False),
              (True, False, True, False, False, True),
              (True, False, False, True, True, False),
              (True, False, False, True, False, True),
              (False, True, True, False, True, False),
              (False, True, True, False, False, True),
              (False, True, False, True, True, False),
              (False, True, False, True, False, True)]))


class TestInit(unittest.TestCase):

    def test_duplicate_object(self):
        with self.assertRaisesRegexp(ValueError, 'duplicate objects'):
            Definition(('spam', 'spam'), (), [])

    def test_duplicate_property(self):
        with self.assertRaisesRegexp(ValueError, 'duplicate properties'):
            Definition((), ('spam', 'spam'), [])


class TestDefinition(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.definition = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])

    @classmethod
    def tearDownClass(cls):
        del cls.definition

    def test_unicode(self):
        assert all(ord(c) < 128 for c in str(self.definition))
        self.assertEqual(u'%s' % self.definition, '%s' % self.definition)

    def test_ne(self):
        self.assertFalse(self.definition != self.definition)

    def test_getitem_int(self):
        self.assertEqual(self.definition[0], self.definition.objects)
        self.assertEqual(self.definition[1], self.definition.properties)
        self.assertEqual(self.definition[2], self.definition.bools)

    def test_getitem(self):
        self.assertEqual(self.definition['spam', 'ni'], True)
        with self.assertRaises(KeyError):
            self.definition['ham', 'spam']

    def test_setitem_int(self):
        with self.assertRaises(ValueError):
            self.definition[0] = ('spam',)


class TestUnion(unittest.TestCase):

    def test_compatible(self):
        a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
        b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, True)])
        self.assertEqual(a.union(b),
            Definition(('spam', 'eggs', 'ham'), ('ni', 'nini'),
                [(True, False), (False, False), (True, True)]))

    def test_conflicting(self):
        a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
        b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, False)])
        with self.assertRaisesRegexp(ValueError, "\[\('spam', 'ni'\)\]"):
            a.union(b)

    def test_ignoring(self):
        a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
        b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, False)])
        self.assertEqual(a.union(b, ignore_conflicts=True),
            Definition(('spam', 'eggs', 'ham'), ('ni', 'nini'),
                [(True, False), (False, False), (True, True)]))

    def test_augmented(self):
        a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
        b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, True)])
        a |= b
        self.assertEqual(a,
            Definition(('spam', 'eggs', 'ham'), ('ni', 'nini'),
                [(True, False), (False, False), (True, True)]))


class TestIntersection(unittest.TestCase):

    def test_compatible(self):
        a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
        b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, True)])
        self.assertEqual(a.intersection(b),
            Definition(['spam'], ['ni'], [(True,)]))

    def test_conflicting(self):
        a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
        b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, False)])
        with self.assertRaisesRegexp(ValueError, "\[\('spam', 'ni'\)\]"):
            a.intersection(b)

    def test_ignoring(self):
        a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
        b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, False)])
        self.assertEqual(a.intersection(b, ignore_conflicts=True),
            Definition(['spam'], ['ni'], [(False,)]))

    def test_augmented(self):
        a = Definition(('spam', 'eggs'), ('ni',), [(True,), (False,)])
        b = Definition(('ham', 'spam'), ('nini', 'ni',), [(True, True), (False, True)])
        a &= b
        self.assertEqual(a,
            Definition(['spam'], ['ni'], [(True,)]))
        
