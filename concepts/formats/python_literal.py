import ast
import functools

from .base import SerializedArgs, Format

__all__ = ['PythonLiteral']


def load_file(file) -> SerializedArgs:
    python_source = file.read()
    args = ast.literal_eval(python_source)
    assert args is not None
    assert isinstance(args, dict)

    objects = args['objects']
    properties = args['properties']

    bools = [[False for _ in args['properties']]
             for _ in args['objects']]
    for row, true_indexes in zip(bools, args['context']):
        for i in true_indexes:
            row[i] = True
    bools = [tuple(row) for row in bools]

    return SerializedArgs(objects, properties, bools, serialized=args)


def dump_file(file, objects, properties, bools, *, _serialized=None) -> None:
    if _serialized is None:
        doc = {'objects': objects,
               'properties': properties,
               'context': [tuple(i for i, b in enumerate(row) if b)
                           for row in bools]}
    else:
        doc = _serialized
        assert isinstance(doc, dict)
        keys = ('objects', 'properties', 'context')
        assert all(k in doc for k in keys)

    indent = ' ' * 2

    def itersection(key, lines, value_list: bool = False):
        start, end = ('[', ']') if value_list else ('(', ')')

        yield f'{indent}{key!r}: {start}'
        yield from lines
        yield f'{indent}{end},'

    def iterlines(doc):
        yield '{'

        for key in ('objects', 'properties'):
            line = ', '.join(map(repr, doc[key]))
            yield from itersection(key, [f'{indent * 2}{line},'])

        for key in ('context',) + (('lattice',) if 'lattice' in doc else ()):
            lines = [f'{indent * 2}{line},' for line in map(repr, doc[key])]
            yield from itersection(key, lines, value_list=True)

        yield '}'

    write = functools.partial(print, file=file)
    for line in iterlines(doc):
        write(line)


class PythonLiteral(Format):
    """Format context as input for ``ast.literal_eval()``."""

    suffix = '.py'

    dumps_rstrip = True

    loadf = staticmethod(load_file)

    dumpf = staticmethod(dump_file)
