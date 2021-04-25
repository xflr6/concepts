import functools

from .. import tools

from .base import ContextArgs, Format

__all__ = ['Table']


def load_file(file):
    lines = (line.partition('#')[0].strip() for line in file)
    lines = list(filter(None, lines))
    properties = [p.strip() for p in lines[0].strip('|').split('|')]
    table = [(obj.strip(),
        tuple(bool(f.strip()) for f in flags.strip('|').split('|')))
        for obj, flags in
            (objflags.partition('|')[::2] for objflags in lines[1:])]
    objects, bools = zip(*table)
    return ContextArgs(objects, properties, bools)


def dump_file(file, objects, properties, bools, *, indent=0, _serialized=None):
    wd = [tools.max_len(objects)]
    wd.extend(map(len, properties))
    tmpl = ' ' * indent + '|'.join(f'%-{w:d}s' for w in wd) + '|'

    write = functools.partial(print, file=file)
    write(tmpl % (('',) + tuple(properties)))
    for o, intent in zip(objects, bools):
        write(tmpl % ((o,) + tuple('X' if b else '' for b in intent)))


class Table(Format):
    """Formal context as ASCII-art style table."""

    suffix = '.txt'

    dumps_rstrip = True

    loadf = staticmethod(load_file)

    dumpf = staticmethod(dump_file)
