.. _examples:

Examples
========

The following code examples are included in the ``examples/`` directory of the
`source repository/distribution`__.

.. __: https://github.com/xflr6/concepts/tree/master/examples/


digits.cxt
----------

.. literalinclude:: ../examples/digits.cxt

.. code:: python

    from concepts import Context
    
    d = Context.fromfile('examples/digits.cxt')
    
    d.lattice.graphviz(view=True)

.. image:: _static/digits.svg
    :align: center


relations.csv
-------------

.. literalinclude:: ../examples/relations.csv

.. code:: python

    from concepts import Context
    
    r = Context.fromfile('examples/relations.csv', frmat='csv')
    
    r.lattice.graphviz(view=True)

.. image:: _static/relations.svg
    :align: center
