import pathlib

import pytest

import concepts
from concepts import algorithms

BOB_ROSS = pathlib.Path('bob_ross.cxt')

ENCODING = 'utf-8'


def test_lattice(lattice):
    pairs = [f'{x._extent.bits()} <-> {x._intent.bits()}' for x in lattice]

    assert pairs == ['000000 <-> 1111111111',
                     '100000 <-> 1001011001',
                     '010000 <-> 1001010110',
                     '001000 <-> 0110011001',
                     '000100 <-> 0110010110',
                     '000010 <-> 0101101001',
                     '000001 <-> 0101100110',
                     '110000 <-> 1001010000',
                     '101000 <-> 0000011001',
                     '100010 <-> 0001001001',
                     '010100 <-> 0000010110',
                     '010001 <-> 0001000110',
                     '001100 <-> 0110010000',
                     '001010 <-> 0100001001',
                     '000101 <-> 0100000110',
                     '000011 <-> 0101100000',
                     '101010 <-> 0000001001',
                     '010101 <-> 0000000110',
                     '111100 <-> 0000010000',
                     '110011 <-> 0001000000',
                     '001111 <-> 0100000000',
                     '111111 <-> 0000000000']


@pytest.mark.parametrize('dual, expected', [
    (False, ['111111 <-> 0000000000',
             '110000 <-> 1001010000',
             '000000 <-> 1111111111',
             '100000 <-> 1001011001',
             '010000 <-> 1001010110',
             '001111 <-> 0100000000',
             '001100 <-> 0110010000',
             '001000 <-> 0110011001',
             '000100 <-> 0110010110',
             '000011 <-> 0101100000',
             '000010 <-> 0101101001',
             '000001 <-> 0101100110',
             '001010 <-> 0100001001',
             '000101 <-> 0100000110',
             '110011 <-> 0001000000',
             '100010 <-> 0001001001',
             '010001 <-> 0001000110',
             '111100 <-> 0000010000',
             '101000 <-> 0000011001',
             '010100 <-> 0000010110',
             '101010 <-> 0000001001',
             '010101 <-> 0000000110']),
    (True, ['000000 <-> 1111111111',
            '100000 <-> 1001011001',
            '110000 <-> 1001010000',
            '111100 <-> 0000010000',
            '111111 <-> 0000000000',
            '110011 <-> 0001000000',
            '101000 <-> 0000011001',
            '101010 <-> 0000001001',
            '100010 <-> 0001001001',
            '010000 <-> 1001010110',
            '010100 <-> 0000010110',
            '010101 <-> 0000000110',
            '010001 <-> 0001000110',
            '001000 <-> 0110011001',
            '001100 <-> 0110010000',
            '001111 <-> 0100000000',
            '001010 <-> 0100001001',
            '000100 <-> 0110010110',
            '000101 <-> 0100000110',
            '000010 <-> 0101101001',
            '000011 <-> 0101100000',
            '000001 <-> 0101100110']),
])
def test_fcbo(context, dual, expected):
    func = getattr(algorithms, 'fcbo_dual' if dual else 'fcbo')

    result = list(func(context))

    pairs = [f'{extent.bits()} <-> {intent.bits()}'
             for extent, intent in result]

    assert pairs == expected


@pytest.mark.parametrize('dual, expected', [
    (False, [('ABCD', ''),
             ('ABC',  '0'),
             ('AC',   '01'),
             ('A',    '012'),
             ('',     '012345'),
             ('C',    '014'),
             ('AB',   '02'),
             ('B',    '02345'),
             ('BC',   '04'),
             ('ACD',  '1'),
             ('AD',   '12'),
             ('ABD',  '2')]),
    (True, [('',     '012345'),
            ('A',    '012'),
            ('AB',   '02'),
            ('ABC',  '0'),
            ('ABCD', ''),
            ('ABD',  '2'),
            ('AC',   '01'),
            ('ACD',  '1'),
            ('AD',   '12'),
            ('B',    '02345'),
            ('BC',   '04'),
            ('C',    '014')]),
])
def test_fcbo_example(dual, expected):
    source = (' |0|1|2|3|4|5|\n'
              'A|X|X|X| | | |\n'
              'B|X| |X|X|X|X|\n'
              'C|X|X| | |X| |\n'
              'D| |X|X| | | |\n')

    context = concepts.make_context(source)

    assert context.objects == ('A', 'B', 'C', 'D')
    assert context.properties == ('0', '1', '2', '3', '4', '5')

    func = getattr(algorithms, 'fcbo_dual' if dual else 'fcbo')

    result = list(func(context))

    assert len(result) == len(expected)

    members = [(''.join(extent.members()), ''.join(intent.members()))
               for extent, intent in result]

    assert set(members) == set(expected)

    assert members == expected


@pytest.fixture
def bob_ross(test_examples, filename=BOB_ROSS):
    path = test_examples / filename

    context = concepts.load_cxt(str(path), encoding=ENCODING)

    assert len(context.objects) == 403
    assert len(context.properties) == 67

    return context


@pytest.mark.slow
def test_lattice_bob_ross(test_examples, test_output, stopwatch, bob_ross):
    with stopwatch() as timing:
        lattice = bob_ross.lattice

    assert lattice is not None
    assert len(lattice) == 3_463

    target = test_output / f'{BOB_ROSS.stem}-serialized.py'
    bob_ross.tofile(str(target), frmat='python-literal')
    result = target.read_text(encoding=ENCODING)

    example = test_examples / target.name
    expected = example.read_text(encoding=ENCODING)

    assert result == expected

    assert timing.duration < 60
