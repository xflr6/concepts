# concepts - implement basic formal concept analysis

"""Formal Concept Analysis (FCA) with Python."""

from .contexts import Context
from .definitions import Definition

__all__ = [
    'Context', 'Definition',
    'load', 'load_cxt', 'load_csv',
    'make_context',
]

__title__ = 'concepts'
__version__ = '0.9.2'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE.txt'
__copyright__ = 'Copyright (c) 2013-2020 Sebastian Bank'

EXAMPLE = '''
   |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
1sg| X|  |  | X|  | X|  X|   |   |  X|
1pl| X|  |  | X|  | X|   |  X|  X|   |
2sg|  | X| X|  |  | X|  X|   |   |  X|
2pl|  | X| X|  |  | X|   |  X|  X|   |
3sg|  | X|  | X| X|  |  X|   |   |  X|
3pl|  | X|  | X| X|  |   |  X|  X|   |
'''


def load(filename, encoding='utf-8', frmat=None):
    """Load and return formal context from file.

    Args:
        filename: Path to the file to load the context from.
        encoding (str): Encoding of the file (``'utf-8'``, ``'latin1'``, ``'ascii'``, ...).
        frmat (str): Format of the file (``'table'``, ``'cxt'``, ``'csv'``).
                     If ``None`` (default), infer ``frmat`` from ``filename`` suffix.

    Returns:
        Context: New :class:`.Context` instance.

    Example:
        >>> load('examples/liveinwater.txt')  # doctest: +ELLIPSIS
        <Context object mapping 8 objects to 9 properties [b1e86589] at 0x...>
    """
    return Context.fromfile(filename, frmat, encoding)


def load_cxt(filename, encoding=None):
    """Load and return formal context from CXT file.

    Args:
        filename: Path to the CXT file to load the context from.
        encoding (str): Encoding of the file (``'utf-8'``, ``'latin1'``, ``'ascii'``, ...).

    Returns:
        Context: New :class:`.Context` instance.

    Example:
        >>> load_cxt('examples/digits.cxt')  # doctest: +ELLIPSIS
        <Context object mapping 10 objects to 7 properties [51e571e6] at 0x...>
    """
    return Context.fromfile(filename, 'cxt', encoding)


def load_csv(filename, dialect='excel', encoding='utf-8'):
    """Load and return formal context from CSV file.

    Args:
        filename: Path to the CSV file to load the context from.
        dialect: Syntax variant of the CSV file (``'excel'``, ``'excel-tab'``).
        encoding (str): Encoding of the file (``'utf-8'``, ``'latin1'``, ``'ascii'``, ...).

    Returns:
        Context: New :class:`.Context` instance.

    Example:
        >>> load_csv('examples/vowels.csv')  # doctest: +ELLIPSIS
        <Context object mapping 12 objects to 8 properties [a717eee4] at 0x...>
    """
    return Context.fromfile(filename, 'csv', encoding, dialect=dialect)


def make_context(source, frmat='table'):
    """Return a new context from source string in the given format.

    Args:
        source (str): Formal context table as plain-text string.
        frmat (str): Format of the context string (``'table'``, ``'cxt'``, ``'csv'``).

    Returns:
        Context: New :class:`.Context` instance.

    Example:
        >>> make_context('''
        ...      |male|female|adult|child|
        ... man  |  X |      |  X  |     |
        ... woman|    |   X  |  X  |     |
        ... boy  |  X |      |     |  X  |
        ... girl |    |   X  |     |  X  |
        ... ''')  # doctest: +ELLIPSIS
        <Context object mapping 4 objects to 4 properties [65aa9782] at 0x...>
    """
    return Context.fromstring(source, frmat=frmat)
