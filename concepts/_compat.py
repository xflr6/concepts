# _compat.py - Python 2/3 compatibility

import io
import json
import locale
import sys

PY2 = (sys.version_info.major == 2)


if PY2:
    text_type = unicode
    string_types = basestring

    from itertools import (imap as map,
                           izip as zip,
                           ifilter as filter)

    def py3_unicode_to_str(cls):
        return cls

    try:
        from cStringIO import StringIO as _cStringIO
    except ImportError:  # pragma: no cover
        from StringIO import StringIO
    else:
        from StringIO import StringIO as _PureStringIO
        def StringIO(*args):  # noqa: N802
            if args and isinstance(args[0], str):
                return _cStringIO(*args)
            return _PureStringIO(*args)

    import copy_reg as copyreg

    from collections import MutableSet

    def json_open(path, mode, encoding=None):
        """Ignore ``encoding`` under Python 2."""
        return open(path, mode)

    def json_path_open(pathobj, mode, encoding=None):
        """Add ``'b'`` to ``mode`` and ignore ``encoding`` under Python 2."""
        return pathobj.open('b' + mode)

    def json_call(funcname, **kwargs):
        """Replace ``enocding=None`` with ``locale.getpreferredencoding()``."""
        if kwargs.get('encoding', object()) is None:
            kwargs['encoding'] = locale.getpreferredencoding()
        return getattr(json, funcname)(**kwargs)


else:
    text_type = string_types = str

    map, zip, filter = map, zip, filter

    def py3_unicode_to_str(cls):
        cls.__str__ = cls.__unicode__
        del cls.__unicode__
        return cls

    from io import StringIO

    import copyreg

    from collections.abc import MutableSet

    json_open = io.open

    def json_path_open(pathobj, mode, encoding=None):
        return pathobj.open(mode, encoding=encoding)

    def json_call(funcname, **kwargs):
        """Ignore ``encoding`` under Python 3."""
        kwargs.pop('encoding', None)
        return getattr(json, funcname)(**kwargs)


def with_metaclass(meta, *bases):
    """From Jinja2 (BSD licensed).

    https://github.com/mitsuhiko/jinja2/blob/master/jinja2/_compat.py
    """
    class metaclass(meta):  # noqa: N801
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})
