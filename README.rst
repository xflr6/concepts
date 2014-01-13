Concepts
========

|PyPI version| |License|

Concepts is a simple Python implementation of **Formal Concept Analysis** (FCA).

FCA provides a mathematical model for describing a set of **objects** (e.g. King
Arthur, Sir Robin, and the holy grail) with a set of **properties** or features
(e.g. human, knight, king, and mysterious) which each of the objects either
has or not. A table called *formal context* defines which objects have a given
property and vice versa which properties a given object has.


Installation
------------

.. code:: bash

    $ pip install concepts


Formal contexts
---------------

With Concepts, context objects can be created from a string with an ascii-art
style table. The objects and properties will simply be represented by strings.
Separate the property columns with *pipe* symbols, create one row for each objects
and indicate the presence of a property with the character *X*. Note that the
object and property names need to be disjoint to uniquely identify them.

.. code:: python

    >>> from concepts import Context

    >>> c = Context.from_string('''
    ...            |human|knight|king |mysterious|
    ... King Arthur|  X  |  X   |  X  |          |
    ... Sir Robin  |  X  |  X   |     |          |
    ... holy grail |     |      |     |     X    |
    ... ''')

    >>> c  # doctest: +ELLIPSIS
    <Context object mapping 3 objects to 4 properties at ...>

After creation, the parsed content of the table is available on the **context object**.

.. code:: python

    >>> c.objects  # row headings
    ('King Arthur', 'Sir Robin', 'holy grail')

    >>> c.properties  # column headings
    ('human', 'knight', 'king', 'mysterious')

    >>> c.bools  # data cells
    [(True, True, True, False), (True, True, False, False), (False, False, False, True)]


The context object can be queried to return the **common properties** for a
collection of objects (common *intent*, ``intension``) as well as the
**common objects** for a collection of properties (common *extent*, 
``extension``):

.. code:: python

    >>> c.intension(['King Arthur', 'Sir Robin'])  # common properties?
    ('human', 'knight')

    >>> c.extension(['knight', 'mysterious'])  # objects with these properties?
    ()

In FCA these operations are called *derivations* and usually notated with the
*prime* symbol(').

For convenience, the derivation methods **automatically split string arguments** on
whitespace. If your names lack whitespace, you can also use them like this:

.. code:: python

    >>> c.extension('knight king')
    ('King Arthur',)

    >>> c.extension('mysterious human')
    ()


Formal concepts
---------------

A pair of objects and properties such that the objects share exactly the
properties and the properties apply to exactly the objects is called *formal
concept*. Informally, they result from maximal rectangles of *X*-marks in the
context table, when rows and columns can be reordered freely.

You can retrieve the **closest matching concept** corresponding to a collection
of objects or properties with the ``__getitem__`` method of the concept object:

.. code:: python

    >>> c['king']  # closest concept matching intent/extent
    (('King Arthur',), ('human', 'knight', 'king'))

    >>> assert c.intension(('King Arthur',)) == ('human', 'knight', 'king')
    >>> assert c.extension(('human', 'knight', 'king')) == ('King Arthur',)

    >>> c[('King Arthur', 'Sir Robin')]
    (('King Arthur', 'Sir Robin'), ('human', 'knight'))

Within each context, there is a **maximally general concept** comprising all
of the objects as extent and having an empty intent (*supremum*).

.. code:: python

    >>> c[('Sir Robin', 'holy grail')]  # maximal concept, supremum
    (('King Arthur', 'Sir Robin', 'holy grail'), ())


Furthermore there is a **minimally general concept** comprising no object at all
and having all properties as intent (*infimum*).

.. code:: python

    >>> c[('mysterious', 'knight')]  # minimal concept, infimum
    ((), ('human', 'knight', 'king', 'mysterious'))

The concepts of a context can be ordered by extent set-inclusion (or dually 
intent set-inclusion). With this (partial) order, they form a *concept lattice*
having the **supremum** concept (i.e. the tautology) at the top, the **infimum** concept
(i.e. the contradiction) at the bottom, and the other concepts in between.


Concept lattice
---------------

The concept ``lattice`` of a context contains **all pairs of objects and properties**
(*formal concepts*) that can be retrieved from a formal context:

.. code:: python

    >>> c  # doctest: +ELLIPSIS
    <Context object mapping 3 objects to 4 properties at ...>
    
    >>> l = c.lattice

    >>> l  # doctest: +ELLIPSIS
    <Lattice object of 2 atoms 5 concepts 2 coatoms at ...>

    >>> for extent, intent in l:
    ...     print extent, intent
    () ('human', 'knight', 'king', 'mysterious')
    ('King Arthur',) ('human', 'knight', 'king')
    ('holy grail',) ('mysterious',)
    ('King Arthur', 'Sir Robin') ('human', 'knight')
    ('King Arthur', 'Sir Robin', 'holy grail') ()

Individual concepts can be retrieved by different means :

.. code:: python

    >>> l.infimum  # first concept, index 0
    <Infimum {} <-> [human knight king mysterious]>

    >>> l.supremum  # last concept
    <Supremum {King Arthur, Sir Robin, holy grail} <-> []>

    >>> l[1]
    <Atom {King Arthur} <-> [human knight king] <=> King Arthur <=> king>

    >>> l[('mysterious',)]
    <Atom {holy grail} <-> [mysterious] <=> holy grail <=> mysterious>


The concepts form a **directed acyclic graph** and are linked upward (more general
concepts, superconcepts) and downward (less general concepts, subconcepts):

.. code:: python

    >>> l.infimum.upper_neighbors
    (<Atom {King Arthur} <-> [human knight king] <=> King Arthur <=> king>, <Atom {holy grail} <-> [mysterious] <=> holy grail <=> mysterious>)

    >>> l[1].lower_neighbors
    (<Infimum {} <-> [human knight king mysterious]>,)


Visualization
-------------

To visualize the lattice, use its ``graphviz`` method:

.. code:: python

    >>> dot = l.graphviz()

    >>> print dot.source  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
    // <Lattice object of 2 atoms 5 concepts 2 coatoms at ...>
    digraph Lattice {
    node [width=.15 style=filled shape=circle]
    edge [labeldistance=1.5 dir=none]
	    "" [label=""]
		    "" -> mysterious
		    "" -> human
	    human [label=""]
		    human -> human [headlabel="Sir Robin" taillabel="human knight" color=transparent labelangle=90]
		    human -> king
	    mysterious [label=""]
		    mysterious -> mysterious [headlabel="holy grail" taillabel="mysterious" color=transparent labelangle=90]
		    mysterious -> "human knight king mysterious"
	    king [label=""]
		    king -> king [headlabel="King Arthur" taillabel="king" color=transparent labelangle=90]
		    king -> "human knight king mysterious"
	    "human knight king mysterious" [label=""]
    }


Further reading
---------------

- http://en.wikipedia.org/wiki/Formal_concept_analysis
- http://www.upriss.org.uk/fca/fca.html

The generation of the concept lattice is based on the algorithm from
C. Lindig. Fast Concept Analysis. In Gerhard Stumme, editors, Working
with Conceptual Structures - Contributions to ICCS 2000, Shaker Verlag,
Aachen, Germany, 2000.

- http://www.st.cs.uni-saarland.de/~lindig/papers/lindig-fca-2000.pdf


License
-------

Concepts is distributed under the `MIT license
<http://opensource.org/licenses/MIT>`_.

.. |PyPI version| image:: https://pypip.in/v/concepts/badge.png
    :target: https://pypi.python.org/pypi/concepts
    :alt: Latest PyPI Version
.. |License| image:: https://pypip.in/license/concepts/badge.png
    :target: https://pypi.python.org/pypi/concepts
    :alt: License
