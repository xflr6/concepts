""""Convert ``Lattice`` to Graphviz DOT."""

import glob
import os

import graphviz

__all__ = ['lattice', 'render_all']

SORTKEYS = [lambda c: c.index]

NAME_GETTERS = [lambda c: f'c{c.index:d}']


def lattice(lattice, filename, directory, render, view,
            make_object_label=' '.join, make_property_label=' '.join,
            **kwargs) -> graphviz.Digraph:
    """Return graphviz source for visualizing the lattice graph."""
    dot = graphviz.Digraph(name=lattice.__class__.__name__,
                           comment=repr(lattice),
                           filename=filename, directory=directory,
                           node_attr={'shape': 'circle', 'width': '.25',
                                      'style': 'filled', 'label': ''},
                           edge_attr={'dir': 'none', 'labeldistance': '1.5',
                                      'minlen': '2'},
                           **kwargs)

    sortkey = SORTKEYS[0]
    node_name = NAME_GETTERS[0]

    for concept in lattice._concepts:
        name = node_name(concept)
        dot.node(name)

        if concept.objects:
            dot.edge(name, name,
                     headlabel=make_object_label(concept.objects),
                     labelangle='270', color='transparent')

        if concept.properties:
            dot.edge(name, name,
                     taillabel=make_property_label(concept.properties),
                     labelangle='90', color='transparent')

        dot.edges((name, node_name(c))
                  for c in sorted(concept.lower_neighbors, key=sortkey))

    if render or view:
        dot.render(view=view)  # pragma: no cover
    return dot


def render_all(filepattern='*.cxt', *, exclude=(),
               encoding: str = None,
               directory=None, out_format=None) -> None:  # pragma: no cover
    import concepts

    for cxtfile in glob.iglob(filepattern):
        print(cxtfile)
        if os.path.basename(cxtfile) in exclude:
            print('  matches exclude, skip')
            continue
        c = concepts.load(cxtfile, encoding=encoding)
        l = c.lattice

        filename = f'{os.path.splitext(cxtfile)[0]}.gv'
        if directory is not None:
            filename = os.path.basename(filename)

        dot = l.graphviz(filename, directory, format=out_format)
        dot.render()
