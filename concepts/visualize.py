# visualize.py - convert lattice to graphviz dot

import os
import glob

import graphviz

__all__ = ['lattice', 'render_all']


def node_name(concept):
    return 'c%d' % concept.index


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

        dot.edges((name, node_name(c)) for c in concept.lower_neighbors)

    if render or view:
        dot.render(view=view)
    return dot


def render_all(filepattern, frmat='cxt'):
    from concepts import Context

    for filename in glob.glob(filepattern):
        c = Context.from_file(filename, frmat)
        name, ext = os.path.splitext(filename)
        filename = '%s.gv' % name

        lattice(c.lattice, filename, None, True, False)
