# concepts - implement basic formal concept analysis

"""Formal Concept Analysis (FCA) with Python.

formats
    Format
        loads dumps

matrices
    relation

contexts
    Context
        from_string to_string
        objects properties
        intension extension neighbors
        lattice

lattices
    Lattice
        infimum supremum atoms
    Concept
        index extent intent objects properties minimal attributes
        upper_neighbors lower_neighbors
        upset downset atoms
        implies subsumes
        join meet

junctors
    relations
    Orthogonal
        Subcontrary
        Implication Replication
        Equivalent
    Incompatible
        Complement
"""

__title__ = 'concepts'
__version__ = '0.2'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE'
__copyright__ = 'Copyright (c) 2013-2014 Sebastian Bank'

from contexts import Context

__all__ = ['Context']
