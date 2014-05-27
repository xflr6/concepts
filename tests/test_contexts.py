# test_contexts.py

import unittest

from concepts.contexts import Context


class TestContextInit(unittest.TestCase):

    def test_duplicate_object(self):
        with self.assertRaises(ValueError):
            Context(('spam', 'spam'), ('ham', 'eggs'),
                [(True, False), (False, True)])

    def test_duplicate_property(self):
        with self.assertRaises(ValueError):
            Context(('spam', 'eggs'), ('ham', 'ham'),
                [(True, False), (False, True)])

    def test_object_property_overlap(self):
        with self.assertRaises(ValueError):
            Context(('spam', 'eggs'), ('eggs', 'ham'),
                [(True, False), (False, True)])

    def test_empty_relation(self):
        with self.assertRaises(ValueError):
            Context((), ('spam',), [(False,)])
        with self.assertRaises(ValueError):
            Context(('spam',), (), [(False,)])

    def test_invalid_bools(self):
        with self.assertRaises(ValueError):
            Context(('spam', 'eggs'), ('camelot', 'launcelot'),
                [(True, False)])
        with self.assertRaises(ValueError):
            Context(('spam', 'eggs'), ('camelot', 'launcelot'),
                [(True, False, False), (False, True)])

    def test_init(self):
        c = Context(('spam', 'eggs'), ('camelot', 'launcelot'),
            [(True, False), (False, True)])
        self.assertEqual(c.objects, ('spam', 'eggs'))
        self.assertEqual(c.properties, ('camelot', 'launcelot'))
        self.assertEqual(c.bools, [(True, False), (False, True)])


class TestContext(unittest.TestCase):

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
        cls.context = Context.fromstring(source)

    @classmethod
    def tearDownClass(cls):
        del cls.context

    def test_eq(self):
        self.assertTrue(self.context ==
            Context(self.context.objects, self.context.properties,
                self.context.bools))

    def test_eq_invalid(self):
        with self.assertRaises(TypeError):
            self.context == object()

    def test_ne(self):
        self.assertTrue(self.context !=
            Context(('spam', 'eggs'), ('camelot', 'launcelot'),
                [(True, False), (False, True)]))

    def test_minimize_infimum(self):
        self.assertEqual(list(self.context._minimize((), self.context.properties)),
            [self.context.properties])
