# visualize.py - convert lattice to graphviz dot

import os
import glob

import graphviz

__all__ = ['lattice', 'render_all']

SORTKEYS = [lambda c: c.index]

NAME_GETTERS = [lambda c: 'c%d' % c.index]


def lattice(lattice, filename, directory, render, view, **kwargs):
    """Return graphviz source for visualizing the lattice graph."""
    dot = graphviz.Digraph(
        name=lattice.__class__.__name__,
        comment=repr(lattice),
        filename=filename,
        directory=directory,
        node_attr=dict(shape='circle', width='.25', style='filled', label=''),
        edge_attr=dict(dir='none', labeldistance='1.5', minlen='2'),
        **kwargs
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
        dot.render(view=view)  # pragma: no cover
    return dot


def render_all(filepattern='*.cxt', frmat=None, encoding=None,
               directory=None, out_format=None):
    from concepts import Context

    if directory is not None:
        get_name = lambda filename: os.path.basename(filename)
    else:
        get_name = lambda filename: filename

    if frmat is None:
        from concepts.formats import Format
        get_frmat = Format.by_extension.get
    else:
        get_frmat = lambda filename: frmat

    for cxtfile in glob.glob(filepattern):
        name, ext = os.path.splitext(cxtfile)
        filename = '%s.gv' % get_name(name)

        c = Context.fromfile(cxtfile, get_frmat(ext), encoding=encoding)
        l = c.lattice
        dot = l.graphviz(filename, directory)

        if out_format is not None:
            dot.format = out_format
        dot.render()
