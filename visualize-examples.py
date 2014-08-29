#!/usr/bin/env python
# visualize-examples.py

import concepts.visualize

ARGS = {'directory': 'visualize-output', 'out_format': 'pdf'}

concepts.visualize.render_all('examples/*.cxt', **ARGS)
concepts.visualize.render_all('examples/[r-v]*.csv', encoding='utf-8', **ARGS)
