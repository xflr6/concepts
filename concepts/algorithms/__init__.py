from collections.abc import Iterator
import os

from .._common import Concept, ConceptList

from .common import iterunion
from .fcbo import fast_generate_from as _fast_generate_from_py
from .fcbo import fcbo_dual as _fcbo_dual_py
from .lindig import lattice as _lattice_py
from .lindig import neighbors

# Try to import Rust implementations
from ._rust import (
    RUST_AVAILABLE,
    fcbo_fast_generate_from_rust,
    fcbo_dual_rust,
    lindig_lattice_rust_full,
)

# Environment variable to force Python implementation
_USE_PYTHON = os.environ.get('CONCEPTS_USE_PYTHON', '').lower() in ('1', 'true', 'yes')

__all__ = ['iterunion',
           'fast_generate_from', 'fcbo_dual',
           'lattice', 'neighbors',
           'iterconcepts', 'get_concepts',
           'RUST_AVAILABLE', 'USE_RUST']

# Flag indicating whether Rust is being used
USE_RUST = RUST_AVAILABLE and not _USE_PYTHON


def fast_generate_from(context):
    """Generate concepts from context using FCBO algorithm.

    Uses Rust implementation if available, otherwise falls back to Python.
    Set CONCEPTS_USE_PYTHON=1 environment variable to force Python implementation.
    """
    if USE_RUST:
        return fcbo_fast_generate_from_rust(context)
    return _fast_generate_from_py(context)


def fcbo_dual(context):
    """Generate concepts from context using FCBO dual algorithm.

    Uses Rust implementation if available, otherwise falls back to Python.
    Set CONCEPTS_USE_PYTHON=1 environment variable to force Python implementation.
    """
    if USE_RUST:
        return fcbo_dual_rust(context)
    return _fcbo_dual_py(context)


def lattice(Objects, *, infimum):
    """Generate lattice using Lindig's algorithm.

    Uses Rust implementation if available, otherwise falls back to Python.
    Set CONCEPTS_USE_PYTHON=1 environment variable to force Python implementation.

    Note: This function requires access to the context for Rust implementation.
    The Rust version is used via the Context._lattice method.
    """
    # For direct calls with Objects bitset, use Python implementation
    # Rust implementation is integrated at the Context level
    return _lattice_py(Objects, infimum=infimum)


def iterconcepts(context) -> Iterator[Concept]:
    iterconcepts = fast_generate_from(context)
    return map(Concept._make, iterconcepts)


def get_concepts(context) -> list[Concept]:
    iterconcepts = fast_generate_from(context)
    return ConceptList.frompairs(iterconcepts)
