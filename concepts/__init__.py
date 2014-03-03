# concepts - implement basic formal concept analysis

"""Formal Concept Analysis (FCA) with Python."""

__title__ = 'concepts'
__version__ = '0.6.2'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE'
__copyright__ = 'Copyright (c) 2013-2014 Sebastian Bank'

from contexts import Context

__all__ = ['Context', 'load_cxt', 'load_csv', 'make_context']


def load_cxt(filename, encoding=None):
    """Load and return formal context from cxt file."""
    return Context.fromfile(filename, 'cxt', encoding)


def load_csv(filename, dialect='excel', encoding='utf8'):
    """Load and return formal context from csv file."""
    return Context.fromfile(filename, 'csv', encoding, dialect=dialect)


def make_context(source, frmat='table'):
    """Return a new context from source string in the given format.

    >>> c = make_context('''
    ...      |male|female|adult|child|
    ... man  |  X |      |  X  |     |
    ... woman|    |   X  |  X  |     |
    ... boy  |  X |      |     |  X  |
    ... girl |    |   X  |     |  X  |
    ... ''')

    >>> c  # doctest: +ELLIPSIS
    <Context object mapping 4 objects to 4 properties at 0x...>
    """
    return Context.fromstring(source, frmat=frmat)
