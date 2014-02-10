# visualize.py - convert lattice to graphviz dot

import os
import glob

import graphviz

__all__ = ['lattice', 'render_all']

SORTKEYS = [lambda c: c.index]

NAME_GETTERS = [lambda c: 'c%d' % c.index]


def lattice(lattice, filename, directory, render, view):
    """Return graphviz source for visualizing the lattice graph."""
    dot = graphviz.Digraph(
        name=lattice.__class__.__name__,
        comment=repr(lattice),
        filename=filename,
        directory=directory,
        node_attr=dict(shape='circle', width='.25', style='filled', label=''),
        edge_attr=dict(dir='none', labeldistance='1.5', minlen='2')
    )

    sortkey = SORTKEYS[0]

    node_name = NAME_GETTERS[0]

    for concept in lattice._concepts:
        name = node_name(concept)
        dot.node(name)

        if concept.objects:
            dot.edge(name, name,
                headlabel=' '.join(concept.objects),
                labelangle='270', color='transparent')

        if concept.properties:
            dot.edge(name, name,
                taillabel=' '.join(concept.properties),
                labelangle='90', color='transparent')

        dot.edges((name, node_name(c))
            for c in sorted(concept.lower_neighbors, key=sortkey))

    if render or view:
        dot.render(view=view)
    return dot


def render_all(filepattern='*.cxt', frmat='cxt'):
    from concepts import Context

    for cxtfile in glob.glob(filepattern):
        c = Context.fromfile(cxtfile, frmat)
        name, ext = os.path.splitext(cxtfile)
        filename = '%s.gv' % name

        lattice(c.lattice, filename, None, True, False)
