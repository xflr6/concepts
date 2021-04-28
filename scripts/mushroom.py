#!/usr/bin/env python3

"""Download mushroom data set from UCI and convert to FCA .cxt file."""

import os
import pathlib
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, os.pardir)
import concepts  # noqa: E402
from concepts import formats  # noqa: E402
from concepts import tools  # noqa: E402

BASE = ('https://archive.ics.uci.edu'
        '/ml/machine-learning-databases'
        '/mushroom/')

MUSHROOM = pathlib.Path('agaricus-lepiota')

NAMES = MUSHROOM.with_suffix('.names')

NAMES_SHA256 = '79e440566900901a5900febc1f3c9659e3746e306a5fa1aed4d084a1e4da76fd'

DATA = MUSHROOM.with_suffix('.data')

DATA_SHA256 = 'e65d082030501a3ebcbcd7c9f7c71aa9d28fdfff463bf4cf4716a3fe13ac360e'

ENCODING = 'ascii'

CSV = MUSHROOM.with_suffix('.csv')

CXT = MUSHROOM.with_suffix('.cxt')

DAT = MUSHROOM.with_suffix('.dat')

CXT_MINIMAL = CXT.with_name(f'{CXT.stem}-minimal{CXT.suffix}')

CSV_MINIMAL_STR = CSV.with_name(f'{CSV.stem}-str{CSV.suffix}')

CSV_MINIMAL_INT = CSV.with_name(f'{CSV.stem}-int{CSV.suffix}')

DAT_MINIMAL = DAT.with_name(f'{DAT.stem}-minimal{DAT.suffix}')

RESULTS = (CSV, CXT, DAT,
           CSV_MINIMAL_STR, CSV_MINIMAL_INT, CXT_MINIMAL, DAT_MINIMAL)

ATTRIBUTES = re.compile(r'''
                        ^7\.[ ]Attribute[ ]Information:
                            [ ]\(classes:
                            [ ]edible=e,
                            [ ]poisonous=p\)\n
                        (?P<attributes>.*?\n)
                        \n
                        ''', re.MULTILINE | re.DOTALL | re.VERBOSE)

ATTRIBUTE = re.compile(r'''
                       ^[ ]*
                       \d+\.[ ]
                       (?P<name>[a-z\-]+)
                       \??  # ignore final question mark
                       :[ ]+
                       (?P<values>[a-z]+=[a-z\?]+
                                  (?:,
                                     (?:\n[ ]+)?
                                     [a-z]+=[a-z\?]
                                   )+
                       )
                       \n
                       ''', re.MULTILINE | re.VERBOSE)


def parse_attributes(text):
    section = ATTRIBUTES.search(text).group('attributes')

    def iterattributes(text, *, pos=0):
        for ma in ATTRIBUTE.finditer(text):
            if ma.start() != pos:
                raise RuntimeError(f'unmatched: {text[pos:ma.start()]!r}')

            name, values = ma.group('name', 'values')
            values = [v.partition('=')[::-2]  # abbreviation as key
                      for v in values.replace(',', ' ').strip().split()]
            yield name, dict(values)
            pos = ma.end()

        if ma.end() != len(text):
            raise RuntimeError(f'unmatched: {text[ma.end():]!r}')

    result = {'class': {'e': 'edible', 'p': 'poisonous'}}
    result.update(iterattributes(section))
    return result


def iterproperties(attributes):
    for name, tags in attributes.items():
        for tag in tags.values():
            yield f'{name}:{tag}'


def iterbools(attributes, data):
    for row in data:
        assert len(row) == len(attributes)
        yield [value == tag
               for value, tags in zip(row, attributes.values())
               for tag in tags]


def iter_cxt_lines(attributes, data):
    objects = list(map(str, range(1, len(data) + 1)))
    properties = list(iterproperties(attributes))
    bools = list(iterbools(attributes, data))
    return formats.iter_cxt_lines(objects, properties, bools)


def iterrows(attributes, data):
    for i, bools in enumerate(iterbools(attributes, data), 1):
        yield [i] + list(map(int, bools))


for path, hexdigest in [(NAMES, NAMES_SHA256), (DATA, DATA_SHA256)]:
    if not path.exists():
        url = urllib.parse.urljoin(BASE, path.name)
        print(url)
        urllib.request.urlretrieve(url, path)
        print(path.name, f'{path.stat().st_size:_d} bytes')
        assert path.stat().st_size

    assert tools.sha256sum(path) == hexdigest, f'{tools.sha256sum(path)} != {hexdigest}'

attributes = parse_attributes(NAMES.read_text(encoding=ENCODING))
assert len(attributes) == 23, f'{len(attributes):_d} != 23'

properties = list(iterproperties(attributes))
print(f'{properties!r:}')
assert len(properties) == 128, f'{len(attributes):_d} != 128'

if not all(path.exists() for path in RESULTS):
    data = list(tools.csv_iterrows(DATA))
    assert len(data) == 8_124, f'{len(data):_d} != 8_124'

    tools.write_csv(CSV, iterrows(attributes, data), header=[MUSHROOM.stem] + properties,
                    encoding=ENCODING)
    print(CSV, f'{CSV.stat().st_size:_d} bytes')

    tools.write_lines(CXT, iter_cxt_lines(attributes, data),
                      encoding=ENCODING, newline='\n')
    print(CXT, f'{CXT.stat().st_size:_d} bytes')

    context = concepts.load(str(CXT))
    context.tofile(DAT, frmat='fimi')
    print(DAT, f'{DAT.stat().st_size:_d} bytes')

    definition = concepts.Definition.fromfile(CXT)
    removed = definition.remove_empty_properties()
    assert removed == ['gill-attachment:descending',
                       'gill-attachment:notched',
                       'gill-spacing:distant',
                       'stalk-root:cup',
                       'stalk-root:rhizomorphs',
                       'veil-type:universal',
                       'ring-type:cobwebby',
                       'ring-type:sheathing',
                       'ring-type:zone']

    context = concepts.Context(*definition)
    assert len(context.properties) == 119, f'{len(attributes):_d} != 119'

    context.tofile(CXT_MINIMAL, frmat='cxt')  # examples/mushroom.cxt
    print(CXT_MINIMAL, f'{CXT_MINIMAL.stat().st_size:_d} bytes')

    context.tofile(CSV_MINIMAL_STR, frmat='csv',
                   object_header=MUSHROOM.stem, bools_as_int=False)
    print(CSV_MINIMAL_STR, f'{CSV_MINIMAL_STR.stat().st_size:_d} bytes')

    context.tofile(CSV_MINIMAL_INT, frmat='csv',
                   object_header=MUSHROOM.stem, bools_as_int=True)
    print(CSV_MINIMAL_INT, f'{CSV_MINIMAL_INT.stat().st_size:_d} bytes')

    context.tofile(DAT_MINIMAL, frmat='fimi')
    print(DAT_MINIMAL, f'{DAT_MINIMAL.stat().st_size:_d} bytes')
