# conftest.py

import io
import sys

import pytest

import concepts


@pytest.fixture(scope='session')
def py2():
    return sys.version_info.major == 2


@pytest.fixture(scope='session')
def make_stringio(py2):
    return io.BytesIO if py2 else io.StringIO


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
def path_or_fileobj(request, tmp_path, make_stringio, filename='context.json'):
    if request.param == 'str':
        yield u'%s' % (tmp_path / filename)
    elif request.param == 'bytes':
        yield str(tmp_path / filename).encode('ascii')
    elif request.param == 'pathlike':
        yield tmp_path / filename
    elif request.param == 'fileobj':
        with make_stringio() as f:
            yield f
    else:
        raise RuntimeError


@pytest.fixture(params=['utf-8', None])
def encoding(request):
    return request.param
