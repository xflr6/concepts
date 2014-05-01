#!/usr/bin/env python
# visualize-examples.py

import concepts.visualize

DIRECTORY = 'visualize-output'
FORMAT = 'pdf'

concepts.visualize.render_all('examples/*.cxt', directory=DIRECTORY, out_format=FORMAT)
