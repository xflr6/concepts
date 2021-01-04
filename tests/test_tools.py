# test_tools.py

import pytest

from concepts import tools


def test_maximal():
    items = map(frozenset, ((1,), (2,), (3,), (1, 2)))
    assert set(tools.maximal(items)) == {frozenset([3]), frozenset([1, 2])}


def test_dump_json_invalid_path():
    with pytest.raises(TypeError, match=r'path_or_fileobj'):
        tools.dump_json({}, object())


def test_load_json_invalid_path():
    with pytest.raises(TypeError, match=r'path_or_fileobj'):
        tools.load_json(object())


def test_dump_load(path_or_fileobj, encoding, obj={'sp\xe4m': 'eggs'}):
    tools.dump_json(obj, path_or_fileobj, encoding=encoding)
    if hasattr(path_or_fileobj, 'seek'):
        path_or_fileobj.seek(0)

    assert tools.load_json(path_or_fileobj, encoding=encoding) == obj
