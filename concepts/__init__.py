# concepts - implement basic formal concept analysis

"""Formal Concept Analysis (FCA) with Python."""

__title__ = 'concepts'
__version__ = '0.7.10.dev0'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE'
__copyright__ = 'Copyright (c) 2013-2015 Sebastian Bank'

from .contexts import Context
from .definitions import Definition

__all__ = ['Context', 'Definition', 'load_cxt', 'load_csv', 'make_context']

EXAMPLE = '''
   |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
1sg| X|  |  | X|  | X|  X|   |   |  X|
1pl| X|  |  | X|  | X|   |  X|  X|   |
2sg|  | X| X|  |  | X|  X|   |   |  X|
2pl|  | X| X|  |  | X|   |  X|  X|   |
3sg|  | X|  | X| X|  |  X|   |   |  X|
3pl|  | X|  | X| X|  |   |  X|  X|   |
'''


def load_cxt(filename, encoding=None):
    """Load and return formal context from CXT file.

    >>> load_cxt('examples/digits.cxt')  # doctest: +ELLIPSIS
    <Context object mapping 10 objects to 7 properties at 0x...>
    """
    return Context.fromfile(filename, 'cxt', encoding)


def load_csv(filename, dialect='excel', encoding='utf-8'):
    """Load and return formal context from CSV file.

    >>> load_csv('examples/vowels.csv')  # doctest: +ELLIPSIS
    <Context object mapping 12 objects to 8 properties at 0x...>
    """
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
