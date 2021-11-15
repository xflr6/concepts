Concepts
========

|PyPI version| |License| |Supported Python| |Format|

|Build| |Codecov| |Readthedocs-stable| |Readthedocs-latest|

Concepts is a simple Python implementation of **Formal Concept Analysis**
(FCA_).

|Logo|

FCA provides a mathematical model for describing a set of **objects** (e.g. King
Arthur, Sir Robin, and the holy grail) with a set of **properties** (e.g. human,
knight, king, and mysterious) which each of the objects either has or not. A
table called *formal context* defines which objects have a given property and
vice versa which properties a given object has.


Links
-----

- GitHub: https://github.com/xflr6/concepts
- PyPI: https://pypi.org/project/concepts/
- Documentation: https://concepts.readthedocs.io
- Changelog: https://concepts.readthedocs.io/en/latest/changelog.html
- Issue Tracker: https://github.com/xflr6/concepts/issues
- Download: https://pypi.org/project/concepts/#files


Installation
------------

This package runs under Python 3.6+, use pip_ to install:

.. code:: bash

    $ pip install concepts

This will also install the bitsets_ and graphviz_ packages from PyPI as
required dependencies.

Rendering lattice graphs depends on the `Graphviz software`_. Make sure its
``dot`` executable is on your systems' path.


Quickstart
----------

Create a **formal context** defining which object has which property, e.g. from
a simple ASCII-art style cross-table with *object* rows and *property* columns
(alternatively load a CXT or CSV file):

.. code:: python

    >>> import concepts
    >>> context = concepts.Context.fromstring('''
    ...            |human|knight|king |mysterious|
    ... King Arthur|  X  |  X   |  X  |          |
    ... Sir Robin  |  X  |  X   |     |          |
    ... holy grail |     |      |     |     X    |
    ... ''')
    >>> context  # doctest: +ELLIPSIS
    <Context object mapping 3 objects to 4 properties [dae7402a] at 0x...>


Query **common properties** of objects or **common objects** of properties
(*derivation*):

.. code:: python

    >>> context.intension(['King Arthur', 'Sir Robin'])
    ('human', 'knight')

    >>> context.extension(['knight', 'mysterious'])
    ()

Get the closest matching **objects-properties pair** of objects or properties
(*formal concepts*):

.. code:: python

    >>> context['Sir Robin', 'holy grail']
    (('King Arthur', 'Sir Robin', 'holy grail'), ())

    >>> context['king',]
    (('King Arthur',), ('human', 'knight', 'king'))

Iterate over the **concept lattice** of all objects-properties pairs:

.. code:: python

    >>> for extent, intent in context.lattice:
    ...     print(extent, intent)
    () ('human', 'knight', 'king', 'mysterious')
    ('King Arthur',) ('human', 'knight', 'king')
    ('holy grail',) ('mysterious',)
    ('King Arthur', 'Sir Robin') ('human', 'knight')
    ('King Arthur', 'Sir Robin', 'holy grail') ()

Make a Graphviz visualization of the lattice (use ``.graphviz(view=True)`` to
directly render it and display the resulting PDF):

.. code:: python

    >>> context.lattice.graphviz()  # doctest: +ELLIPSIS
    <graphviz.graphs.Digraph object at 0x...>

.. image:: https://raw.github.com/xflr6/concepts/master/docs/holy-grail.png
    :align: center


Further reading
---------------

- https://en.wikipedia.org/wiki/Formal_concept_analysis
- http://www.upriss.org.uk/fca/

The generation of the concept lattice is based on the algorithm from C. Lindig.
`Fast Concept Analysis`_. In Gerhard Stumme, editors, Working with Conceptual
Structures - Contributions to ICCS 2000, Shaker Verlag, Aachen, Germany, 2000.

Most of the included example ``CXT`` files are taken from Uta Priss'
`FCA homepage`_.

The ``mushroom`` dataset is converted from the
`UCI Mashine Learning repsitory`_.


See also
--------

The implementation is based on these Python packages:

- bitsets_ |--| Ordered subsets over a predefined domain
- graphviz_ |--| Simple Python interface for Graphviz

The following package is build on top of concepts:

- features_ |--| Feature set algebra for linguistics

If you want to apply FCA to bigger data sets, you might want to consider `other
implementations`_ based on `more sophisticated algorithms`_ like In-Close_
or Fcbo_.


License
-------

Concepts is distributed under the `MIT license`_.


.. _FCA: https://en.wikipedia.org/wiki/Formal_concept_analysis
.. _Fast Concept Analysis: http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.143.948
.. _FCA homepage: http://www.upriss.org.uk/fca/examples.html
.. _UCI Mashine Learning repsitory: https://archive.ics.uci.edu/ml/machine-learning-databases/mushroom/

.. _pip: https://pip.readthedocs.io
.. _Graphviz software: http://www.graphviz.org

.. _bitsets: https://pypi.org/project/bitsets/
.. _graphviz: https://pypi.org/project/graphviz/
.. _features: https://pypi.org/project/features/

.. _other implementations: http://www.upriss.org.uk/fca/fcasoftware.html
.. _more sophisticated algorithms: https://upriss.github.io/fca/fcaalgorithms.html
.. _In-Close: https://sourceforge.net/projects/inclose/
.. _Fcbo: http://fcalgs.sourceforge.net

.. _MIT license: https://opensource.org/licenses/MIT


.. |--| unicode:: U+2013


.. |PyPI version| image:: https://img.shields.io/pypi/v/concepts.svg
    :target: https://pypi.org/project/concepts/
    :alt: Latest PyPI Version
.. |License| image:: https://img.shields.io/pypi/l/concepts.svg
    :target: https://pypi.org/project/concepts/
    :alt: License
.. |Supported Python| image:: https://img.shields.io/pypi/pyversions/concepts.svg
    :target: https://pypi.org/project/concepts/
    :alt: Supported Python Versions
.. |Format| image:: https://img.shields.io/pypi/format/concepts.svg
    :target: https://pypi.org/project/concepts/
    :alt: Format

.. |Build| image:: https://github.com/xflr6/concepts/actions/workflows/build.yaml/badge.svg?branch=master
    :target: https://github.com/xflr6/concepts/actions/workflows/build.yaml?query=branch%3Amaster
    :alt: Build
.. |Codecov| image:: https://codecov.io/gh/xflr6/concepts/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/xflr6/concepts
    :alt: Codecov
.. |Readthedocs-stable| image:: https://readthedocs.org/projects/concepts/badge/?version=stable
    :target: https://concepts.readthedocs.io/en/stable/?badge=stable
    :alt: Readthedocs stable
.. |Readthedocs-latest| image:: https://readthedocs.org/projects/concepts/badge/?version=latest
    :target: https://concepts.readthedocs.io/en/latest/?badge=latest
    :alt: Readthedocs latest

.. |Logo| image:: https://raw.github.com/xflr6/concepts/master/docs/logo_full.png
    :alt: Logo