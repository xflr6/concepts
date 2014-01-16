# visualize-examples

import os
import glob

from concepts import Context

for filename in glob.glob('examples/*.cxt'):
    c = Context.from_file(filename)
    name, ext = os.path.splitext(filename)
    c.lattice.graphviz().save('%s.gv' % name, compile=True)
