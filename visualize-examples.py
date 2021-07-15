#!/usr/bin/env python3

"""Visualize ``examples/*``."""

import concepts.visualize

KWARGS = {'directory': 'visualize-output', 'out_format': 'pdf'}

concepts.visualize.render_all('examples/*.cxt',
                              exclude={'bob-ross.cxt', 'mushroom.cxt',
                                       'sgments.cxt'},  # FIXME
                              **KWARGS)

concepts.visualize.render_all('examples/[r-v]*.csv', encoding='utf-8', **KWARGS)
