import contextlib
import pathlib
import time
import types

import pytest

import concepts

BOB_ROSS = pathlib.Path('bob_ross.cxt')

ENCODING = 'utf-8'


@pytest.fixture
def bob_ross(test_examples, filename=BOB_ROSS):
    path = test_examples / filename

    context = concepts.load_cxt(str(path))

    assert len(context.objects) == 403
    assert len(context.properties) == 67

    return context


@contextlib.contextmanager
def stopwatch(*, quiet: bool = False):
    """Context manager that measures and prints the execution wall time."""
    timing = types.SimpleNamespace(start=None, end=None, duration=None)
    timing.start = time.perf_counter()

    yield timing

    timing.end = time.perf_counter()
    timing.duration = timing.end - timing.start

    if not quiet:
        print(timing.duration)


def test_lattice_bob_ross(test_examples, test_output, bob_ross):
    with stopwatch() as timing:
        lattice = bob_ross.lattice

    assert lattice is not None
    assert len(lattice) == 3_463

    target = test_output / f'{BOB_ROSS.stem}-serialized.py'
    bob_ross.tofile(str(target), frmat='pythonliteral')
    result = target.read_text(encoding=ENCODING)

    example = test_examples / target.name
    expected = example.read_text(encoding=ENCODING)

    assert result == expected

    assert timing.duration < 60
