#!/usr/bin/env python3

"""Visualize ``examples/*.cxt`` and ``examples/*.csv``."""

import concepts.visualize

KWARGS = {'exclude': {'bob-ross.cxt',
                      'liveinwater.csv',
                      'mushroom.cxt',
                      'segments.cxt'},
          'encoding': 'utf-8',
          'directory': 'visualize-output',
          'out_format': 'pdf'}


concepts.visualize.render_all('examples/*.cxt', **KWARGS)

concepts.visualize.render_all('examples/*.csv', **KWARGS)
