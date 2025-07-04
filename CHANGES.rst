Changelog
=========


Version 0.10 (in development)
-----------------------------

Switch to pyprojec.toml.

Drop Python 2 support.

Drop Python 3.5, 3.6, and 3.7 support and tag Python 3.9, 3.10, and 3.11 support.

Add ``shape`` property to ``Context```and ``Definition`` returning a named tuple of
``(len(objects), len(properties))`` (PR Tomáš Mikula).

Add ``fill_ratio`` property to ``Context```and ``Definition`` (PR Tomáš Mikula).


Version 0.9.2
-------------

Add ``make_object_label`` and ``make_property_label`` keyword arguments to
``Lattice.graphviz()`` allowing to override the formatting of object and
property labels (e.g. ``make_object_labels=', '.join`` objects labels as
comma-separated object lists.


Version 0.9.1
-------------

Tag Python 3.8 support.


Version 0.9
-----------

Make the ``frmat`` argument (e.g. ``'table'``, ``'cxt'``, ``'csv'``) for
reading/writing ``Context`` objects case-insensitive (mirroring
case-insensitivity of format inference from filename suffixes).

Add ``Context.tojson(path_or_fileonj)`` and ``Context.fromjson(path_or_fileonj)``
for long term storage format serialized as json. This custom format can include
the lattice structure information so that e.g. big lattices that are expensive to
compute can be stored and loaded without the need to re-calculate the lattice.

Add ``Context.todict()`` and ``Context.fromdict()`` for custom format as plain
Python ``dict``. Can be (de)serialized with other tools such as pickle,
``pprint.pprint()`` + ``ast.literal_eval()``, yaml, toml, xml, a database,
etc.


Version 0.8.1
-------------

Drop Python 3.4 support.


Version 0.8
-----------

Add ``.crc32()``-method to ``Context`` and ``Definition`` returning the
hex-encoded crc32 of their context table string.

Include crc32 in the ``__repr__`` of context objects.

Add recipe for context from ``pandas.DataFrame`` to docs.


Version 0.7.14
--------------

Add ``load()`` inferring the format form the file suffix.

Tag Python 3.7 support, add simple tox config.

Fix collections.MutableSet PendingDeprecationWarning.


Version 0.7.13
--------------

Increase API docs coverage.

Use compatible release version specifiers (bump ``graphviz`` to ~=0.7).


Version 0.7.12
--------------

Drop Python 3.3 support.

Include LICENSE file in wheel.


Version 0.7.11
--------------

Port most tests from nose/unittest to pytest, add Travis CI and coveralls.

Update package meta data, tag python 3.6 support.


Version 0.7.10
--------------

Let the ``.graphviz()``-method pass ``kwargs`` to the returned graph (e.g. ``format='png'``).

Relax optional ``graphivz`` dependency to < 1.0.

Added extended Sphinx-based documentation.


Version 0.7.9
-------------

Added ``move_object()`` and ``move_property()`` to definitions.

The ``take()``-method of definitions now supports skipping all objects or properties
when called with empty iterables (default None means include all).

Simplified ``__getitem__`` examples.


Version 0.7.8
-------------

Fixed a possible encoding issue with ``.tofile()``.

Visualize more examples.

Added tests for formats dump/load file roundtrips.


Version 0.7.7
-------------

Changed context ``__eq__`` test with non-contexts from ``TypeError`` to ``NotImplemented``.

Fixed non-working augmented assignment operators on definitions.
Simplified definition implementation.


Version 0.7.6
-------------

Added context definition objects, allowing interactive building, modification,
and combination of context creation arguments.

Added ``include_unary`` option to logical connectives calculation.


Version 0.7.5
-------------

Made derivation code more explicit. Subset test replaced by inlined
implementation using only ``bitwise_and``.


Version 0.7.4
-------------

Changed context ``._lattice()`` to a generator.

Fixed failure to handle contexts with single object/property.


Version 0.7.3
-------------

Improved context/lattice division of labour: context now computes all concepts
with their covering relation, while lattice only builds/decorates the object-
based representation.

Improved context and bitset interface used by lattice (``reduce_and()``, ``reduce_or()``).
Added ``doubleprime()``-method to extents and intents.
Added ``raw`` option to ``intension()``, ``extension()``, and ``neighbors()`` method of context.

Added ``EXAMPLE`` context for repl experiments.


Version 0.7.2
-------------

Context relation now omits orthogonal pairs in ``__str__()``.


Version 0.7.1
-------------

Fixed CSV export with Python 3.3+.


Version 0.7
-----------

Added Python 3.3+ support.

Set default UTF-8 encoding in context ``.tofile()``.


Version 0.6.2
-------------

Switch ``setup.py`` dependencies to version ranges.


Version 0.6.1
-------------

Added ``make_context()``.

Improved documentation.


Version 0.6
-----------

Added ``.orthogonal_to()``.

Changed attributes to return a generator instead of a list.

Improved doctests.


Version 0.5
-----------

Upset and downset of concept object now are iterable-returning methods instead
of properties (backwards incompatible). 

Changed concept object minimal generating properties to be computed on request
instead of being precomputed during lattice build; changed minimal and
attributes from properties to methods (backwards incompatible). 

Improved unicode support.

Changed pickling of lattice and concepts.

Changed ordering of ``downset`` and ``lower_neighbors`` to longlex.


Version 0.4
-----------

Add context file ``'csv'`` format.

Added newline normalization to context file loading.

Update ``bitset`` dependency to 0.5 (better neighbors).

Backwards incompatible: removed underscore from (from|to)_(string|file) method
names.


Version 0.3
-----------

Update ``graphviz`` interface dependency to 0.2 (UTF-8 support) with changed api.


Version 0.2.3
-------------

Support empty iterables in ``Lattice.join()`` and ``.meet()``.


Version 0.2.2
-------------

Simplified ``graphviz`` quoting.


Version 0.2.1
-------------

Improved visualization.


Version 0.2
-----------

Added loading and dumping of contexts and include some example cxt files.

Make context objects pickleable.

Context and lattice methods no more implicitly split string arguments.


Version 0.1.4
-------------

Switch to standalone ``graphviz`` interface implementation.


Version 0.1.3
-------------

Refine packaging info.


Version 0.1.2
-------------

Account for ``bitsets`` internal api change.

Improve documentation.


Version 0.1.1
-------------

Switch to standalone ``bitsets`` implementation.


Version 0.1
-----------

First public release.
