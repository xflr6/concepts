import pytest

from concepts import tools


def test_maximal():
    items = map(frozenset, ((1,), (2,), (3,), (1, 2)))
    assert set(tools.maximal(items)) == {frozenset([3]), frozenset([1, 2])}


def test_sha256sum(tmp_path):
    filepath = tmp_path / 'spam.txt'
    filepath.write_text('spam', encoding='ascii')

    result = tools.sha256sum(filepath)

    assert result == '4e388ab32b10dc8dbc7e28144f552830adc74787c1e2c0824032078a79f227fb'


def test_write_lines(tmp_path):
    filepath = tmp_path / 'spam.txt'

    tools.write_lines(filepath, ['spam'])

    assert filepath.read_text(encoding='ascii') == 'spam\n'


def test_write_csv(tmp_path):
    filepath = tmp_path / 'spam.csv'

    tools.write_csv(filepath, [('spam',)], header=['name'])

    assert filepath.read_text(encoding='ascii') == ('name\n'
                                                    'spam\n')


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
