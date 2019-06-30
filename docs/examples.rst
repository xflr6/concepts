.. _examples:

Examples
========

These and more examples files are included in the ``examples/`` directory of the
`source repository/distribution`__.

.. __: https://github.com/xflr6/concepts/tree/master/examples/


digits.cxt
----------

.. literalinclude:: ../examples/digits.cxt
    :linenos:

.. code:: python

    from concepts import Context
    
    d = Context.fromfile('examples/digits.cxt')
    
    d.lattice.graphviz(view=True)

.. image:: _static/digits.svg
    :align: center


relations.csv
-------------

.. literalinclude:: ../examples/relations.csv
    :linenos:

.. code:: python

    from concepts import Context
    
    r = Context.fromfile('examples/relations.csv', frmat='csv')
    
    r.lattice.graphviz(view=True)

.. image:: _static/relations.svg
    :align: center


example.json
------------

.. literalinclude:: ../examples/example.json
    :linenos:

.. code:: python

    from concepts import Context
    
    e = Context.fromjson('examples/example.json', require_lattice=True)
    
    e.lattice.graphviz(view=True)

.. image:: _static/example.svg
    :align: center
