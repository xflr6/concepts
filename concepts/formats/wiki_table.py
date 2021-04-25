import functools

from .base import Format

__all__ = ['WikiTable']


def dump_file(file, objects, properties, bools, *, _serialized=None):
    write = functools.partial(print, file=file)
    write('{| class="featuresystem"')
    write('!')
    write('!{}'.format('!!'.join(properties)))

    wp = list(map(len, properties))

    for o, intent in zip(objects, bools):
        bcells = (('X' if b else '').ljust(w) for w, b in zip(wp, intent))
        write('|-')
        write(f'!{o}')
        write('|{}'.format('||'.join(bcells)))
    write('|}')


class WikiTable(Format):
    """Formal context as MediaWiki markup table."""

    aliases = ['wikitable']

    dumps_rstrip = True

    dumpf = staticmethod(dump_file)
