# graphviz.py - assemble and compile code in the DOT language of graphviz

"""Create graph visualization PDFs with graphviz."""

__all__ = ['Digraph', 'Subgraph']

import os
import re
import subprocess
from itertools import imap

ID = re.compile(r'([a-zA-Z_]\w*|-?\d+)$')


def quote(key, valid_id=ID.match):
    """Return DOT identifier from key, quote if needed."""
    if not valid_id(key):
        return '"%s"' % key.replace('"', '\"')
    return key


def attributes(label=None, kwargs=None, attributes=None, raw=None):
    """Return assembled DOT attributes string."""
    if label is None:
        result = []
    else:
        label = quote(label.replace('-', '&minus;'))
        result = ['label=%s' % label]
    if kwargs:
        result.extend(imap('%s=%s'.__mod__, kwargs.iteritems()))
    if attributes:
        if hasattr(attributes, 'iteritems'):
            attributes = attributes.iteritems()
        result.extend(imap('%s=%s'.__mod__, attributes))
    if raw:
        result.append(raw)
    return ' [%s]' % ' '.join(result) if result else ''


class Graphviz(object):
    """Create, save, compile, and view source code in the DOT language.

    >>> dot = Digraph('The Round Table')

    >>> dot.node('A', 'Kind Arthur')
    >>> dot.node('B', 'Sir Bedevere the Wise')
    >>> dot.node('L', 'Sir Lancelot the Brave')

    >>> dot.edges(['AB', 'AL'])
    >>> dot.edge('B', 'L', constraint='false')

    >>> print dot  #doctest: +NORMALIZE_WHITESPACE
    // 'The Round Table'
    digraph {
        A [label="Kind Arthur"]
        B [label="Sir Bedevere the Wise"]
        L [label="Sir Lancelot the Brave"]
                A -> B
                A -> L
                B -> L [constraint=false]
    }
    """

    _comment = '// %r'
    _tail = '}'
    _filename = '%s.gv'
    _compile = 'dot -Tpdf -O %s'

    _key = staticmethod(quote)
    _attributes = staticmethod(attributes)

    def __init__(self, comment=None, key=None, filename=None, directory=None,
            graph_attr=None, node_attr=None, edge_attr=None, body=None):

        self.comment = comment
        self.key = key
        if filename is None:
            filename = self._filename % (key if key else 'Graph')
        self.filename =  filename
        self.directory = directory
        self._saved = False

        self.graph_attr = {} if graph_attr is None else dict(graph_attr)
        self.node_attr = {} if node_attr is None else dict(node_attr)
        self.edge_attr = {} if edge_attr is None else dict(edge_attr)

        self.body = [] if body is None else body

    def __iter__(self):
        yield self._comment % self.comment
        yield self._head % (self._key(self.key) + ' ' if self.key else '')
        for kw in ('graph', 'node', 'edge'):
            attr = getattr(self, '%s_attr' % kw)
            if attr:
                yield '%s%s' % (kw, self._attributes(None, attr))
        for line in self.body:
            yield line
        yield self._tail

    def lines(self):
        return list(self)

    def __str__(self):
        return '\n'.join(self)

    source = property(__str__)

    def append(self, line):
        """Add line to the source."""
        self.body.append(line)

    def extend(self, lines):
        """Add lines to the source."""
        self.body.extend(lines)

    def node(self, key, label=None, _attributes=None, **kwargs):
        """Create a node."""
        key = self._key(key)
        attributes = self._attributes(label, kwargs, _attributes)
        self.body.append('\t%s%s' % (key, attributes))

    def edge(self, parent_key, child_key, label=None, _attributes=None, **kwargs):
        """Create an edge."""
        parent_key = self._key(parent_key)
        child_key = self._key(child_key)
        attributes = self._attributes(label, kwargs, _attributes)
        self.body.append('\t\t%s -> %s%s' % (parent_key, child_key, attributes))

    def edges(self, parent_child):
        """Create a bunch of edges."""
        key = self._key
        self.body.extend('\t\t%s -> %s' % (key(p), key(c)) for p, c in parent_child)

    def save(self, filename=None, compile=False, view=False, directory=None):
        """Save the source to file."""
        if filename is None:
            filename = self.filename
        if directory is None:
            directory = self.directory
        for dname in [directory, os.path.dirname(filename)]:
            if dname and not os.path.exists(dname):
                os.mkdir(dname)
        if directory:
            filename = os.path.join(directory, filename)
        data = self.source
        with open(filename, 'wb') as fd:
            fd.write(data)
        self._saved = filename
        if compile or view:
            self.compile(view=view)

    def compile(self, view=False):
        """Compile the saved source file to PDF."""
        if not self._saved:
            self.save(compile=False, view=False)
        subprocess.call(self._compile % self._saved)
        if view:
            self.view()

    def view(self):
        """View the compiled PDF from the saved source file."""
        if not self._saved:
            self.save(compile=False, view=False)
        pdfpath = '%s.pdf' % self._saved
        if not os.path.exists(pdfpath):
            self.compile(view=False)
        subprocess.call(pdfpath, shell=True)


class Digraph(Graphviz):
    """Directed graph source code in the DOT language."""

    _head = 'digraph %s{'


class Subgraph(Graphviz):
    """Subgraph source code in the DOT language."""

    _head = 'subgraph %s{'


def _test(verbose=False):
    import doctest
    doctest.testmod(verbose=verbose)

if __name__ == '__main__':
    _test()
