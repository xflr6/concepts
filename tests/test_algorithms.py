import pathlib

import pytest

import concepts
from concepts import algorithms
from concepts import formats

BOB_ROSS = pathlib.Path('bob-ross.cxt')

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
    func = getattr(algorithms, 'fcbo_dual' if dual else 'iterconcepts')

    result = iterconcepts = func(context)
    result = (algorithms.ConceptList.frompairs(iterconcepts) if dual else result)

    pairs = list(map(str, result))

    assert pairs == expected


def test_serialize_bob_ross(test_output, bob_ross):
    target = test_output / f'{BOB_ROSS.stem}-serialized.py'
    bob_ross.tofile(str(target), frmat='python-literal')

    Format = formats.Format['python-literal']
    serialized_args = Format.load(target, encoding='utf-8')

    for name in ('objects', 'properties'):
        assert getattr(serialized_args, name) == (serialized_args
                                                  .serialized[name])
    assert serialized_args.lattice is None

    for name in ('objects', 'properties', 'bools'):
        assert getattr(serialized_args, name) == getattr(bob_ross, name)


@pytest.mark.slow
@pytest.mark.no_cover
def test_lattice_bob_ross(test_examples, test_output, stopwatch, bob_ross):
    with stopwatch() as timing:
        lattice = bob_ross.lattice

    assert lattice is not None
    assert len(lattice) == 3_463

    target = test_output / f'{BOB_ROSS.stem}-serialized-lattice.py'
    bob_ross.tofile(str(target), frmat='python-literal')
    result = target.read_text(encoding=ENCODING)

    example = test_examples / target.name
    expected = example.read_text(encoding=ENCODING)

    assert result == expected

    assert timing.duration < 40


@pytest.mark.slow
@pytest.mark.no_cover
@pytest.mark.skip(reason='TODO')
def test_lattice_mushroom(stopwatch, mushroom):
    with stopwatch():
        lattice = mushroom.lattice

    assert lattice is not None

    assert len(lattice) == 238_710


@pytest.mark.slow
@pytest.mark.no_cover
def test_fcbo_mushroom(stopwatch, mushroom):
    with stopwatch() as timing:
        result = algorithms.get_concepts(mushroom)

    assert len(result) == 238_710

    assert timing.duration < 90
