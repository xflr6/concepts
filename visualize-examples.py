#!/usr/bin/env python
# visualize-examples.py

import concepts.visualize

DIRECTORY = 'visualize-output'


concepts.visualize.render_all('examples/*.cxt', DIRECTORY)
