import pathlib
import time

import pytest

import concepts

ENCODING = 'utf-8'


def test_fcbo_mushroom(test_output, test_examples, filename='bob_ross.cxt'):
    filename = pathlib.Path(filename)
    source = test_examples / filename

    print(concepts)
    context = concepts.load_cxt(str(source))

    assert len(context.objects) == 403
    assert len(context.properties) == 67

    start = time.perf_counter()
    lattice = context.lattice

    duration = time.perf_counter() - start
    print(duration)

    assert lattice is not None

    assert len(lattice) == 3_463

    target = test_output / f'{filename.stem}-serialized.py'
    context.tofile(str(target), frmat='pythonliteral')
    result = target.read_text(encoding=ENCODING)

    example = test_examples / target.name
    expected = example.read_text(encoding=ENCODING)

    assert result == expected

    assert duration < 60
