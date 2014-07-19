# definitions.py - mutable triples of object, properties, bools

"""Mutable formal context creation arguments with set-like operations."""

from ._compat import zip, py3_unicode_to_str

from . import formats, tools

__all__ = ['Definition']


@py3_unicode_to_str
class BaseDefinition(object):
    """Triple of (objects, properties, bools) for creating a context.

    >>> d = BaseDefinition(['Mr. Praline', 'parrot'], ['alive', 'dead'],
    ...     [(True, False), (False, True)])

    >>> d  # doctest: +NORMALIZE_WHITESPACE
    <BaseDefinition(['Mr. Praline', 'parrot'], ['alive', 'dead'],
        [(True, False), (False, True)])>

    >>> print(d)
               |alive|dead|
    Mr. Praline|X    |    |
    parrot     |     |X   |

    >>> tuple(d)
    (('Mr. Praline', 'parrot'), ('alive', 'dead'), [(True, False), (False, True)])

    >>> (d[0], d[1], d[2]) == (d.objects, d.properties, d.bools)
    True

    >>> d == (d.objects, d.properties, d.bools)
    True


    >>> d['Mr. Praline', 'alive']
    True

    >>> d['parrot', 'alive']
    False


    >>> d.take(['parrot'])
    <BaseDefinition(['parrot'], ['alive', 'dead'], [(False, True)])>

    >>> d.take(properties=['dead'])
    <BaseDefinition(['Mr. Praline', 'parrot'], ['dead'], [(False,), (True,)])>

    >>> d.take(['Brian'], ['alive', 'holy'])
    Traceback (most recent call last):
        ...
    KeyError: ['Brian', 'holy']

    >>> d.take(['parrot', 'Mr. Praline'], ['alive'], reorder=True)
    <BaseDefinition(['parrot', 'Mr. Praline'], ['alive'], [(False,), (True,)])>


    >>> print(d.transposed())
         |Mr. Praline|parrot|
    alive|X          |      |
    dead |           |X     |

    >>> print(d.inverted())
               |alive|dead|
    Mr. Praline|     |X   |
    parrot     |X    |    |
    """

    @classmethod
    def fromfile(cls, filename, frmat='cxt', encoding=None, **kwargs):
        """Return a new definiton from file source in given format."""
        frmat = formats.Format[frmat]
        objects, properties, bools = frmat.load(filename, encoding, **kwargs)
        return cls(objects, properties, bools)

    @classmethod
    def _fromargs(cls, _objects, _properties, _map):
        inst = super(BaseDefinition, cls).__new__(cls)
        inst._objects = _objects
        inst._properties = _properties
        inst._map = _map
        return inst

    def __init__(self, objects=(), properties=(), bools=()):
        self._objects = tools.Unique(objects)
        if len(self._objects) != len(objects):
            raise ValueError('Duplicate objects: %r' % (objects,))
        self._properties = tools.Unique(properties)
        if len(self._properties) != len(properties):
            raise ValueError('Duplicate properties: %r' % (properties,))
        self._map = {(o, p): b for o, boo in zip(objects, bools)
            for p, b in zip(properties, boo) if b}

    def copy(self):
        return self._fromargs(self._objects.copy(), self._properties.copy(),
            self._map.copy())

    def __iter__(self):
        yield self.objects
        yield self.properties
        yield self.bools

    def __getitem__(self, pair):
        if isinstance(pair, int):
            return list(self)[pair]
        o, p = pair
        if o not in self._objects or p not in self._properties:
            raise KeyError(pair)
        return self._map.get(pair, False)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self._objects == other._objects and
                self._properties == other._properties and
                self.bools == other.bools)
        return (self.objects, self.properties, self.bools) == other

    def __ne__(self, other):
        return not self == other

    @property
    def objects(self):
        return tuple(self._objects)

    @property
    def properties(self):
        return tuple(self._properties)

    @property
    def bools(self):
        prop = self._properties
        get_value = self._map.get
        return [tuple(get_value((o, p), False) for p in prop)
            for o in self._objects]

    def __str__(self):
        return self.tostring(escape=True)

    def __unicode__(self):
        return self.tostring()

    def __repr__(self):
        return '<%s(%r, %r, %r)>' % (self.__class__.__name__,
            self._objects._items, self._properties._items, self.bools)

    def tostring(self, frmat='table', **kwargs):
        return formats.Format[frmat].dumps(*self, **kwargs)

    def take(self, objects=(), properties=(), reorder=False):
        """Return a subset with given objects/properties as new definition."""
        if (not self._objects.issuperset(objects) or
            not self._properties.issuperset(properties)):
            notfound = self._objects.rsub(objects) | self._properties.rsub(properties)
            raise KeyError(list(notfound))
        if reorder:
            obj = tools.Unique(objects) if objects else self._objects.copy()
            prop = tools.Unique(properties) if properties else self._properties.copy()
        else:
            obj = self._objects.copy()
            prop = self._properties.copy()
            if objects:
                obj &= objects
            if properties:
                prop &= properties
        values = self._map
        _map = {(o, p): values[(o, p)] for o in obj for p in prop
            if (o, p) in values}
        return self._fromargs(obj, prop, _map)

    def transposed(self):
        """Return a new definition swapping objects and properties."""
        bools = zip(*self.bools)
        return self.__class__(self._properties, self._objects, bools)

    def inverted(self):
        """Return a new definition flipping all booleans."""
        bools = ((not b for b in boo) for boo in self.bools)
        return self.__class__(self._objects, self._properties, bools)

    __invert__ = inverted


def conflicting_pairs(left, right):
    """Yield all (object, property) pairs where the two definitions disagree."""
    objects = left._objects & right._objects
    properties = left._properties & right._properties
    left_value, right_value = left._map.get, right._map.get
    for o in objects:
        for p in properties:
            pair = (o, p)
            if left_value(pair, False) != right_value(pair, False):
                yield pair


class Definition(BaseDefinition):
    """Mutable triple of (objects, properties, bools) for creating a context.

    >>> d = Definition()

    >>> d
    <Definition([], [], [])>

    >>> d.add_object('King Arthur')

    >>> print(d)
               |
    King Arthur|

    >>> d.add_object('Sir Robin', ['human', 'knight'])
    >>> d.add_object('holy grail')

    >>> print(d)
               |human|knight|
    King Arthur|     |      |
    Sir Robin  |X    |X     |
    holy grail |     |      |

    >>> d.add_object('King Arthur', ['human', 'knight', 'king'])
    >>> d.add_property('mysterious', ['holy grail', 'Sir Robin'])

    >>> print(d)
               |human|knight|king|mysterious|
    King Arthur|X    |X     |X   |          |
    Sir Robin  |X    |X     |    |X         |
    holy grail |     |      |    |X         |

    >>> d['Sir Robin', 'mysterious'] = False

    >>> print(d)
               |human|knight|king|mysterious|
    King Arthur|X    |X     |X   |          |
    Sir Robin  |X    |X     |    |          |
    holy grail |     |      |    |X         |


    >>> e = d.copy()
    >>> e.rename_object('Sir Robin', 'Launcelot')
    >>> e.add_property('brave', ['Launcelot'])
    >>> e.rename_object('holy grail', 'grail')
    >>> e.rename_property('mysterious', 'holy')

    >>> print(e)
               |human|knight|king|holy|brave|
    King Arthur|X    |X     |X   |    |     |
    Launcelot  |X    |X     |    |    |X    |
    grail      |     |      |    |X   |     |

    >>> print(e & d)
               |human|knight|king|
    King Arthur|X    |X     |X   |

    >>> print(e | d)
               |human|knight|king|holy|brave|mysterious|
    King Arthur|X    |X     |X   |    |     |          |
    Launcelot  |X    |X     |    |    |X    |          |
    grail      |     |      |    |X   |     |          |
    Sir Robin  |X    |X     |    |    |     |          |
    holy grail |     |      |    |    |     |X         |

    >>> e.remove_object('grail')
    >>> e.remove_property('holy')
    >>> e.rename_object('King Arthur', 'Arthur')
    >>> e.set_property('king', [])
    >>> e.set_object('Launcelot', ['human'])

    >>> print(e)
             |human|knight|king|brave|
    Arthur   |X    |X     |    |     |
    Launcelot|X    |      |    |     |

    >>> e.set_property('knight', ['Launcelot'])

    >>> print(e)
             |human|knight|king|brave|
    Arthur   |X    |      |    |     |
    Launcelot|X    |X     |    |     |
    """

    def rename_object(self, old, new):
        """Replace the name of an object by a new one."""
        self._objects.replace(old, new)
        values, pop = self._map, self._map.pop
        self._map.update({(new, p): pop((old, p)) for p in self._properties
            if (old, p) in values})

    def rename_property(self, old, new):
        """Replace the name of a property by a new one."""
        self._properties.replace(old, new)
        values, pop = self._map, self._map.pop
        self._map.update({(o, new): pop((o, old)) for o in self._objects
            if (o, old) in values})

    def __setitem__(self, pair, value):
        if isinstance(pair, int):
            raise ValueError('Cannot assign item.')
        o, p = pair
        self._objects.add(o)
        self._properties.add(p)
        if value:
            self._map[pair] = True
        else:
            self._map.pop(pair, None)

    def add_object(self, obj, properties=()):
        """Add an object to the definition and add properties as related."""
        self._objects.add(obj)
        self._properties |= properties
        self._map.update(((obj, p), True) for p in properties)

    def add_property(self, prop, objects=()):
        """Add a property to the definition and add objects as related."""
        self._properties.add(prop)
        self._objects |= objects
        self._map.update(((o, prop), True) for o in objects)

    def remove_object(self, obj):
        """Remove an object from the definition."""
        self._objects.remove(obj)
        pop = self._map.pop
        for p in self._properties:
            pop((obj, p), None)

    def remove_property(self, prop):
        """Remove a property from the definition."""
        self._properties.remove(prop)
        pop = self._map.pop
        for o in self._objects:
            pop((o, prop), None)

    def set_object(self, obj, properties):
        """Add an object to the definition and set its properties."""
        self._objects.add(obj)
        properties = set(properties)
        self._properties |= properties
        values = self._map
        for p in self._properties:
            if p in properties:
                values[(obj, p)] = True
            else:
                values.pop((obj, p), None)

    def set_property(self, prop, objects):
        """Add a property to the definition and set its objects."""
        self._properties.add(prop)
        objects = set(objects)
        self._objects |= objects
        values = self._map
        for o in self._objects:
            if o in objects:
                values[(o, prop)] = True
            else:
                values.pop((o, prop), None)

    def union_update(self, other, ignore_conflicts=False):
        """Update the definition with the union of ther other."""
        conflicts = list(conflicting_pairs(self, other))
        if conflicts and not ignore_conflicts:
            raise ValueError('Conflicting values for object/property pairs: %r' % conflicts)
        self._objects |= other._objects
        self._properties |= other._properties
        self._map.update(other._map)
        self._map.update((pair, True) for pair in conflicts)

    def intersection_update(self, other, ignore_conflicts=False):
        """Update the definition with the intersection of ther other."""
        conflicts = list(conflicting_pairs(self, other))
        if conflicts and not ignore_conflicts:
            raise ValueError('Conflicting values for object/property pairs: %r' % conflicts)
        self._objects &= other._objects
        self._properties &= other._properties
        self._map.update(other._map)
        pop = self._map.pop
        for pair in conflicts:
            pop(pair, None)

    __ior__ = union_update
    __and__ = intersection_update

    def union(self, other, ignore_conflicts=False):
        """Return a new definition from the union of the definitions."""
        result = self.copy()
        result.union_update(other, ignore_conflicts)
        return result

    def intersection(self, other, ignore_conflicts=False):
        """Return a new definition from the intersection of the definitions."""
        result = self.copy()
        result.intersection_update(other, ignore_conflicts)
        return result

    __or__ = union
    __and__ = intersection
