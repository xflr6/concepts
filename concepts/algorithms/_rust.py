"""Rust-accelerated FCA lattice generation algorithms.

This module provides Python wrappers for the Rust implementations of:
- Lindig's Fast Concept Analysis algorithm
- FCBO (Fast Close by One) algorithm

The wrappers maintain 100% API compatibility with the pure Python implementations.
"""

__all__ = ['lindig_lattice_rust', 'fcbo_fast_generate_from_rust', 'fcbo_dual_rust',
           'RUST_AVAILABLE']

try:
    import concepts_rust
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False


def _extract_context_data(context):
    """Extract raw bitset data from a Context object for Rust functions."""
    n_objects = context.shape.objects
    n_properties = context.shape.properties

    # Get raw integer representations of extents and intents
    # extents[j] = bitset of objects that have property j
    # intents[i] = bitset of properties that object i has
    extents = [int(e) for e in context._extents]
    intents = [int(i) for i in context._intents]

    return n_objects, n_properties, extents, intents


def lindig_lattice_rust(context, infimum=()):
    """Rust implementation of Lindig's lattice algorithm.

    Args:
        context: A Context object.
        infimum: Starting objects (default empty).

    Yields:
        (extent, intent, upper, lower) tuples with bitset objects.
    """
    if not RUST_AVAILABLE:
        raise ImportError("concepts_rust module not available")

    Objects = context._Objects
    Properties = context._Properties

    n_objects, n_properties, extents, intents = _extract_context_data(context)

    # Convert infimum to integer
    infimum_int = int(Objects.frommembers(infimum))

    # Call Rust implementation
    results = concepts_rust.lindig_lattice_py(
        n_objects, n_properties, extents, intents, infimum_int
    )

    # Convert results back to bitset objects
    for extent_int, intent_int, upper_indices, lower_indices in results:
        extent = Objects.fromint(extent_int)
        intent = Properties.fromint(intent_int)
        # upper and lower are indices that will be filled with extents later
        # We need to convert them to extent bitsets
        yield (extent, intent, upper_indices, lower_indices)


def lindig_lattice_rust_full(context, infimum=()):
    """Rust implementation returning full concept tuples with extent references.

    This version post-processes to match the exact Python output format
    where upper/lower contain actual extent bitsets instead of indices.
    """
    if not RUST_AVAILABLE:
        raise ImportError("concepts_rust module not available")

    Objects = context._Objects
    Properties = context._Properties

    n_objects, n_properties, extents, intents = _extract_context_data(context)
    infimum_int = int(Objects.frommembers(infimum))

    results = concepts_rust.lindig_lattice_py(
        n_objects, n_properties, extents, intents, infimum_int
    )

    # First pass: collect all concepts
    concepts = []
    for extent_int, intent_int, upper_indices, lower_indices in results:
        extent = Objects.fromint(extent_int)
        intent = Properties.fromint(intent_int)
        concepts.append((extent, intent, upper_indices, lower_indices))

    # Second pass: convert indices to extent references
    for extent, intent, upper_indices, lower_indices in concepts:
        upper_extents = [concepts[i][0] for i in upper_indices]
        lower_extents = [concepts[i][0] for i in lower_indices]
        yield (extent, intent, upper_extents, lower_extents)


def fcbo_fast_generate_from_rust(context):
    """Rust implementation of FCBO fast_generate_from algorithm.

    Args:
        context: A Context object.

    Yields:
        (extent, intent) pairs with bitset objects.
    """
    if not RUST_AVAILABLE:
        raise ImportError("concepts_rust module not available")

    Objects = context._Objects
    Properties = context._Properties

    n_objects, n_properties, extents, intents = _extract_context_data(context)

    # Call Rust implementation
    results = concepts_rust.fcbo_fast_generate_from_py(
        n_objects, n_properties, extents, intents
    )

    # Convert results back to bitset objects
    for extent_int, intent_int in results:
        extent = Objects.fromint(extent_int)
        intent = Properties.fromint(intent_int)
        yield (extent, intent)


def fcbo_dual_rust(context):
    """Rust implementation of FCBO dual algorithm.

    Args:
        context: A Context object.

    Yields:
        (extent, intent) pairs with bitset objects.
    """
    if not RUST_AVAILABLE:
        raise ImportError("concepts_rust module not available")

    Objects = context._Objects
    Properties = context._Properties

    n_objects, n_properties, extents, intents = _extract_context_data(context)

    # Call Rust implementation
    results = concepts_rust.fcbo_dual_py(
        n_objects, n_properties, extents, intents
    )

    # Convert results back to bitset objects
    for extent_int, intent_int in results:
        extent = Objects.fromint(extent_int)
        intent = Properties.fromint(intent_int)
        yield (extent, intent)
