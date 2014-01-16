# visualize.py - convert lattice to graphviz dot

import graphviz

__all__ = ['lattice']


def lattice(lattice, save, compile, view):
    """Return graphviz source for visualizing the lattice graph."""
    dot = graphviz.Digraph(comment=lattice, key=lattice.__class__.__name__,
        node_attr=dict(shape='circle', width='.25', style='filled', label='""'),
        edge_attr=dict(dir='none', labeldistance='1.5', minlen='2'))

    for concept in lattice._concepts:
        key = 'c%d' % concept.index
        dot.node(key, None)

        if concept.objects:
            dot.edge(key, key,
                headlabel='"%s"' % ' '.join(concept.objects).replace('-', '&minus;'),
                labelangle='270', color='transparent')

        if concept.properties:
            dot.edge(key, key,
                taillabel='"%s"' % ' '.join(concept.properties).replace('-', '&minus;'),
                labelangle='90', color='transparent')

        dot.edges((key, 'c%d' % c.index) for c in concept.lower_neighbors)

    if save or compile or view:
        dot.save(compile=compile, view=view)
    return dot
