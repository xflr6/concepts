"""pytest command line options and fixtures."""

import contextlib
import io
import pathlib
import time
import types

import pytest

import concepts

TEST_EXAMPLES = pathlib.Path('examples')

TEST_OUTPUT = pathlib.Path('test-output')


def pytest_addoption(parser):
    parser.addoption('--run-slow', action='store_true', default=False,
                     help='run tests that are marked as slow')


def pytest_configure(config):
    config.addinivalue_line('markers',
                            'slow: skip the test (override with --run-slow)')


def pytest_collection_modifyitems(config, items):
    if not config.getoption('--run-slow'):
        skip_slow = pytest.mark.skip(reason='require --run-slow')
        for item in items:
            if 'slow' in item.keywords:
                item.add_marker(skip_slow)


@pytest.fixture(scope='session')
def test_examples(path=TEST_EXAMPLES):
    assert path.exists()
    return path


@pytest.fixture(scope='session')
def test_output(path=TEST_OUTPUT):
    if not path.exists():
        path.mkdir()
    return path


@pytest.fixture(scope='session')
def source():
    return concepts.EXAMPLE


@pytest.fixture(scope='session')
def context(source):
    return concepts.make_context(source)


@pytest.fixture(scope='module')
def lattice(context):
    context = concepts.Context(context.objects, context.properties,
                               context.bools)
    return context.lattice


@pytest.fixture(params=['str', 'bytes', 'pathlike', 'fileobj'])
def path_or_fileobj(request, tmp_path, filename='context.json'):
    if request.param == 'str':
        yield str(tmp_path / filename)
    elif request.param == 'bytes':
        yield str(tmp_path / filename).encode('ascii')
    elif request.param == 'pathlike':
        yield tmp_path / filename
    elif request.param == 'fileobj':
        with io.StringIO() as f:
            yield f
    else:
        raise RuntimeError


@pytest.fixture(params=['utf-8', None])
def encoding(request):
    return request.param


@pytest.fixture
def stopwatch():
    return _stopwatch


@contextlib.contextmanager
def _stopwatch(*, quiet: bool = False):
    """Context manager that measures and prints the execution wall time."""
    timing = types.SimpleNamespace(start=None, end=None, duration=None)
    timing.start = time.perf_counter()

    yield timing

    timing.end = time.perf_counter()
    timing.duration = timing.end - timing.start

    if not quiet:
        print(timing.duration)
