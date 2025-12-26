//! Rust implementation of Formal Concept Analysis lattice generation algorithms.
//!
//! This module provides exact reimplementations of:
//! - Lindig's Fast Concept Analysis algorithm (2000)
//! - FCBO (Fast Close by One) algorithm (Outrata & Vychodil, 2012)

use pyo3::prelude::*;
use std::cmp::Ordering;
use std::collections::{BinaryHeap, HashMap};

// =============================================================================
// BitSet Implementation (arbitrary size using Vec<u64>)
// =============================================================================

/// A bitset represented as a vector of u64 words.
/// Bit 0 is the LSB of words[0], bit 64 is the LSB of words[1], etc.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
struct BitSet {
    words: Vec<u64>,
    n_bits: usize,
}

impl BitSet {
    /// Create a new bitset with all bits set to 0.
    fn new(n_bits: usize) -> Self {
        let n_words = (n_bits + 63) / 64;
        BitSet {
            words: vec![0; n_words],
            n_bits,
        }
    }

    /// Create a bitset with all bits set to 1 (up to n_bits).
    fn supremum(n_bits: usize) -> Self {
        let n_words = (n_bits + 63) / 64;
        let mut words = vec![u64::MAX; n_words];
        // Mask off extra bits in the last word
        if n_bits % 64 != 0 {
            words[n_words - 1] &= (1u64 << (n_bits % 64)) - 1;
        }
        BitSet { words, n_bits }
    }

    /// Create a bitset from a u128 value (for small bitsets).
    fn from_u128(value: u128, n_bits: usize) -> Self {
        let n_words = (n_bits + 63) / 64;
        let mut words = vec![0u64; n_words];
        if n_words >= 1 {
            words[0] = value as u64;
        }
        if n_words >= 2 {
            words[1] = (value >> 64) as u64;
        }
        BitSet { words, n_bits }
    }

    /// Convert to u128 (for small bitsets).
    fn to_u128(&self) -> u128 {
        let mut result: u128 = 0;
        if !self.words.is_empty() {
            result |= self.words[0] as u128;
        }
        if self.words.len() >= 2 {
            result |= (self.words[1] as u128) << 64;
        }
        result
    }

    /// Check if the bitset is empty (all zeros).
    fn is_empty(&self) -> bool {
        self.words.iter().all(|&w| w == 0)
    }

    /// Count the number of set bits.
    fn count(&self) -> usize {
        self.words.iter().map(|w| w.count_ones() as usize).sum()
    }

    /// Get bit at position i.
    fn get(&self, i: usize) -> bool {
        if i >= self.n_bits {
            false
        } else {
            (self.words[i / 64] >> (i % 64)) & 1 != 0
        }
    }

    /// Set bit at position i.
    fn set(&mut self, i: usize) {
        if i < self.n_bits {
            self.words[i / 64] |= 1u64 << (i % 64);
        }
    }

    /// Bitwise NOT (complement), respecting n_bits.
    fn complement(&self) -> Self {
        let mut result = BitSet::new(self.n_bits);
        for (i, &w) in self.words.iter().enumerate() {
            result.words[i] = !w;
        }
        // Mask off extra bits in the last word
        if self.n_bits % 64 != 0 {
            let n_words = result.words.len();
            result.words[n_words - 1] &= (1u64 << (self.n_bits % 64)) - 1;
        }
        result
    }

    /// Bitwise AND.
    fn and(&self, other: &BitSet) -> Self {
        let mut result = BitSet::new(self.n_bits);
        for (i, (&a, &b)) in self.words.iter().zip(other.words.iter()).enumerate() {
            result.words[i] = a & b;
        }
        result
    }

    /// Bitwise OR.
    fn or(&self, other: &BitSet) -> Self {
        let mut result = BitSet::new(self.n_bits);
        for (i, (&a, &b)) in self.words.iter().zip(other.words.iter()).enumerate() {
            result.words[i] = a | b;
        }
        result
    }

    /// Subtract 1 from the bitset (for computing j_mask = j_property - 1).
    fn sub_one(&self) -> Self {
        let mut result = self.clone();
        let mut borrow = true;
        for w in result.words.iter_mut() {
            if borrow {
                if *w == 0 {
                    *w = u64::MAX;
                } else {
                    *w -= 1;
                    borrow = false;
                }
            }
        }
        // Mask off extra bits
        if self.n_bits % 64 != 0 {
            let n_words = result.words.len();
            result.words[n_words - 1] &= (1u64 << (self.n_bits % 64)) - 1;
        }
        result
    }

    /// Get shortlex sort key: (count, lexicographic order).
    /// Returns (count, words) for comparison.
    fn shortlex(&self) -> (usize, Vec<u64>) {
        (self.count(), self.words.clone())
    }

    /// Iterate over set bit positions.
    fn iter_bits(&self) -> impl Iterator<Item = usize> + '_ {
        let n_bits = self.n_bits;
        self.words.iter().enumerate().flat_map(move |(word_idx, &word)| {
            let base = word_idx * 64;
            (0..64).filter_map(move |bit| {
                if (word >> bit) & 1 != 0 && base + bit < n_bits {
                    Some(base + bit)
                } else {
                    None
                }
            })
        })
    }

    /// Create atomic bitsets (single bit set) for each set bit.
    fn atoms(&self) -> Vec<BitSet> {
        self.iter_bits()
            .map(|i| {
                let mut atom = BitSet::new(self.n_bits);
                atom.set(i);
                atom
            })
            .collect()
    }
}

// =============================================================================
// FCA Context Structure
// =============================================================================

/// Formal context with extents and intents as integer vectors.
struct FcaContext {
    n_objects: usize,
    n_properties: usize,
    /// extents[j] = bitset of objects that have property j
    extents: Vec<BitSet>,
    /// intents[i] = bitset of properties that object i has
    intents: Vec<BitSet>,
}

impl FcaContext {
    fn new(n_objects: usize, n_properties: usize, extents_raw: Vec<u128>, intents_raw: Vec<u128>) -> Self {
        let extents: Vec<BitSet> = extents_raw
            .iter()
            .map(|&e| BitSet::from_u128(e, n_objects))
            .collect();
        let intents: Vec<BitSet> = intents_raw
            .iter()
            .map(|&i| BitSet::from_u128(i, n_properties))
            .collect();
        FcaContext {
            n_objects,
            n_properties,
            extents,
            intents,
        }
    }

    /// Prime operation: objects -> properties (intent of objects).
    /// For each set bit in `objects`, AND the corresponding intent.
    fn prime_objects(&self, objects: &BitSet) -> BitSet {
        let mut result = BitSet::supremum(self.n_properties);
        for i in objects.iter_bits() {
            if i < self.intents.len() {
                result = result.and(&self.intents[i]);
            }
        }
        result
    }

    /// Prime operation: properties -> objects (extent of properties).
    /// For each set bit in `properties`, AND the corresponding extent.
    fn prime_properties(&self, properties: &BitSet) -> BitSet {
        let mut result = BitSet::supremum(self.n_objects);
        for j in properties.iter_bits() {
            if j < self.extents.len() {
                result = result.and(&self.extents[j]);
            }
        }
        result
    }

    /// Double prime: objects -> (closed_objects, intent).
    fn doubleprime_objects(&self, objects: &BitSet) -> (BitSet, BitSet) {
        let intent = self.prime_objects(objects);
        let extent = self.prime_properties(&intent);
        (extent, intent)
    }

    /// Double prime: properties -> (extent, closed_properties).
    fn doubleprime_properties(&self, properties: &BitSet) -> (BitSet, BitSet) {
        let extent = self.prime_properties(properties);
        let intent = self.prime_objects(&extent);
        (extent, intent)
    }
}

// =============================================================================
// Lindig Algorithm (Fast Concept Analysis)
// =============================================================================

/// Wrapper for heap ordering (max-heap, but we want min-heap by shortlex).
#[derive(Clone, Eq, PartialEq)]
struct HeapEntry {
    shortlex_key: (usize, Vec<u64>),
    extent: BitSet,
    intent: BitSet,
    index: usize,
}

impl Ord for HeapEntry {
    fn cmp(&self, other: &Self) -> Ordering {
        // Reverse for min-heap behavior
        other.shortlex_key.cmp(&self.shortlex_key)
    }
}

impl PartialOrd for HeapEntry {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

/// Find upper neighbors of a concept (Lindig's neighbor function).
/// This is an exact translation of lindig.py's neighbors function.
fn neighbors(objects: &BitSet, ctx: &FcaContext) -> Vec<(BitSet, BitSet)> {
    let mut result = Vec::new();
    let mut minimal = objects.complement();

    for i in 0..ctx.n_objects {
        if !minimal.get(i) {
            continue;
        }

        // add = atomic bitset with only bit i set
        let mut add = BitSet::new(ctx.n_objects);
        add.set(i);

        let objects_and_add = objects.or(&add);
        let (extent, intent) = ctx.doubleprime_objects(&objects_and_add);

        // Check: extent & ~objects_and_add & minimal
        let complement_oaa = objects_and_add.complement();
        let check = extent.and(&complement_oaa).and(&minimal);

        if !check.is_empty() {
            // minimal &= ~add
            minimal = minimal.and(&add.complement());
        } else {
            result.push((extent, intent));
        }
    }

    result
}

/// Lindig's lattice generation algorithm.
/// Returns: Vec<(extent_int, intent_int, upper_indices, lower_indices)>
fn lindig_lattice(ctx: &FcaContext, infimum: &BitSet) -> Vec<(u128, u128, Vec<usize>, Vec<usize>)> {
    let (extent, intent) = ctx.doubleprime_objects(infimum);

    let mut concepts: Vec<(BitSet, BitSet, Vec<usize>, Vec<usize>)> = Vec::new();
    let mut mapping: HashMap<Vec<u64>, usize> = HashMap::new();
    let mut heap: BinaryHeap<HeapEntry> = BinaryHeap::new();

    let idx = 0;
    concepts.push((extent.clone(), intent.clone(), Vec::new(), Vec::new()));
    mapping.insert(extent.words.clone(), idx);

    heap.push(HeapEntry {
        shortlex_key: extent.shortlex(),
        extent: extent.clone(),
        intent: intent.clone(),
        index: idx,
    });

    while let Some(entry) = heap.pop() {
        let current_idx = entry.index;
        let extent = &concepts[current_idx].0;

        let nbrs = neighbors(extent, ctx);

        for (n_extent, n_intent) in nbrs {
            // Add n_extent to current concept's upper list
            let n_key = n_extent.words.clone();

            if let Some(&existing_idx) = mapping.get(&n_key) {
                // n_extent already exists - add to its lower list
                concepts[current_idx].2.push(existing_idx);
                concepts[existing_idx].3.push(current_idx);
            } else {
                // New concept
                let new_idx = concepts.len();
                concepts[current_idx].2.push(new_idx);
                concepts.push((
                    n_extent.clone(),
                    n_intent.clone(),
                    Vec::new(),
                    vec![current_idx],
                ));
                mapping.insert(n_key, new_idx);

                heap.push(HeapEntry {
                    shortlex_key: n_extent.shortlex(),
                    extent: n_extent,
                    intent: n_intent,
                    index: new_idx,
                });
            }
        }
    }

    // Convert to output format
    concepts
        .into_iter()
        .map(|(e, i, u, l)| (e.to_u128(), i.to_u128(), u, l))
        .collect()
}

// =============================================================================
// FCBO Algorithm (Fast Close by One)
// =============================================================================

/// FCBO fast_generate_from algorithm.
/// Generates concepts by intents.
fn fcbo_fast_generate_from(ctx: &FcaContext) -> Vec<(u128, u128)> {
    let n_properties = ctx.n_properties;

    // j_atom: list of (index, atomic bitset for property j)
    let properties_supremum = BitSet::supremum(n_properties);
    let j_atom: Vec<(usize, BitSet)> = properties_supremum
        .atoms()
        .into_iter()
        .enumerate()
        .collect();

    let objects_supremum = BitSet::supremum(ctx.n_objects);
    let properties_infimum = BitSet::new(n_properties);

    let initial_concept = ctx.doubleprime_objects(&objects_supremum);

    // Stack: (concept, property_index, property_sets)
    let mut stack: Vec<((BitSet, BitSet), usize, Vec<BitSet>)> = Vec::new();
    let initial_property_sets = vec![properties_infimum.clone(); n_properties];
    stack.push((initial_concept, 0, initial_property_sets));

    let mut result: Vec<(u128, u128)> = Vec::new();

    while let Some((concept, property_index, property_sets)) = stack.pop() {
        let (extent, intent) = &concept;
        result.push((extent.to_u128(), intent.to_u128()));

        if property_index == n_properties || extent.is_empty() {
            continue;
        }

        let mut next_property_sets = property_sets.clone();

        // Iterate in reverse order
        for &(j, ref j_property) in j_atom[property_index..].iter().rev() {
            // if j_property & intent
            if !j_property.and(intent).is_empty() {
                continue;
            }

            // j_mask = j_property - 1
            let j_mask = j_property.sub_one();

            // x = next_property_sets[j] & j_mask
            let x = next_property_sets[j].and(&j_mask);

            // if x & intent == x
            if x.and(intent) == x {
                // j_extent = extent & context._extents[j]
                let j_extent_bits = extent.and(&ctx.extents[j]);

                // j_intent = prime(j_extent)
                let j_intent = ctx.prime_objects(&j_extent_bits);

                // j_lower = j_intent & j_mask
                let j_lower = j_intent.and(&j_mask);

                // if j_lower & intent == j_lower
                if j_lower.and(intent) == j_lower {
                    let new_concept = (j_extent_bits.clone(), j_intent.clone());
                    stack.push((new_concept, j + 1, next_property_sets.clone()));
                } else {
                    next_property_sets[j] = j_intent;
                }
            }
        }
    }

    result
}

/// FCBO dual algorithm.
/// Generates concepts by extents.
fn fcbo_dual(ctx: &FcaContext) -> Vec<(u128, u128)> {
    let n_objects = ctx.n_objects;

    // j_atom: list of (index, atomic bitset for object j)
    let objects_supremum = BitSet::supremum(n_objects);
    let j_atom: Vec<(usize, BitSet)> = objects_supremum
        .atoms()
        .into_iter()
        .enumerate()
        .collect();

    let objects_infimum = BitSet::new(n_objects);

    // Start with Objects.infimum.doubleprime() = (empty extent, all properties)
    let initial_concept = ctx.doubleprime_objects(&objects_infimum);

    // Stack: (concept, object_index, object_sets)
    let mut stack: Vec<((BitSet, BitSet), usize, Vec<BitSet>)> = Vec::new();
    let initial_object_sets = vec![objects_infimum.clone(); n_objects];
    stack.push((initial_concept, 0, initial_object_sets));

    let mut result: Vec<(u128, u128)> = Vec::new();

    while let Some((concept, object_index, object_sets)) = stack.pop() {
        let (extent, intent) = &concept;
        result.push((extent.to_u128(), intent.to_u128()));

        if object_index == n_objects || intent.is_empty() {
            continue;
        }

        let mut next_object_sets = object_sets.clone();

        // Iterate in reverse order
        for &(j, ref j_object) in j_atom[object_index..].iter().rev() {
            // if extent & j_object
            if !extent.and(j_object).is_empty() {
                continue;
            }

            // j_mask = j_object - 1
            let j_mask = j_object.sub_one();

            // x = next_object_sets[j] & j_mask
            let x = next_object_sets[j].and(&j_mask);

            // if x & extent == x
            if x.and(extent) == x {
                // j_intent = intent & context._intents[j]
                let j_intent_bits = intent.and(&ctx.intents[j]);

                // j_extent = prime(j_intent)
                let j_extent = ctx.prime_properties(&j_intent_bits);

                // j_lower = j_extent & j_mask
                let j_lower = j_extent.and(&j_mask);

                // if j_lower & extent == j_lower
                if j_lower.and(extent) == j_lower {
                    let new_concept = (j_extent.clone(), j_intent_bits.clone());
                    stack.push((new_concept, j + 1, next_object_sets.clone()));
                } else {
                    next_object_sets[j] = j_extent;
                }
            }
        }
    }

    result
}

// =============================================================================
// Python Bindings
// =============================================================================

/// Lindig lattice algorithm.
///
/// Args:
///     n_objects: Number of objects in the context.
///     n_properties: Number of properties in the context.
///     extents: List of integers representing extents (column bitsets).
///     intents: List of integers representing intents (row bitsets).
///     infimum: Starting extent (usually 0 for empty set).
///
/// Returns:
///     List of (extent, intent, upper_indices, lower_indices) tuples.
#[pyfunction]
fn lindig_lattice_py(
    n_objects: usize,
    n_properties: usize,
    extents: Vec<u128>,
    intents: Vec<u128>,
    infimum: u128,
) -> Vec<(u128, u128, Vec<usize>, Vec<usize>)> {
    let ctx = FcaContext::new(n_objects, n_properties, extents, intents);
    let infimum_bitset = BitSet::from_u128(infimum, n_objects);
    lindig_lattice(&ctx, &infimum_bitset)
}

/// FCBO fast_generate_from algorithm.
///
/// Args:
///     n_objects: Number of objects in the context.
///     n_properties: Number of properties in the context.
///     extents: List of integers representing extents (column bitsets).
///     intents: List of integers representing intents (row bitsets).
///
/// Returns:
///     List of (extent, intent) tuples.
#[pyfunction]
fn fcbo_fast_generate_from_py(
    n_objects: usize,
    n_properties: usize,
    extents: Vec<u128>,
    intents: Vec<u128>,
) -> Vec<(u128, u128)> {
    let ctx = FcaContext::new(n_objects, n_properties, extents, intents);
    fcbo_fast_generate_from(&ctx)
}

/// FCBO dual algorithm.
///
/// Args:
///     n_objects: Number of objects in the context.
///     n_properties: Number of properties in the context.
///     extents: List of integers representing extents (column bitsets).
///     intents: List of integers representing intents (row bitsets).
///
/// Returns:
///     List of (extent, intent) tuples.
#[pyfunction]
fn fcbo_dual_py(
    n_objects: usize,
    n_properties: usize,
    extents: Vec<u128>,
    intents: Vec<u128>,
) -> Vec<(u128, u128)> {
    let ctx = FcaContext::new(n_objects, n_properties, extents, intents);
    fcbo_dual(&ctx)
}

/// A Python module implemented in Rust for FCA lattice generation.
#[pymodule]
fn concepts_rust(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(lindig_lattice_py, m)?)?;
    m.add_function(wrap_pyfunction!(fcbo_fast_generate_from_py, m)?)?;
    m.add_function(wrap_pyfunction!(fcbo_dual_py, m)?)?;
    Ok(())
}
