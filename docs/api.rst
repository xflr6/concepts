.. _api:

API Reference
=============


Context
-------

.. autofunction:: concepts.load_cxt

.. autofunction:: concepts.load_csv

.. autofunction:: concepts.make_context

.. autoclass:: concepts.Context
    :members:
        fromstring, fromfile,
        intension, extension,
        neighbors,
        __getitem__,
        tostring, tofile,
        objects, properties, bools,
        definition, relations, lattice


Definition
----------

.. autoclass:: concepts.Definition
    :members:
        fromfile, copy,
        __iter__, __getitem__,
        objects, properties, bools,
        tostring,
        take, transposed, inverted,
        rename_object, rename_property,
        move_object, move_property,
        __setitem__,
        add_object, add_property,
        remove_object, remove_property,
        set_object, set_property,
        union_update, intersection_update,
        union, intersection


Lattice
-------

.. autoclass:: concepts.lattices.Lattice
    :members:
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
        objects, properties,
        __iter__,
        extent, intent,
        minimal, attributes, 
        upset, downset,
        implies, subsumes,
        properly_implies, properly_subsumes,
        join, meet,
        incompatible_with, complement_of, subcontrary_with, orthogonal_to
