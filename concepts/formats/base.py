"""Parse and serialize FCA formal contexts in different formats."""

import io
import os
from typing import NamedTuple, TypeAlias

from .. import tools

__all__ = ['ContextArgs', 'SerializedArgs',
           'Format']


class ContextArgs(NamedTuple):
    """Return value of ``.loads()`` and ``.load()``."""

    objects: list[str]

    properties: list[str]

    bools: list[tuple[bool, ...]]

    serialized: 'SerializedArgs | None' = None


LatticeType: TypeAlias = list[tuple[tuple[int, ...],
                                    tuple[int, ...],
                                    tuple[int, ...],
                                    tuple[int, ...]]]


class SerializedArgs(ContextArgs):

    lattice: LatticeType | None = None


class FormatMeta(type):
    """Collect and retrieve concrete ``Format`` subclasses by name."""

    _map = {}

    by_suffix = {}

    def __init__(self, name, bases, dct):  # noqa: N804
        if not dct.get('__abstract__'):
            if 'name' not in dct:
                self.name = tools.snakify(name, sep='-')
            if 'suffix' in dct:
                self.by_suffix[self.suffix] = self.name
            self._map[self.name] = self
            if 'aliases' in dct:
                self._map.update(dict.fromkeys(dct['aliases'], self))

    def __getitem__(self, name):  # noqa: N804
        try:
            return self._map[name.lower()]
        except KeyError:
            raise KeyError(f'{self!r} unknown format: {name!r}')

    def infer_format(self, filename, frmat=None):  # noqa: N804
        _, suffix = os.path.splitext(filename)
        try:
            return self.by_suffix[suffix.lower()]
        except KeyError:
            raise ValueError('cannot infer file format from filename suffix'
                             f' {suffix!r}, please specify ``frmat``')


class Format(metaclass=FormatMeta):
    """Parse and serialize formal contexts in a specific string format."""

    __abstract__ = True

    encoding = None

    newline = None

    dumps_rstrip = None

    @classmethod
    def load(cls, filename, encoding, **kwargs) -> ContextArgs:
        """Load and parse serialized objects, properties, bools from file."""
        if encoding is None:
            encoding = cls.encoding

        with open(filename, encoding=encoding, newline=cls.newline) as f:
            return cls.loadf(f, **kwargs)

    @classmethod
    def loads(cls, source, **kwargs) -> ContextArgs:
        """Parse source string and return ``ContextArgs``."""
        with io.StringIO(source) as buf:
            return cls.loadf(buf, **kwargs)

    @classmethod
    def dump(cls, filename, objects, properties, bools,
             *, encoding: str | None, _serialized=None, **kwargs):
        """Write serialized objects, properties, bools to file."""
        if encoding is None:
            encoding = cls.encoding

        with open(filename, 'w', encoding=encoding, newline=cls.newline) as f:
            cls.dumpf(f, objects, properties, bools, _serialized=_serialized,
                      **kwargs)

    @classmethod
    def dumps(cls, objects, properties, bools, _serialized=None, **kwargs):
        with io.StringIO(newline=cls.newline) as buf:
            cls.dumpf(buf, objects, properties, bools, _serialized=_serialized,
                      **kwargs)
            source = buf.getvalue()
        if cls.dumps_rstrip:
            source = source.rstrip()
        return source

    @staticmethod
    def loadf(file, **kwargs) -> ContextArgs:
        """Parse file-like object and return ``ContextArgs``."""
        raise NotImplementedError  # pragma: no cover

    @staticmethod
    def dumpf(file, objects, properties, bools, *, _serialized=None, **kwargs):
        """Serialize ``(objects, properties, bools)`` into file-like object."""
        raise NotImplementedError  # pragma: no cover
