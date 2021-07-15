.. _api:

API Reference
=============

.. autosummary::
    :nosignatures:

    ~concepts.load
    ~concepts.load_csv
    ~concepts.load_cxt
    ~concepts.make_context
    ~concepts.Context
    ~concepts.Definition
    concepts.lattices.Lattice
    concepts.lattices.Concept


Top-level functions
-------------------

Short-cuts to the most common uses of :meth:`.Context.fromfile` and
:meth:`.Context.fromstring`:

.. autofunction:: concepts.load

.. autofunction:: concepts.load_csv

.. autofunction:: concepts.load_cxt

.. autofunction:: concepts.make_context


Context
-------

.. autoclass:: concepts.Context
    :members:
        fromstring, fromfile, fromdict, fromjson,
        intension, extension,
        neighbors,
        __getitem__,
        __eq__, __ne__,
        tostring, tofile, todict, tojson, crc32,
        objects, properties, bools, shape, fill_ratio,
        definition, relations, lattice


Definition
----------

.. autoclass:: concepts.Definition
    :members:
        fromfile, copy,
        __iter__, __getitem__,
        objects, properties, bools, shape, fill_ratio,
        tostring, crc32,
        take, transposed, inverted,
        rename_object, rename_property,
        move_object, move_property,
        __setitem__,
        add_object, add_property,
        remove_object, remove_property,
        remove_empty_objects, remove_empty_properties,
        set_object, set_property,
        union_update, intersection_update,
        union, intersection


Lattice
-------

.. autoclass:: concepts.lattices.Lattice
    :members:
        infimum, supremum,
        __call__, __getitem__, __iter__, __len__,
        atoms,
        join, meet,
        upset_union, downset_union,
        upset_generalization,
        graphviz


Concept
-------

.. autoclass:: concepts.lattices.Concept
    :members:
        lattice,
        upper_neighbors, lower_neighbors,
        objects, properties,
        __iter__,
        extent, intent,
        minimal, attributes, 
        upset, downset,
        implies, subsumes,
        properly_implies, properly_subsumes,
        join, meet,
        incompatible_with, complement_of, subcontrary_with, orthogonal_to
