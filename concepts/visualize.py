# visualize.py - convert lattice to graphviz dot

import os
import glob

import graphviz

__all__ = ['lattice', 'render_all']

SORTKEYS = [lambda c: c.index]

NAME_GETTERS = [lambda c: 'c%d' % c.index]


def lattice(lattice, filename, directory, render, view, node_color,node,font_size,distance,**kwargs):
    """Return graphviz source for visualizing the lattice graph."""
    dot = graphviz.Digraph(name=lattice.__class__.__name__,
                           comment=repr(lattice),
                           filename=filename, directory=directory,
                           node_attr={'shape': 'circle', 'width': '0.2',
                                      'style': 'filled', 'label': ''},
                           edge_attr={'dir': 'none', 'labeldistance': '1',
                                      'minlen': str(distance)},
                           **kwargs)
    font_size=str(font_size)
    sortkey = SORTKEYS[0]
    node_name = NAME_GETTERS[0]
    low=[]
    up=[]
    place=None
    for concept in lattice._concepts:

        if node==None:
            place=None
        elif node in concept.objects:
            place=node_name(concept)
        elif node in concept.properties:
            place=node_name(concept)

    #場所の指定がなかった場合
    if place==None:
        for concept in lattice._concepts:
            name = node_name(concept)
            dot.node(name,color=node_color)
            for c in sorted(concept.lower_neighbors, key=sortkey):
                dot.edge(name,node_name(c),color="black")
            if concept.objects:
                dot.edge(name, name,fontsize=font_size,
                 headlabel='\n'.join(concept.objects),
                 labelangle='270', color='transparent')

            if concept.properties:
                dot.edge(name, name,fontsize=font_size,
                 taillabel='\n'.join(concept.properties),
                 labelangle='90', color='transparent')

    #場所の指定があった場合
    else:
        #場所の特定
        for concept in lattice._concepts:
            name = node_name(concept)
            dot.node(name,color=node_color)
            if name==place:
                low.append(concept)
                up.append(concept)
                dot.node(name,color="red")

        low_and_up_list=[]
        low_and_up_name_list=[place]
        #特定されたノードの下位概念の特定
        while True:
            lower_list=[]
            for i in range(len(low)):
                for c in sorted(low[i].lower_neighbors,key=sortkey):
                    dot.node(node_name(c),color="blue")
                    dot.edge(node_name(low[i]),node_name(c),color="blue")
                    if c in lower_list:
                        pass
                    else:
                        lower_list.append(c)
                        if c not in low_and_up_name_list:
                            low_and_up_name_list.append(node_name(c))

                    low_and_up_list.append([node_name(low[i]),node_name(c)])
            if lower_list==[]:
                break
            low=lower_list
        #特定されたノードの上位概念の特定
        while True:
            upper_list=[]
            for i in range(len(up)):
                for c in sorted(up[i].upper_neighbors,key=sortkey):
                    dot.node(node_name(c),color="blue")
                    dot.edge(node_name(c),node_name(up[i]),color="blue")
                    if c in upper_list:
                        pass
                    else:
                        upper_list.append(c)
                        if c  not in low_and_up_name_list:
                            low_and_up_name_list.append(node_name(c))

                    low_and_up_list.append([node_name(c),node_name(up[i])])

            if upper_list==[]:
                break
            up=upper_list

        #表示の設定(特定されたノードにつながる概念を強調して表示する)
        for concept in lattice._concepts:
            name = node_name(concept)
            dot.node(name)
            if name in low_and_up_name_list:
                    if concept.objects:
                        dot.edge(name, name,fontsize=font_size,
                             headlabel='\n'.join(concept.objects),
                             labelangle='270', color='transparent')

                    if concept.properties:
                        dot.edge(name, name,fontsize=font_size,
                             taillabel='\n'.join(concept.properties),
                             labelangle='90', color='transparent')
            for c in sorted(concept.lower_neighbors, key=sortkey):
                if [name,node_name(c)] not in low_and_up_list:
                    dot.edge(name,node_name(c),color="lightgray")


    if render or view:
        dot.render(view=view)  # pragma: no cover

    return dot



def render_all(filepattern='*.cxt', encoding=None,
               directory=None, out_format=None):  # pragma: no cover
    import concepts

    for cxtfile in glob.iglob(filepattern):
        c = concepts.load(cxtfile, encoding=encoding)
        l = c.lattice

        filename = '%s.gv' % os.path.splitext(cxtfile)[0]
        if directory is not None:
            filename = os.path.basename(filename)

        dot = l.graphviz(filename, directory, format=out_format)
        dot.render()
