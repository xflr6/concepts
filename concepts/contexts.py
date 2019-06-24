# contexts.py - create FCA context and provide derivation and neighbors

"""Formal Concept Analysis contexts."""

import heapq

from ._compat import py3_unicode_to_str, string_types, map

from . import formats, matrices, tools, definitions, junctors, lattices

__all__ = ['Context']


@py3_unicode_to_str
class Context(object):
    """Formal context defining a relation between objects and properties.

    Example:
        >>> Context(['man', 'woman'], ['male', 'female'], [(True, False), (False, True)])  # doctest: +ELLIPSIS
        <Context object mapping 2 objects to 2 properties [47e29724] at 0x...>

    Usage:

    >>> c = Context.fromstring('''
    ...    |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
    ... 1sg| X|  |  | X|  | X|  X|   |   |  X|
    ... 1pl| X|  |  | X|  | X|   |  X|  X|   |
    ... 2sg|  | X| X|  |  | X|  X|   |   |  X|
    ... 2pl|  | X| X|  |  | X|   |  X|  X|   |
    ... 3sg|  | X|  | X| X|  |  X|   |   |  X|
    ... 3pl|  | X|  | X| X|  |   |  X|  X|   |
    ... ''')

    >>> print(c)  # doctest: +ELLIPSIS
    <Context object mapping 6 objects to 10 properties [b9d20179] at 0x...>
           |+1|-1|+2|-2|+3|-3|+sg|+pl|-sg|-pl|
        1sg|X |  |  |X |  |X |X  |   |   |X  |
        1pl|X |  |  |X |  |X |   |X  |X  |   |
        2sg|  |X |X |  |  |X |X  |   |   |X  |
        2pl|  |X |X |  |  |X |   |X  |X  |   |
        3sg|  |X |  |X |X |  |X  |   |   |X  |
        3pl|  |X |  |X |X |  |   |X  |X  |   |


    >>> c.objects
    ('1sg', '1pl', '2sg', '2pl', '3sg', '3pl')

    >>> c.properties
    ('+1', '-1', '+2', '-2', '+3', '-3', '+sg', '+pl', '-sg', '-pl')

    >>> c.bools  # doctest: +NORMALIZE_WHITESPACE
    [(True, False, False, True, False, True, True, False, False, True),
     (True, False, False, True, False, True, False, True, True, False),
     (False, True, True, False, False, True, True, False, False, True),
     (False, True, True, False, False, True, False, True, True, False),
     (False, True, False, True, True, False, True, False, False, True),
     (False, True, False, True, True, False, False, True, True, False)]


    >>> c.intension(['1sg'])
    ('+1', '-2', '-3', '+sg', '-pl')

    >>> c.extension(['+1'])
    ('1sg', '1pl')


    >>> c.neighbors(['1sg', '1pl', '2pl'])
    [(('1sg', '1pl', '2sg', '2pl', '3sg', '3pl'), ())]


    >>> c['1sg',]
    (('1sg',), ('+1', '-2', '-3', '+sg', '-pl'))

    >>> c['1sg', '1pl', '2pl']
    (('1sg', '1pl', '2sg', '2pl'), ('-3',))

    >>> c['-1', '-sg']
    (('2pl', '3pl'), ('-1', '+pl', '-sg'))


    >>> print(c.relations())
    +sg equivalent   -pl
    +pl equivalent   -sg
    +1  complement   -1
    +2  complement   -2
    +3  complement   -3
    +sg complement   +pl
    +sg complement   -sg
    +pl complement   -pl
    -sg complement   -pl
    +1  incompatible +2
    +1  incompatible +3
    +2  incompatible +3
    +1  implication  -2
    +1  implication  -3
    +2  implication  -1
    +3  implication  -1
    +2  implication  -3
    +3  implication  -2
    -1  subcontrary  -2
    -1  subcontrary  -3
    -2  subcontrary  -3

    >>> c.definition() == (c.objects, c.properties, c.bools)
    True
    """

    @classmethod
    def fromstring(cls, source, frmat='table', **kwargs):
        """Return a new context from string ``source`` in given format."""
        frmat = formats.Format[frmat]
        objects, properties, bools = frmat.loads(source, **kwargs)
        return cls(objects, properties, bools)

    @classmethod
    def fromfile(cls, filename, frmat='cxt', encoding=None, **kwargs):
        """Return a new context from file source in given format."""
        if frmat is None:
            frmat = formats.Format.infer_format(filename)

        frmat = formats.Format[frmat]
        objects, properties, bools = frmat.load(filename, encoding, **kwargs)
        return cls(objects, properties, bools)

    @classmethod
    def fromjson(cls, path_or_fileobj, encoding='utf-8',
                 ignore_lattice=False, require_lattice=False, raw=False):
        """Return a new context from json path or file-like object.

        Args:
            path_or_fileobj:
            encoding:
            ignore_lattice (bool): don't load lattice from json
            require_lattice (bool): raise if no lattice in json
            raw (bool): if set, sort so the input sequences can be in any order;
                        if unset (default), assume input is already ordered for speedup
        """
        d = tools.load_json(path_or_fileobj, encoding=encoding)
        return cls.fromdict(d,
                            ignore_lattice=ignore_lattice,
                            require_lattice=require_lattice, raw=raw)

    @classmethod
    def fromdict(cls, d, ignore_lattice=False, require_lattice=False, raw=False):
        """Return a new context from dict ``d``.

        Args:
            d (dict): serialized context with optional ``'lattice'``
            ignore_lattice (bool): don't load lattice from ``d``
            require_lattice (bool): raise if no lattice in ``d``
            raw (bool): if set, sort so the input sequences can be in any order;
                        if unset (default), assume input is already ordered for speedup
        Returns: new :class:`concepts.Context` instance
        """
        required_keys = ('objects', 'properties', 'context')
        try:
            args = [d[k] for k in required_keys]
        except KeyError:
            missing = [k for k in required_keys if k not in d]
            raise ValueError('missing required keys in fromdict: %r' % missing)
        else:
            objects, properties, context = args

        for name, values in zip(['objects', 'properties'], args[:2]):
            if not all(isinstance(v, string_types) for v in values):
                raise ValueError('non-string %s in %r' % (name, values))

        if len(context) != len(objects):
            raise ValueError('mismatch: %r objects with %r'
                             ' context rows: ' % (len(objects),
                                                 len(context)))

        if require_lattice:
            try:
                lattice = d['lattice']
            except KeyError:
                raise ValueError('missing lattice with required_lattice')
        else:
            lattice = d.get('lattice')
        if lattice is not None and not lattice:
            raise ValueError('empty lattice')

        indexes = tuple(range(len(properties)))

        def _make_set(r, indexes=set(indexes)):
            result = set(r)
            if len(result) != len(r):
                raise ValueError('context contains duplicated values')
            if not result.issubset(indexes):
                raise ValueError('context contains invalid index')
            return result

        bools = [tuple(i in intent for i in indexes)
                 for intent in map(_make_set, context)]

        inst = cls(objects, properties, bools)

        if not ignore_lattice and lattice is not None:
            assert 'lattice' not in inst.__dict__
            inst.lattice = lattices.Lattice._fromlist(inst, lattice, raw)
        return inst

    def __init__(self, objects, properties, bools):
        """Create context from ``objects``, ``properties``, and correspondence."""
        objects, properties = map(tuple, (objects, properties))

        for items, name in [(objects, 'objects'), (properties, 'properties')]:
            if not items:
                raise ValueError('empty %s' % name)
            if len(set(items)) != len(items):
                raise ValueError('duplicate %s: %r' % (name, items))

        if not set(objects).isdisjoint(properties):
            raise ValueError('objects and properties overlap: '
                             '%r' % (set(objects) & set(properties)))

        if (len(bools) != len(objects)
            or {len(b) for b in bools} != {len(properties)}):
            raise ValueError('bools is not %d items '
                             'of length %d' % (len(objects), len(properties)))

        self._intents, self._extents = matrices.Relation('Intent', 'Extent',
                                                         properties, objects,
                                                         bools)

        self._Intent = self._intents.BitSet
        self._Extent = self._extents.BitSet

    def __getstate__(self):
        """Pickle context as ``(intents, extents)`` tuple."""
        return self._intents, self._extents

    def __setstate__(self, state):
        """Unpickle context from ``(intents, extents)`` tuple."""
        self._intents, self._extents = state
        self._Intent = self._intents.BitSet
        self._Extent = self._extents.BitSet

    def __eq__(self, other):
        if not isinstance(other, Context):
            return NotImplemented

        return (self.objects == other.objects
                and self.properties == other.properties
                and self.bools == other.bools)

    def __ne__(self, other):
        if not isinstance(other, Context):
            return NotImplemented

        return not self == other

    def _minimal(self, extent, intent):
        """Return short lexicograpically minimum intent generating extent."""
        return next(self._minimize(extent, intent))

    def _minimize(self, extent, intent):
        """Yield short lexicograpically ordered extent generating intents."""
        if not extent:
            yield intent
            return

        for it in intent.powerset():
            if it.prime() == extent:
                yield it

    def _neighbors(self, objects):
        """Yield upper neighbors from extent (in colex order?).

        cf. C. Lindig. 2000. Fast Concept Analysis.
        """
        doubleprime = self._extents.doubleprime
        minimal = ~objects
        for add in self._Extent.atomic(minimal):
            objects_ = objects | add
            extent, intent = doubleprime(objects_)
            if minimal & extent & ~objects_:
                minimal &= ~add
            else:
                yield extent, intent

    def _lattice(self, infimum=()):
        """Yield ``(extent, indent, upper, lower)`` in short lexicographic order.

        cf. C. Lindig. 2000. Fast Concept Analysis.
        """
        extent, intent = self._Extent.frommembers(infimum).doubleprime()
        concept = (extent, intent, [], [])
        heap = [(extent.shortlex(), concept)]
        push, pop = heapq.heappush, heapq.heappop
        mapping = {extent: concept}
        while heap:
            concept = pop(heap)[1]
            for extent, intent in self._neighbors(concept[0]):
                if extent in mapping:
                    neighbor = mapping[extent]
                else:
                    neighbor = mapping[extent] = (extent, intent, [], [])
                    push(heap, (extent.shortlex(), neighbor))
                concept[2].append(neighbor[0])
                neighbor[3].append(concept[0])
            yield concept  # concept[3] keeps growing until exhaustion

    def intension(self, objects, raw=False):
        """Return all properties shared by the given ``objects``."""
        intent = self._Extent.frommembers(objects).prime()
        if raw:
            return intent
        return intent.members()

    def extension(self, properties, raw=False):
        """Return all objects sharing the given ``properties``."""
        extent = self._Intent.frommembers(properties).prime()
        if raw:
            return extent
        return extent.members()

    def neighbors(self, objects, raw=False):
        """Return the upper neighbors of the concept having all given ``objects``."""
        objects = self._Extent.frommembers(objects).double()
        if raw:
            return list(self._neighbors(objects))
        return [(extent.members(), intent.members())
                for extent, intent in self._neighbors(objects)]

    def __getitem__(self, items, raw=False):
        """Return ``(extension, intension)`` pair by shared objects or properties."""
        try:
            extent = self._Extent.frommembers(items)
        except KeyError:
            intent = self._Intent.frommembers(items)
            intent, extent = intent.doubleprime()
        else:
            extent, intent = extent.doubleprime()

        if raw:
            return extent, intent
        return extent.members(), intent.members()

    def __str__(self):
        return '%r\n%s' % (self, self.tostring(escape=True, indent=4))

    def __unicode__(self):
        return '%r\n%s' % (self, self.tostring(indent=4))

    def __repr__(self):
        return ('<%s object mapping %d objects to %d properties'
                ' [%s] at %#x>') % (self.__class__.__name__,
                                    len(self._Extent._members),
                                    len(self._Intent._members),
                                    self.crc32(), id(self))

    def todict(self, include_lattice=None):
        """Return serialized context with optional lattice.

        Args:
            include_lattice (bool): include ``'lattice'`` in result
        Returns: new ``dict`` with serialized context
        """
        result = {
            u'objects': self.objects,
            u'properties': self.properties,
            u'context': self._intents.index_sets(),
        }
        if (include_lattice
            or include_lattice is None and u'lattice' in self.__dict__):
            result[u'lattice'] = self.lattice._tolist()
        return result

    def tojson(self, path_or_fileobj, encoding='utf-8', include_lattice=None):
        """Write serialized context as json to path or file-like object.

        Args:
            path_or_fileobj: 
            include_lattice (bool): include ``'lattice'`` in result
        """
        d = self.todict(include_lattice=include_lattice)
        tools.dump_json(d, path_or_fileobj, encoding=encoding)

    def tostring(self, frmat='table', **kwargs):
        """Return the context serialized in the given string-based format."""
        frmat = formats.Format[frmat]
        return frmat.dumps(self._Extent._members, self._Intent._members,
                           self._intents.bools(), **kwargs)

    def tofile(self, filename, frmat='cxt', encoding='utf-8', **kwargs):
        """Save the context serialized to file in the given format."""
        frmat = formats.Format[frmat]
        return frmat.dump(filename,
                          self._Extent._members, self._Intent._members,
                          self._intents.bools(), encoding, **kwargs)

    def crc32(self, encoding='utf-8'):
        """Return hex-encoded unsigned CRC32 over encoded context table string."""
        return tools.crc32_hex(self.tostring().encode(encoding))

    @property
    def objects(self):
        """(Names of the) objects described by the context."""
        return self._Extent._members

    @property
    def properties(self):
        """(Names of the) properties that describe the objects."""
        return self._Intent._members

    @property
    def bools(self):
        """Row-wise boolean relation matrix between objects and properties."""
        return self._intents.bools()

    def definition(self):
        """Return ``(objects, properties, bools)`` triple as mutable object."""
        return definitions.Definition(self._Extent._members,
                                      self._Intent._members,
                                      self._intents.bools())

    def relations(self, include_unary=False):
        """Return the logical relations between the context properties."""
        return junctors.Relations(self.properties,
                                  self._extents.bools(),
                                  include_unary)

    @tools.lazyproperty
    def lattice(self):
        """The concept lattice of the formal context."""
        return lattices.Lattice(self)
