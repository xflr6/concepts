.. _advanced:

Advanced Usage
==============


Modification
------------

:class:`.Context` objects are **immutable**. However, iterative assembling,
modification, and combination of contexts is supported by using
:class:`.Definition` objects. They can be edited and then given to
:class:`.Context` to construct a new context object:

.. code:: python

    >>> import concepts

    >>> definition = concepts.Definition()

    >>> definition.add_object('man', ['male'])
    >>> definition.add_object('woman', ['female'])

    >>> definition
    <Definition(['man', 'woman'], ['male', 'female'], [(True, False), (False, True)])>

    >>> definition.add_property('adult', ['man', 'woman'])
    >>> definition.add_property('child', ['boy', 'girl'])

    >>> print(definition)
         |male|female|adult|child|
    man  |X   |      |X    |     |
    woman|    |X     |X    |     |
    boy  |    |      |     |X    |
    girl |    |      |     |X    |

    >>> definition['boy', 'male'] = True
    >>> definition.add_object('girl', ['female'])

    >>> print(concepts.Context(*definition))  # doctest: +ELLIPSIS
    <Context object mapping 4 objects to 4 properties [65aa9782] at 0x...>
             |male|female|adult|child|
        man  |X   |      |X    |     |
        woman|    |X     |X    |     |
        boy  |X   |      |     |X    |
        girl |    |X     |     |X    |


Use definitions to combine two contexts, fill out the missing cells, and create
the resulting context:

.. code:: python

    >>> context = concepts.Context.fromstring('''
    ...            |human|knight|king |mysterious|
    ... King Arthur|  X  |  X   |  X  |          |
    ... Sir Robin  |  X  |  X   |     |          |
    ... holy grail |     |      |     |     X    |
    ... ''')

    >>> human = concepts.Context.fromstring('''
    ...      |male|female|adult|child|
    ... man  |  X |      |  X  |     |
    ... woman|    |   X  |  X  |     |
    ... boy  |  X |      |     |  X  |
    ... girl |    |   X  |     |  X  |
    ... ''')

    >>> union = context.definition() | human.definition()

    >>> print(union)
               |human|knight|king|mysterious|male|female|adult|child|
    King Arthur|X    |X     |X   |          |    |      |     |     |
    Sir Robin  |X    |X     |    |          |    |      |     |     |
    holy grail |     |      |    |X         |    |      |     |     |
    man        |     |      |    |          |X   |      |X    |     |
    woman      |     |      |    |          |    |X     |X    |     |
    boy        |     |      |    |          |X   |      |     |X    |
    girl       |     |      |    |          |    |X     |     |X    |

    >>> union.add_property('human', ['man', 'woman', 'boy', 'girl'])
    >>> union.add_object('King Arthur', ['male', 'adult'])
    >>> union.add_object('Sir Robin', ['male', 'adult'])

    >>> print(union)
               |human|knight|king|mysterious|male|female|adult|child|
    King Arthur|X    |X     |X   |          |X   |      |X    |     |
    Sir Robin  |X    |X     |    |          |X   |      |X    |     |
    holy grail |     |      |    |X         |    |      |     |     |
    man        |X    |      |    |          |X   |      |X    |     |
    woman      |X    |      |    |          |    |X     |X    |     |
    boy        |X    |      |    |          |X   |      |     |X    |
    girl       |X    |      |    |          |    |X     |     |X    |

    >>> concepts.Context(*union).lattice  # doctest: +ELLIPSIS
    <Lattice object of 5 atoms 14 concepts 2 coatoms at 0x...>

.. image:: _static/union.svg
    :align: center


:class:`.Context` from ``pandas.DataFrame``
-------------------------------------------

.. code:: python

    import concepts
    import pandas as pd

    CONTEXT = 'examples/relations.csv'

    context = concepts.load_csv(CONTEXT)

    df = pd.read_csv(CONTEXT, index_col='name')
    objects = df.index.tolist()
    properties = list(df)
    bools = list(df.fillna(False).astype(bool).itertuples(index=False, name=None))

    context_ = concepts.Context(objects, properties, bools)
    assert context_ == context


.. _json_format:

Custom serialization format
---------------------------

For the :class:`.Context` from :data:`concepts.EXAMPLE`:

.. literalinclude:: ../concepts/_example.py

The serialization as Python :obj:`dict` (including its
:attr:`~.Concept.lattice` structure) looks like this:

.. literalinclude:: ../tests/test_serialization.py
    :lines: 10-49

Any extra keys are ignored when loading.

Note that the ``'context'`` list items are (by-index) references to
``'properties'`` (*intents*).
The ``'lattice'`` list items are 4-tuples where the first elements are
references to ``'objects'`` (*extents*), the second elements are references to
``'properties'`` (*intents*), and the last two are references to the
``'lattice'`` list itself (upper and lower neighbors, a.k.a. *cover sets*).
All references are zero-based index references into their target sequence.
