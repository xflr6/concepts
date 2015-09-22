.. _examples:

Examples
========


digits.cxt
----------

.. literalinclude:: ../examples/digits.cxt

.. code:: python

    from concepts import Context
    
    d = Context.fromfile('examples/digits.cxt')
    
    d.lattice.graphviz().view()

.. image:: _static/digits.svg
    :align: center

