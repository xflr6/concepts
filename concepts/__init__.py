# concepts - implement basic formal concept analysis

"""Formal Concept Analysis (FCA) with Python.

matrices
    relation

formats
    Format
        loads dumps

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

relations
    relations
    Orthogonal
        Subcontrary
        Implication Replication
        Equivalent
    Incompatible
        Complement
"""

__title__ = 'concepts'
__version__ = '0.1.2'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE.txt'
__copyright__ = 'Copyright (c) 2013-2014 Sebastian Bank'

from contexts import Context

__all__ = ['Context']
