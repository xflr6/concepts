# concepts - implement basic formal concept analysis

"""Formal Concept Analysis (FCA) with Python."""

__title__ = 'concepts'
__version__ = '0.6'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE'
__copyright__ = 'Copyright (c) 2013-2014 Sebastian Bank'

from contexts import Context

__all__ = ['Context', 'load_cxt', 'load_csv']


def load_cxt(filename, encoding=None):
    """Load and return formal context from cxt file."""
    return Context.fromfile(filename, 'cxt', encoding)


def load_csv(filename, dialect='excel', encoding='utf8'):
    """Load and return formal context from csv file."""
    return Context.fromfile(filename, 'csv', encoding, dialect=dialect)
