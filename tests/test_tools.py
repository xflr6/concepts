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


def test_dump_load(path_or_fileobj, encoding, obj={u'sp\xe4m': 'eggs'}):
    f, is_fileobj = path_or_fileobj
    kwargs = {'encoding': encoding} if encoding is not None else {}

    tools.dump_json(obj, f, **kwargs)
    if is_fileobj:
        f.seek(0)

    assert tools.load_json(f, **kwargs) == obj
