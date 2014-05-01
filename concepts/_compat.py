# _compat.py - Python 2/3 compatibility

import sys

PY2 = sys.version_info[0] == 2


if PY2:  # pragma: no cover
    text_type = unicode

    from itertools import imap as map
    from itertools import izip as zip
    from itertools import ifilter as filter
    from itertools import ifilterfalse as filterfalse

    def py3_unicode_to_str(cls):
        return cls

    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    import copy_reg as copyreg


else:  # pragma: no cover
    text_type = str

    map = map
    zip = zip
    filter = filter
    from itertools import filterfalse

    def py3_unicode_to_str(cls):
        cls.__str__ = cls.__unicode__
        del cls.__unicode__
        return cls

    from io import StringIO

    import copyreg


def with_metaclass(meta, *bases):
    """From Jinja2 (BSD licensed).

    http://github.com/mitsuhiko/jinja2/blob/master/jinja2/_compat.py
    """
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__
        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)
    return metaclass('temporary_class', None, {})
