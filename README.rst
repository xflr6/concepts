Concepts
========

|PyPI version| |License| |Supported Python| |Format| |Downloads|

Concepts is a simple Python implementation of **Formal Concept Analysis**
(FCA_).

FCA provides a mathematical model for describing a set of **objects** (e.g. King
Arthur, Sir Robin, and the holy grail) with a set of **properties** (e.g. human,
knight, king, and mysterious) which each of the objects either has or not. A
table called *formal context* defines which objects have a given property and
vice versa which properties a given object has.


Links
-----

- GitHub: http://github.com/xflr6/concepts
- PyPI: http://pypi.python.org/pypi/concepts
- Documentation: http://concepts.readthedocs.org
- Changelog: http://concepts.readthedocs.org/en/latest/changelog.html
- Issue Tracker: http://github.com/xflr6/concepts/issues
- Download: http://pypi.python.org/pypi/concepts#downloads


Installation
------------

This package runs under Python 2.7 and 3.3+, use pip_ to install:

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

    >>> from concepts import Context

    >>> c = Context.fromstring('''
    ...            |human|knight|king |mysterious|
    ... King Arthur|  X  |  X   |  X  |          |
    ... Sir Robin  |  X  |  X   |     |          |
    ... holy grail |     |      |     |     X    |
    ... ''')


Query **common properties** of objects or **common objects** of properties
(*derivation*):

.. code:: python

    >>> c.intension(['King Arthur', 'Sir Robin'])
    ('human', 'knight')

    >>> c.extension(['knight', 'mysterious'])
    ()

Get the closest matching **objects-properties pair** of objects or properties
(*formal concepts*):

.. code:: python

    >>> c['Sir Robin', 'holy grail']
    (('King Arthur', 'Sir Robin', 'holy grail'), ())

    >>> c['king',]
    (('King Arthur',), ('human', 'knight', 'king'))

Iterate over the **concept lattice** of all objects-properties pairs:

.. code:: python

    >>> for extent, intent in c.lattice:
    ...     print('%r %r' % (extent, intent))
    () ('human', 'knight', 'king', 'mysterious')
    ('King Arthur',) ('human', 'knight', 'king')
    ('holy grail',) ('mysterious',)
    ('King Arthur', 'Sir Robin') ('human', 'knight')
    ('King Arthur', 'Sir Robin', 'holy grail') ()

Make a Graphviz visualization of the lattice (use ``.graphviz(view=True)`` to
directly render it and display the resulting PDF):

.. code:: python

    >>> c.lattice.graphviz()  # doctest: +ELLIPSIS
    <graphviz.dot.Digraph object at 0x...>

.. image:: https://raw.github.com/xflr6/concepts/master/docs/holy-grail.png
    :align: center


Further reading
---------------

- http://en.wikipedia.org/wiki/Formal_concept_analysis
- http://www.upriss.org.uk/fca/

The generation of the concept lattice is based on the algorithm from C. Lindig.
`Fast Concept Analysis`_. In Gerhard Stumme, editors, Working with Conceptual
Structures - Contributions to ICCS 2000, Shaker Verlag, Aachen, Germany, 2000.

The included example ``CXT`` files are taken from Uta Priss' `FCA homepage`_


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


.. _FCA: http://en.wikipedia.org/wiki/Formal_concept_analysis
.. _Fast Concept Analysis: http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.143.948
.. _FCA homepage: http://www.upriss.org.uk/fca/examples.html

.. _pip: http://pip.readthedocs.org
.. _Graphviz software: http://www.graphviz.org

.. _bitsets: http://pypi.python.org/pypi/bitsets
.. _graphviz: http://pypi.python.org/pypi/graphviz
.. _features: http://pypi.python.org/pypi/features

.. _other implementations: http://www.upriss.org.uk/fca/fcasoftware.html
.. _more sophisticated algorithms: http://www.upriss.org.uk/fca/fcaalgorithms.html
.. _In-Close: http://sourceforge.net/projects/inclose/
.. _Fcbo: http://fcalgs.sourceforge.net

.. _MIT license: http://opensource.org/licenses/MIT


.. |--| unicode:: U+2013


.. |PyPI version| image:: https://img.shields.io/pypi/v/concepts.svg
    :target: https://pypi.python.org/pypi/concepts
    :alt: Latest PyPI Version
.. |License| image:: https://img.shields.io/pypi/l/concepts.svg
    :target: https://pypi.python.org/pypi/concepts
    :alt: License
.. |Supported Python| image:: https://img.shields.io/pypi/pyversions/concepts.svg
    :target: https://pypi.python.org/pypi/concepts
    :alt: Supported Python Versions
.. |Format| image:: https://img.shields.io/pypi/format/concepts.svg
    :target: https://pypi.python.org/pypi/concepts
    :alt: Format
.. |Downloads| image:: https://img.shields.io/pypi/dm/concepts.svg
    :target: https://pypi.python.org/pypi/concepts
    :alt: Downloads
