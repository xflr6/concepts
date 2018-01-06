# _compat.py - Python 2/3 compatibility

import sys

PY2 = sys.version_info.major == 2


if PY2:
    text_type = unicode
    string_types = basestring

    from itertools import imap as map, izip as zip, ifilter as filter

    def py3_unicode_to_str(cls):
        return cls

    try:
        from cStringIO import StringIO as _cStringIO
    except ImportError:  # pragma: no cover
        from StringIO import StringIO
    else:
        from StringIO import StringIO as _PureStringIO
        def StringIO(*args):
            if args and isinstance(args[0], str):
                return _cStringIO(*args)
            return _PureStringIO(*args)

    import copy_reg as copyreg


else:
    text_type = string_types = str

    map, zip, filter = map, zip, filter

    def py3_unicode_to_str(cls):
        cls.__str__ = cls.__unicode__
        del cls.__unicode__
        return cls

    from io import StringIO

    import copyreg


def with_metaclass(meta, *bases):
    """From Jinja2 (BSD licensed).

    https://github.com/mitsuhiko/jinja2/blob/master/jinja2/_compat.py
    """
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})
