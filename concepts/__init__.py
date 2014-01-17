# concepts - implement basic formal concept analysis

"""Formal Concept Analysis (FCA) with Python."""

__title__ = 'concepts'
__version__ = '0.2.2'
__author__ = 'Sebastian Bank <sebastian.bank@uni-leipzig.de>'
__license__ = 'MIT, see LICENSE'
__copyright__ = 'Copyright (c) 2013-2014 Sebastian Bank'

from contexts import Context

__all__ = ['Context']


def _test():
    global l
    l = Context.from_string('''
       |+1|-1|+2|-2|+3|-3|+sg|+du|+pl|-sg|-du|-pl|
    1s | X|  |  | X|  | X|  X|   |   |   |  X|  X|
    1de| X|  |  | X|  | X|   |  X|   |  X|   |  X|
    1pe| X|  |  | X|  | X|   |   |  X|  X|  X|   |
    1di| X|  | X|  |  | X|   |  X|   |  X|   |  X|
    1pi| X|  | X|  |  | X|   |   |  X|  X|  X|   |
    2s |  | X| X|  |  | X|  X|   |   |   |  X|  X|
    2d |  | X| X|  |  | X|   |  X|   |  X|   |  X|
    2p |  | X| X|  |  | X|   |   |  X|  X|  X|   |
    3s |  | X|  | X| X|  |  X|   |   |   |  X|  X|
    3d |  | X|  | X| X|  |   |  X|   |  X|   |  X|
    3p |  | X|  | X| X|  |   |   |  X|  X|  X|   |
    ''').lattice
    assert len(l.supremum.lower_neighbors) == 6
    print l

if __name__ == '__main__':
    _test()
