# test_formats.py

import unittest

from concepts.formats import Format, Cxt, Table, Csv, WikiTable


class LoadsDumpsAscii(object):

    input_ascii = (('Cheddar', 'Limburger'), ('in_stock', 'sold_out'),
        [(False, True), (False, True)])

    def test_loads_ascii(self):
        o, p, b = self.format.loads(self.result_ascii)
        objects, properties, bools = self.input_ascii
        self.assertSequenceEqual(o, objects)
        self.assertSequenceEqual(p, properties)
        self.assertSequenceEqual(b, bools)

    def test_dumps_ascii(self):
        objects, properties, bools = self.input_ascii
        r = self.format.dumps(objects, properties, bools)
        self.assertEqual(r, self.result_ascii)


class LoadsDumpsUnicode(object):

    input_unicode = ((u'M\xf8\xf8se', 'Llama'), ('majestic', 'bites'),
        [(True, True), (False, False)])

    def test_loads_unicode(self):
        o, p, b = self.format.loads(self.result_unicode)
        objects, properties, bools = self.input_unicode
        self.assertSequenceEqual(o, objects)
        self.assertSequenceEqual(p, properties)
        self.assertSequenceEqual(b, bools)

    def test_dumps_unicode(self):
        objects, properties, bools = self.input_unicode
        r = self.format.dumps(objects, properties, bools)
        self.assertEqual(r, self.result_unicode)


class TestFormat(unittest.TestCase):

    def test_getitem(self):
        self.assertEqual(Format['cxt'], Cxt)
        self.assertEqual(Format['table'], Table)
        self.assertEqual(Format['csv'], Csv)
        self.assertEqual(Format['wikitable'], WikiTable)
        with self.assertRaises(KeyError):
            Format['spam']


class TestCxt(unittest.TestCase, LoadsDumpsAscii, LoadsDumpsUnicode):

    format = Cxt

    result_ascii = 'B\n\n2\n2\n\nCheddar\nLimburger\nin_stock\nsold_out\n.X\n.X\n'

    result_unicode = u'B\n\n2\n2\n\nM\xf8\xf8se\nLlama\nmajestic\nbites\nXX\n..\n'


class TestTable(unittest.TestCase, LoadsDumpsAscii, LoadsDumpsUnicode):

    format = Table

    result_ascii = (
        '         |in_stock|sold_out|\n'
        'Cheddar  |        |X       |\n'
        'Limburger|        |X       |')

    result_unicode = (
        u'     |majestic|bites|\n'
        u'M\xf8\xf8se|X       |X    |\n'
        u'Llama|        |     |')


class TestCsv(unittest.TestCase, LoadsDumpsAscii, LoadsDumpsUnicode):

    format = Csv

    result_ascii = (
        ',in_stock,sold_out\r\n'
        'Cheddar,,X\r\n'
        'Limburger,,X\r\n')

    result_unicode = (
        u',majestic,bites\r\n'
        u'M\xf8\xf8se,X,X\r\n'
        u'Llama,,\r\n')

    @unittest.skip('TODO')
    def test_loads_unicode(self):
        pass


class TestWikitable(unittest.TestCase, LoadsDumpsAscii, LoadsDumpsUnicode):

    format = WikiTable

    result_ascii = (
        '{| class="featuresystem"\n'
        '!\n'
        '!in_stock!!sold_out\n'
        '|-\n'
        '!Cheddar\n'
        '|        ||X       \n'
        '|-\n'
        '!Limburger\n'
        '|        ||X       \n'
        '|}')

    result_unicode = (
        u'{| class="featuresystem"\n'
        u'!\n'
        u'!majestic!!bites\n'
        u'|-\n'
        u'!M\xf8\xf8se\n|X       ||X    \n'
        u'|-\n'
        u'!Llama\n'
        u'|        ||     \n'
        '|}')

    def test_loads_ascii(self):
        pass

    def test_loads_unicode(self):
        pass
