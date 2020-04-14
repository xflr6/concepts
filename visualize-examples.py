#!/usr/bin/env python
# visualize-examples.py

import concepts.visualize

KWARGS = {'directory': 'visualize-output', 'out_format': 'pdf'}

concepts.visualize.render_all('examples/*.cxt', **KWARGS)
concepts.visualize.render_all('examples/[r-v]*.csv', encoding='utf-8', **KWARGS)
