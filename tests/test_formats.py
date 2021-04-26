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


@pytest.mark.parametrize('source, kwargs', [
    ('''\
cheese,in_stock,sold_out\r
Cheddar,0,1\r
Limburger,0,1\r
''', {}),
    ('''\
cheese,in_stock,sold_out\r
Cheddar,,X\r
Limburger,,X\r
''', {})])
def test_csv_loads_auto_as_int(source, kwargs):
    args = formats.Csv.loads(source, **kwargs)

    assert args.objects == ['Cheddar', 'Limburger']
    assert args.properties == ['in_stock', 'sold_out']
    assert args.bools ==  [(False, True), (False, True)]


@pytest.mark.parametrize('source, expected, match', [
    ('''\
cheese,in_stock,sold_out\r
Cheddar,0,\r
Limburger,0,1\r
''', ValueError, r''),
    ('''\
cheese,in_stock,sold_out\r
Cheddar,0,1\r
Limburger,X,1\r
''', KeyError, r'')])
def test_csv_loads_auto_as_int_invalid(source, expected, match):
    with pytest.raises(expected, match=match):
        result = formats.Csv.loads(source)


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
}'''


class TestFimi(unittest.TestCase, Ascii):

    format = formats.Fimi

    result = '''\
1
1
'''


@pytest.mark.parametrize('frmat, label, kwargs, expected', [
    ('table', None, {}, '''\
   |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
1sg|X |  |  |X |  |X |X  |   |   |X  |
1pl|X |  |  |X |  |X |   |X  |X  |   |
2sg|  |X |X |  |  |X |X  |   |   |X  |
2pl|  |X |X |  |  |X |   |X  |X  |   |
3sg|  |X |  |X |X |  |X  |   |   |X  |
3pl|  |X |  |X |X |  |   |X  |X  |   |
'''),
    ('cxt', None, {}, '''\
B

6
10

1sg
1pl
2sg
2pl
3sg
3pl
+1
-1
+2
-2
+3
-3
+sg
+pl
-sg
-pl
X..X.XX..X
X..X.X.XX.
.XX..XX..X
.XX..X.XX.
.X.XX.X..X
.X.XX..XX.
'''),
    ('python-literal', 'literal', {}, '''\
{
  'objects': (
    '1sg', '1pl', '2sg', '2pl', '3sg', '3pl',
  ),
  'properties': (
    '+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl',
  ),
  'context': [
    (0, 3, 5, 6, 9),
    (0, 3, 5, 7, 8),
    (1, 2, 5, 6, 9),
    (1, 2, 5, 7, 8),
    (1, 3, 4, 6, 9),
    (1, 3, 4, 7, 8),
  ],
}
'''),
    ('csv', 'str', {'bools_as_int': False}, '''\
,+1,-1,+2,-2,+3,-3,+sg,+pl,-sg,-pl
1sg,X,,,X,,X,X,,,X
1pl,X,,,X,,X,,X,X,
2sg,,X,X,,,X,X,,,X
2pl,,X,X,,,X,,X,X,
3sg,,X,,X,X,,X,,,X
3pl,,X,,X,X,,,X,X,
'''),
    ('csv', 'int', {'bools_as_int': True}, '''\
,+1,-1,+2,-2,+3,-3,+sg,+pl,-sg,-pl
1sg,1,0,0,1,0,1,1,0,0,1
1pl,1,0,0,1,0,1,0,1,1,0
2sg,0,1,1,0,0,1,1,0,0,1
2pl,0,1,1,0,0,1,0,1,1,0
3sg,0,1,0,1,1,0,1,0,0,1
3pl,0,1,0,1,1,0,0,1,1,0
'''),
    ('fimi', None, {}, '''\
0 3 5 6 9
0 3 5 7 8
1 2 5 6 9
1 2 5 7 8
1 3 4 6 9
1 3 4 7 8
'''),
    ( 'wiki-table', 'wiki-table', {}, '''\
{| class="featuresystem"
!
!+1!!-1!!+2!!-2!!+3!!-3!!+sg!!+pl!!-sg!!-pl
|-
!1sg
|X ||  ||  ||X ||  ||X ||X  ||   ||   ||X  
|-
!1pl
|X ||  ||  ||X ||  ||X ||   ||X  ||X  ||   
|-
!2sg
|  ||X ||X ||  ||  ||X ||X  ||   ||   ||X  
|-
!2pl
|  ||X ||X ||  ||  ||X ||   ||X  ||X  ||   
|-
!3sg
|  ||X ||  ||X ||X ||  ||X  ||   ||   ||X  
|-
!3pl
|  ||X ||  ||X ||X ||  ||   ||X  ||X  ||   
|}
''')])
def test_write_example(test_output, context, frmat, label, kwargs, expected):
    Format = formats.Format[frmat]

    flag = f'-{label}' if label else ''

    suffix = getattr(Format, 'suffix', '.txt')
    target = test_output / f'example{flag}{suffix}'

    result = write_format(target,
                          context.objects, context.properties, context.bools,
                          Format=Format, **kwargs)

    assert result == expected

    try:
        reloaded = Format.load(target, encoding=Format.encoding, **kwargs)
    except NotImplementedError:
        pytest.skip('not implemented')


def write_format(target, objects, properties, bools, *, Format, **kwargs):
    Format.dump(str(target),
                objects, properties, bools,
                encoding=Format.encoding, **kwargs)

    assert target.exists()
    assert target.stat().st_size

    result = target.read_text(encoding=Format.encoding)

    return result


@pytest.mark.parametrize('extents, label, expected', [
    ( False, 'intents', '''\
0 1 2 3 4 5 6 7 8 9
0 3 5 6 9
0 3 5 7 8
1 2 5 6 9
1 2 5 7 8
1 3 4 6 9
1 3 4 7 8
0 3 5
5 6 9
3 6 9
5 7 8
3 7 8
1 2 5
1 6 9
1 7 8
1 3 4
6 9
7 8
5
3
1

'''),
    (True, 'extents', '''\

0
1
2
3
4
5
0 1
0 2
0 4
1 3
1 5
2 3
2 4
3 5
4 5
0 2 4
1 3 5
0 1 2 3
0 1 4 5
2 3 4 5
0 1 2 3 4 5
''')])
def test_write_example_concepts_dat(test_output, context, extents, label, expected):
    context = context.copy()

    Format = formats.Format['fimi']

    target = test_output / f'example-{label}.dat'
    iterconcepts = ((c._extent, c._intent) for c in context.lattice)
    
    formats.write_concepts_dat(target, iterconcepts, extents=extents)

    assert target.exists()
    assert target.stat().st_size

    result = target.read_text(encoding=Format.encoding)

    assert result == expected
