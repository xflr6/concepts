"""Mutable formal context creation arguments (object, properties, bools) with set-like operations."""

import typing

from . import formats
from . import tools
from . import contexts

__all__ = ['Definition']


StrSequence = typing.Sequence[str]


class Triple:
    """Triple of ``(objects, properties, bools)`` for creating a context."""

    @classmethod
    def fromfile(cls, filename,
                 frmat: str = 'cxt',
                 encoding: typing.Optional[str] = None, **kwargs):
        """Return a new definiton from file source in given format.

        Args:
            filename: Path to the file to load the context from.
            frmat: File format (``'table'``, ``'cxt'``, ``'csv'``).
            encoding: File encoding (``'utf-8'``, ``'latin1'``, ``'ascii'``, ...).

        Returns:
            Definition: A new :class:`.Definition` instance.
        """
        frmat = formats.Format[frmat]
        args = frmat.load(filename, encoding, **kwargs)
        return cls(args.objects, args.properties, args.bools)

    @classmethod
    def _fromargs(cls, _objects, _properties, _pairs):
        inst = super().__new__(cls)
        inst._objects = _objects
        inst._properties = _properties
        inst._pairs = _pairs
        return inst

    def __init__(self,
                 objects: StrSequence = (),
                 properties: StrSequence = (),
                 bools: typing.Sequence[typing.Sequence[bool]] = ()):
        self._objects = tools.Unique(objects)
        if len(self._objects) != len(objects):
            raise ValueError(f'duplicate objects: {objects!r}')

        self._properties = tools.Unique(properties)
        if len(self._properties) != len(properties):
            raise ValueError(f'duplicate properties: {properties!r}')

        self._pairs = {(o, p) for o, boo in zip(objects, bools)
                       for p, b in zip(properties, boo) if b}

    def copy(self):
        """Return an independent copy of the instance.

        Returns:
            An instance of ``type(self)``.
        """
        return self._fromargs(self._objects.copy(),
                              self._properties.copy(),
                              self._pairs.copy())

    def __eq__(self, other) -> bool:
        """Return whether two definitions are equivalent.

        Args:
            other (Definition): Another :class:`.Definition` instance.

        Returns:
            ``True`` if the definitions are equal, ``False`` otherwise.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> definition == (definition.objects,
            ...                definition.properties,
            ...                definition.bools)
            True
        """
        if isinstance(other, Triple):  # order insensitive
            return (self._objects == other._objects
                    and self._properties == other._properties
                    and self._pairs == other._pairs)
        return (self.objects, self.properties, self.bools) == other

    def __ne__(self, other) -> bool:
        """Return whether two definitions are inequivalent.

        Args:
            other (Definition): Another :class:`.Definition` instance.

        Returns:
            ``True`` if the definitions are unequal, ``False`` otherwise.
        """
        return not self == other

    def __iter__(self):
        """Yield ``objects``, ``properties``, and ``bools`` (e.g. for triple unpacking).

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> list(definition)  # doctest: +NORMALIZE_WHITESPACE
            [('Mr. Praline', 'parrot'),
             ('alive', 'dead'),
             [(True, False), (False, True)]]
        """
        yield self.objects
        yield self.properties
        yield self.bools

    def __getitem__(self, pair) -> bool:
        """Return the relation value for an (object, property) pair.

        Returns:
            ``True`` if ``object`` has ``property`` else ``False``.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> definition['Mr. Praline', 'alive']
            True
            >>> definition['parrot', 'alive']
            False
            >>> (definition[0],
            ...  definition[1],
            ...  definition[2]) == (definition.objects,
            ...                     definition.properties,
            ...                     definition.bools)
            True
        """
        if isinstance(pair, int):
            return list(self)[pair]

        o, p = pair
        if o not in self._objects or p not in self._properties:
            raise KeyError(pair)
        return pair in self._pairs

    @property
    def objects(self) -> typing.Tuple[str, ...]:
        """(Names of the) objects described by the definition.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> definition.objects
            ('Mr. Praline', 'parrot')
        """
        return tuple(self._objects)

    @property
    def properties(self) -> typing.Tuple[str, ...]:
        """(Names of the) properties that describe the objects.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> definition.properties
            ('alive', 'dead')
        """
        return tuple(self._properties)

    @property
    def bools(self) -> typing.List[typing.Tuple[bool, ...]]:
        """Row-major :obj:`list` of boolean tuples.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> definition.bools
            [(True, False), (False, True)]
        """
        prop = self._properties
        pairs = self._pairs
        return [tuple((o, p) in pairs for p in prop) for o in self._objects]

    @property
    def shape(self) -> 'contexts.Shape':
        """Return shape/dimensions of the context.

        Returns:
            New :class:`.Shape` instance.

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'grail'],
            ...                                  ['holy'],
            ...                                  [(False,), (True,)])
            >>> definition.shape
            Shape(objects=2, properties=1)
        """
        return contexts.Shape(len(self.objects), len(self.properties))

    def __str__(self) -> str:
        """

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> print(definition)
                       |alive|dead|
            Mr. Praline|X    |    |
            parrot     |     |X   |
        """
        return self.tostring()

    def __repr__(self) -> str:
        """

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> definition  # doctest: +NORMALIZE_WHITESPACE
            <Definition(['Mr. Praline', 'parrot'],
                        ['alive', 'dead'],
                        [(True, False), (False, True)])>
        """
        return (f'<{self.__class__.__name__}('
                f'{self._objects._items!r}, {self._properties._items!r},'
                f' {self.bools!r})>')

    def tostring(self, frmat: str = 'table', **kwargs) -> str:
        """Return the definition serialized in the given string-based format.

        Args:
            frmat: Format of the string (``'table'``, ``'cxt'``, ``'csv'``).

        Returns:
            The definition as seralized string.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> print(definition.tostring())
                       |alive|dead|
            Mr. Praline|X    |    |
            parrot     |     |X   |
        """
        return formats.Format[frmat].dumps(*self, **kwargs)

    def crc32(self, *, encoding: str = 'utf-8') -> str:
        """Return hex-encoded unsigned CRC32 over encoded definition table string.

        Args:
            encoding: Encoding of the serialzation (``'utf-8'``, ``'latin1'``, ``'ascii'``, ...).

        Returns:
            The unsigned CRC32 checksum as hex-string.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> definition.crc32()
            '9642849e'
        """
        return tools.crc32_hex(self.tostring().encode(encoding))


class TransformableMixin:
    """Transformation-methods for triple of context-creating ``(objects, properties, bools)``."""

    def inverted(self):
        """Return a new definition flipping all booleans.

        Returns:
            Definition: A new :class:`.Definition` instance.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> print(definition.inverted())
                       |alive|dead|
            Mr. Praline|     |X   |
            parrot     |X    |    |

        """
        pairs = self._pairs
        return self._fromargs(self._objects.copy(), self._properties.copy(),
                              {(o, p) for o in self._objects for p in self._properties
                               if (o, p) not in pairs})

    __invert__ = inverted

    def transposed(self):
        """Return a new definition swapping ``objects`` and ``properties``.

        Returns:
            Definition: A new :class:`.Definition` instance.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> print(definition.transposed())
                 |Mr. Praline|parrot|
            alive|X          |      |
            dead |           |X     |
        """
        return self._fromargs(self._properties.copy(), self._objects.copy(),
                              {(p, o) for (o, p) in self._pairs})

    __neg__ = transposed

    def take(self,
             objects: typing.Optional[StrSequence] = None,
             properties: typing.Optional[StrSequence] = None,
             reorder: bool = False):
        """Return a subset with given ``objects``/``properties`` as new definition.

        Args:
            objects: Object names.
            properties: Property names.
            reorder: Return subset in ``objects`` and ``properties`` order.

        Returns:
            Definition: A new :class:`.Definition` instance.

        Example:
            >>> from concepts import Definition
            >>> definition = Definition(['Mr. Praline', 'parrot'],
            ...                         ['alive', 'dead'],
            ...                         [(True, False), (False, True)])
            >>> definition.take(['parrot'])
            <Definition(['parrot'], ['alive', 'dead'], [(False, True)])>
            >>> definition.take(properties=['dead'])
            <Definition(['Mr. Praline', 'parrot'], ['dead'], [(False,), (True,)])>
            >>> definition.take(['Brian'], ['alive', 'holy'])
            Traceback (most recent call last):
                ...
            KeyError: ['Brian', 'holy']
            >>> definition.take(['parrot', 'Mr. Praline'], ['alive'], reorder=True)
            <Definition(['parrot', 'Mr. Praline'], ['alive'], [(False,), (True,)])>
        """
        if (objects and not self._objects.issuperset(objects)
            or properties and not self._properties.issuperset(properties)):
            notfound = (self._objects.rsub(objects or ())
                        | self._properties.rsub(properties or ()))
            raise KeyError(list(notfound))

        if reorder:
            obj = tools.Unique(objects) if objects is not None else self._objects.copy()
            prop = tools.Unique(properties) if properties is not None else self._properties.copy()
        else:
            obj = self._objects.copy()
            prop = self._properties.copy()
            if objects is not None:
                obj &= objects
            if properties is not None:
                prop &= properties
        pairs = self._pairs
        return self._fromargs(obj, prop,
                              {(o, p) for o in obj for p in prop
                               if (o, p) in pairs})


def conflicting_pairs(left, right):
    """Yield all ``(object, property)`` pairs where the two definitions disagree."""
    objects = left._objects & right._objects
    properties = left._properties & right._properties
    difference = left._pairs ^ right._pairs
    for o in objects:
        for p in properties:
            if (o, p) in difference:
                yield (o, p)


def ensure_compatible(left, right):
    """Raise an informative ``ValueError`` if the two definitions disagree."""
    conflicts = list(conflicting_pairs(left, right))
    if conflicts:
        raise ValueError('conflicting values for object/property pairs:'
                         f' {conflicts!r}')


class MutableMixin:
    """Mutation-methods for triple of context-creating ``(objects, properties, bools)``."""

    def __setitem__(self, pair, value) -> None:
        """

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'grail'],
            ...                                  ['holy'],
            ...                                  [(False,), (True,)])
            >>> definition['King Arthur', 'holy'] = True
            >>> print(definition)
                       |holy|
            King Arthur|X   |
            grail      |X   |
            >>> definition['King Arthur', 'holy'] = False
            >>> print(definition)
                       |holy|
            King Arthur|    |
            grail      |X   |
        """
        if isinstance(pair, int):
            raise ValueError("can't set item")
        o, p = pair
        self._objects.add(o)
        self._properties.add(p)
        if value:
            self._pairs.add(pair)
        else:
            self._pairs.discard(pair)

    def rename_object(self, old: str, new: str) -> None:
        """Replace the name of an object by a new one.

        Args:
            old: Current name of the object.
            new: New name for the object.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'holy grail'],
            ...                                  ['human'],
            ...                                  [(True,), (False,)])
            >>> definition.rename_object('holy grail', 'grail')
            >>> print(definition)
                       |human|
            King Arthur|X    |
            grail      |     |
        """
        self._objects.replace(old, new)
        pairs = self._pairs
        pairs |= {(new, p) for p in self._properties
                  if (old, p) in pairs and not pairs.remove((old, p))}

    def rename_property(self, old: str, new: str) -> None:
        """Replace the name of a property by a new one.

        Args:
            old: Current name of the property.
            new: New name for the property.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'grail'],
            ...                                  ['holy'],
            ...                                  [(False,), (True,)])
            >>> definition.rename_property('holy', 'mysterious')
            >>> print(definition)
                       |mysterious|
            King Arthur|          |
            grail      |X         |
        """
        self._properties.replace(old, new)
        pairs = self._pairs
        pairs |= {(o, new) for o in self._objects
                  if (o, old) in pairs and not pairs.remove((o, old))}

    def move_object(self, obj: str, index: int) -> None:
        """Reorder the definition such that object is at ``index``.

        Args:
            obj: Name of the object to move.
            index: Index for the object to move to.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'grail'],
            ...                                  ['holy'],
            ...                                  [(False,), (True,)])
            >>> definition.move_object('grail', 0)
            >>> print(definition)
                       |holy|
            grail      |X   |
            King Arthur|    |
        """
        self._objects.move(obj, index)

    def move_property(self, prop: str, index: int) -> None:
        """Reorder the definition such that property is at ``index``.

        Args:
            prop: Name of the property to move.
            index: Index for the property to move to.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur'],
            ...                                  ['human', 'night', 'holy'],
            ...                                  [(True, True, False)])
            >>> definition.move_property('holy', 0)
            >>> print(definition)
                       |holy|human|night|
            King Arthur|    |X    |X    |
        """
        self._properties.move(prop, index)

    def add_object(self, obj: str, properties: StrSequence = ()) -> None:
        """Add an object to the definition and add ``properties`` as related.

        Args:
            obj: Name of the object to add.
            properties: Iterable of property name strings.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition()
            >>> print(definition)
            |
            >>> definition.add_object('King Arthur')
            >>> print(definition)
                       |
            King Arthur|
            >>> definition.add_object('King Arthur', ['human', 'knight', 'king'])
            >>> print(definition)
                       |human|knight|king|
            King Arthur|X    |X     |X   |
        """
        self._objects.add(obj)
        self._properties |= properties
        self._pairs.update((obj, p) for p in properties)

    def add_property(self, prop: str, objects: StrSequence = ()) -> None:
        """Add a property to the definition and add ``objects`` as related.

        Args:
            prop: Name of the property to add.
            objects: Iterable of object name strings.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition()
            >>> print(definition)
            |
            >>> definition.add_property('mysterious')
            >>> print(definition)
            |mysterious|
            >>> definition.add_property('mysterious', ['holy grail', 'Sir Robin'])
            >>> print(definition)
                      |mysterious|
            holy grail|X         |
            Sir Robin |X         |
        """
        self._properties.add(prop)
        self._objects |= objects
        self._pairs.update((o, prop) for o in objects)

    def remove_object(self, obj: str) -> None:
        """Remove an object from the definition.

        Args:
            obj: Name of the object to remove.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'holy grail'],
            ...                                  ['human'],
            ...                                  [(True,), (False,)])
            >>> definition.remove_object('holy grail')
            >>> print(definition)
                       |human|
            King Arthur|X    |
        """
        self._objects.remove(obj)
        self._pairs.difference_update((obj, p) for p in self._properties)

    def remove_property(self, prop: str) -> None:
        """Remove a property from the definition.

        Args:
            prop: Name of the property to remove.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'holy grail'],
            ...                                  ['human'],
            ...                                  [(True,), (False,)])
            >>> definition.remove_property('human')
            >>> print(definition)
                       |
            King Arthur|
            holy grail |
        """
        self._properties.remove(prop)
        self._pairs.difference_update((o, prop) for o in self._objects)

    def remove_empty_objects(self) -> typing.List[str]:
        """Remove objects without any ``True`` property

        Returns:
            Removed object names.

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'holy grail'],
            ...                                  ['human'],
            ...                                  [(True,), (False,)])
            >>> definition.remove_empty_objects()
            ['holy grail']
            >>> print(definition)
                       |human|
            King Arthur|X    |
            """
        nonempty_objects = {o for o, _ in self._pairs}
        empty_objects = [o for o in self._objects if o not in nonempty_objects]
        for o in empty_objects:
            self._objects.remove(o)
        return empty_objects

    def remove_empty_properties(self) -> typing.List[str]:
        """Remove properties without any ``True`` object.

        Returns:
            Removed property names.

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'holy grail'],
            ...                                  ['moose'],
            ...                                  [(False,), (False,)])
            >>> definition.remove_empty_properties()
            ['moose']
            >>> print(definition)
                       |
            King Arthur|
            holy grail |
        """
        nonempty_properties = {p for _, p in self._pairs}
        empty_properties = [p for p in self._properties if p not in nonempty_properties]
        for p in empty_properties:
            self._properties.remove(p)
        return empty_properties

    def set_object(self, obj: str, properties: StrSequence) -> None:
        """Add an object to the definition and set its ``properties``.

        Args:
            obj: Name of the object to add.
            properties: Property name strings.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'holy grail'],
            ...                                  ['moose'],
            ...                                  [(False,), (True,)])
            >>> definition.set_object('holy grail', ['holy'])
            >>> print(definition)
                       |moose|holy|
            King Arthur|     |    |
            holy grail |     |X   |
        """
        self._objects.add(obj)
        properties = set(properties)
        self._properties |= properties
        pairs = self._pairs
        for p in self._properties:
            if p in properties:
                pairs.add((obj, p))
            else:
                pairs.discard((obj, p))

    def set_property(self, prop: str, objects: StrSequence) -> None:
        """Add a property to the definition and set its ``objects``.

        Args:
            prop: Name of the property to add.
            objects: Iterable of object name strings.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur', 'holy grail'],
            ...                                  ['moose'],
            ...                                  [(False,), (True,)])
            >>> definition.set_property('moose', [])
            >>> print(definition)
                       |moose|
            King Arthur|     |
            holy grail |     |
            >>> definition.set_property('moose', ['King Arthur', 'holy grail'])
            >>> print(definition)
                       |moose|
            King Arthur|X    |
            holy grail |X    |
        """
        self._properties.add(prop)
        objects = set(objects)
        self._objects |= objects
        pairs = self._pairs
        for o in self._objects:
            if o in objects:
                pairs.add((o, prop))
            else:
                pairs.discard((o, prop))

    def union_update(self, other: 'Definition',
                     ignore_conflicts: bool = False) -> None:
        """Update the definition with the union of the ``other``.

        Args:
            other: Another :class:`.Definition` instance.
            ignore_conflicts: Allow overwrite from other.

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur'],
            ...                                  ['human'],
            ...                                  [(True,)])
            >>> other = concepts.Definition(['grail'],
            ...                             ['holy'],
            ...                             [(True,)])
            >>> definition.union_update(other)
            >>> print(definition)
                       |human|holy|
            King Arthur|X    |    |
            grail      |     |X   |
        """
        if not ignore_conflicts:
            ensure_compatible(self, other)
        self._objects |= other._objects
        self._properties |= other._properties
        self._pairs |= other._pairs

    def intersection_update(self, other: 'Definition',
                            ignore_conflicts: bool = False) -> None:
        """Update the definition with the intersection of the ``other``.

        Args:
            other: Another :class:`.Definition` instance.
            ignore_conflicts:  Allow overwrite from other.

        Returns:
            ``None``

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur'],
            ...                                  ['human'],
            ...                                  [(True,)])
            >>> other = concepts.Definition(['King Arthur', 'grail'],
            ...                             ['human', 'holy'],
            ...                             [(True, True), (False, True)])
            >>> definition.intersection_update(other)
            >>> print(definition)
                       |human|
            King Arthur|X    |
        """
        if not ignore_conflicts:
            ensure_compatible(self, other)
        self._objects &= other._objects
        self._properties &= other._properties
        self._pairs &= other._pairs

    def __ior__(self, other: 'Definition') -> 'Definition':
        self.union_update(other)
        return self

    def __iand__(self, other: 'Definition') -> 'Definition':
        self.intersection_update(other)
        return self

    def union(self, other: 'Definition',
              ignore_conflicts: bool = False) -> 'Definition':
        """Return a new definition from the union of the definitions.

        Args:
            other: Another :class:`.Definition` instance.
            ignore_conflicts):

        Returns:
            Definition: A new :class:`.Definition` instance.

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur'],
            ...                                  ['human'],
            ...                                  [(True,)])
            >>> other = concepts.Definition(['grail'],
            ...                             ['holy'],
            ...                             [(True,)])
            >>> print(definition.union(other))
                       |human|holy|
            King Arthur|X    |    |
            grail      |     |X   |

        """
        result = self.copy()
        result.union_update(other, ignore_conflicts)
        return result

    def intersection(self, other: 'Definition',
                     ignore_conflicts: bool = False) -> 'Definition':
        """Return a new definition from the intersection of the definitions.

        Args:
            other: Another :class:`.Definition` instance.
            ignore_conflicts: Allow overwrite from other.

        Returns:
            Definition: A new :class:`.Definition` instance.

        Example:
            >>> import concepts
            >>> definition = concepts.Definition(['King Arthur'],
            ...                                  ['human'],
            ...                                  [(True,)])
            >>> other = concepts.Definition(['King Arthur', 'grail'],
            ...                             ['human', 'holy'],
            ...                             [(True, True), (False, True)])
            >>> print(definition.intersection(other))
                       |human|
            King Arthur|X    |
        """
        result = self.copy()
        result.intersection_update(other, ignore_conflicts)
        return result

    __or__ = union

    __and__ = intersection


class Definition(MutableMixin, TransformableMixin, Triple):
    """Mutable triple of ``(objects, properties, bools)`` for creating a context.

    Create definition from ``objects``, ``properties``, and ``bools`` correspondence.

    Args:
        objects: Object names.
        properties: Property names.
        bools: Row-major sequence of boolean sequences.

    Returns:
        Definition: New :class:`.Definition` instance.

    Example:
        >>> Definition(['man', 'woman'],
        ...            ['male', 'female'],
        ...            [(True, False), (False, True)])
        <Definition(['man', 'woman'], ['male', 'female'], [(True, False), (False, True)])>
        >>> Definition()
        <Definition([], [], [])>
    """
