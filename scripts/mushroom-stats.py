#!/usr/bin/env python3

import itertools

import pandas as pd

from mushroom import MUSHROOM, ENCODING, CSV, CSV_MINIMAL_INT, properties


dtype = {MUSHROOM.stem: 'uint'}
dtype.update((p, bool) for p in properties)

df = pd.read_csv(CSV, dtype=dtype, index_col=MUSHROOM.stem, encoding=ENCODING)
df.info(memory_usage='deep')

empty = df.any(axis='rows')[lambda x: ~x].index.tolist()
print(empty)
assert len(empty) == 9
df = df.drop(empty, axis='columns')
df.info(memory_usage='deep')

cf = (df[['class:edible', 'class:poisonous']]
      .sum().to_frame('count')
      .assign(ratio=lambda x: 100 * x / x.sum()))

cf = pd.concat([cf, cf.sum().to_frame('total').T])

print(cf)
print('fill ratio:', f'{df.sum().sum() / df.count().sum():.2%}')


mf = pd.read_csv(CSV_MINIMAL_INT, dtype=dtype, index_col=MUSHROOM.stem,
                 encoding=ENCODING)
mf.info(memory_usage='deep')

assert df.equals(mf), ("df.drop(empty, axis='columns') aggrees"
                       ' with Definition.remove_empty_properties()')
