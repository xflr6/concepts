import pathlib
import unittest

import pytest

from concepts import formats

from conftest import TEST_OUTPUT


@pytest.mark.parametrize('name, expected', [
    ('table', formats.Table),
    ('cxt', formats.Cxt),
    ('csv', formats.Csv),
    ('wiki-table', formats.WikiTable),
])
def test_getitem(name, expected):
    assert formats.Format[name] is expected is formats.Format[name.upper()]


def test_getitem_invalid():
    with pytest.raises(KeyError):
        formats.Format['spam']


@pytest.mark.parametrize('filename, expected', [
    ('spam.TXT', 'table'),
    ('spam.cxt', 'cxt'),
    ('spam.spam.csv', 'csv')
])
def test_infer_format(filename, expected):
    assert formats.Format.infer_format(filename) == expected


def test_infer_format_invalid():
    with pytest.raises(ValueError, match=r'filename suffix'):
        formats.Format.infer_format('spam.spam')


class LoadsDumps:

    def test_loads(self):
        try:
            args = self.format.loads(self.result)
        except NotImplementedError:
            pass
        else:
            self.assertSequenceEqual(args.objects, self.objects)
            self.assertSequenceEqual(args.properties, self.properties)
            self.assertSequenceEqual(args.bools, self.bools)

    def test_dumps(self):
        result = self.format.dumps(self.objects, self.properties, self.bools)
        self.assertEqual(result, self.result)

    def test_dump_load(self, outdir=TEST_OUTPUT):
        extension = getattr(self.format, 'extension', '.txt')
        filepath = (outdir / self.__class__.__name__).with_suffix(extension)
        self.format.dump(str(filepath),
                         self.objects, self.properties, self.bools,
                         encoding=self.encoding)

        try:
            args = self.format.load(filepath, encoding=self.encoding)
        except NotImplementedError:
            pass
        else:
            self.assertSequenceEqual(args.objects, self.objects)
            self.assertSequenceEqual(args.properties, self.properties)
            self.assertSequenceEqual(args.bools, self.bools)


class Ascii(LoadsDumps):

    objects = ('Cheddar', 'Limburger')

    properties = ('in_stock', 'sold_out')

    bools = [(False, True), (False, True)]

    encoding = None


class Unicode(LoadsDumps):

    objects = ('M\xf8\xf8se', 'Llama')

    properties = ('majestic', 'bites')

    bools = [(True, True), (False, False)]

    encoding = 'utf-8'


class TestCxtAscii(unittest.TestCase, Ascii):

    format = formats.Cxt

    result = '''\
B

2
2

Cheddar
Limburger
in_stock
sold_out
.X
.X
'''


class TextCxtUnicode(unittest.TestCase, Unicode):

    format = formats.Cxt

    result = '''\
B

2
2

Møøse
Llama
majestic
bites
XX
..
'''


class TestTableAscii(unittest.TestCase, Ascii):

    format = formats.Table

    result = '''\
         |in_stock|sold_out|
Cheddar  |        |X       |
Limburger|        |X       |'''


class TestTableUnicode(unittest.TestCase, Unicode):

    format =formats.Table

    result = '''\
     |majestic|bites|
Møøse|X       |X    |
Llama|        |     |'''


class TestCsvAscii(unittest.TestCase, Ascii):

    format = formats.Csv

    result = '''\
,in_stock,sold_out\r
Cheddar,,X\r
Limburger,,X\r
'''

class TestCsvUnicode(unittest.TestCase, Unicode):

    format = formats.Csv

    result = '''\
,majestic,bites\r
Møøse,X,X\r
Llama,,\r
'''


class TestWikitableAscii(unittest.TestCase, Ascii):

    format = formats.WikiTable

    result = '''\
{| class="featuresystem"
!
!in_stock!!sold_out
|-
!Cheddar
|        ||X       
|-
!Limburger
|        ||X       
|}'''


class TestWikitableUnicode(unittest.TestCase, Unicode):

    format = formats.WikiTable

    result = '''\
{| class="featuresystem"
!
!majestic!!bites
|-
!Møøse
|X       ||X    
|-
!Llama
|        ||     
|}'''


class TestPythonLiteral(unittest.TestCase, Ascii):

    format = formats.PythonLiteral

    result = '''\
{
  'objects': (
    'Cheddar', 'Limburger',
  ),
  'properties': (
    'in_stock', 'sold_out',
  ),
  'context': [
    (1,),
    (1,),
  ],
}
'''
