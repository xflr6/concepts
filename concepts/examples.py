"""Loading examplary formal contexts."""

import typing
from urllib.request import urlopen

from .contexts import Context

__all__ = ['load_dataset']

DATASET_SOURCE = "https://raw.githubusercontent.com/fcatools/contexts/main/contexts"


# inspired by https://github.com/mwaskom/seaborn/blob/master/seaborn/utils.py#L524
def load_dataset(name: str, data_src: typing.Optional[str] = DATASET_SOURCE,
                 encoding: typing.Optional[str] = 'utf-8'):
    """Load an example formal context from the online repository (requires internet).

    Args:
        name (str):
            Name of the dataset (``{name}.cxt`` on
            https://github.com/fcatools/contexts/tree/main/contexts).
        data_src (str, optional):
            Base URL to the repository to download the dataset.
        encoding (str, optional):
            Encoding of the file (``'utf-8'``, ``'latin1'``, ``'ascii'``, ...).

    Returns:
        Context: New :class:`.Context` instance.

    Example:
        >>> import concepts
        >>> concepts.load_dataset('living_beings_and_water.cxt')
        <Context object mapping 8 objects to 9 properties [b1e86589] at 0x...>
    """

    url = f"{data_src}/{name}.cxt"

    # TODO: implement caching here?

    return Context.fromstring(urlopen(url).read().decode(encoding), 'cxt')
