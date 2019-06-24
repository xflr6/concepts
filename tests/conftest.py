# conftest.py

import sys

import pytest

import concepts


@pytest.fixture(scope='session')
def py2():
    return sys.version_info.major == 2


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
