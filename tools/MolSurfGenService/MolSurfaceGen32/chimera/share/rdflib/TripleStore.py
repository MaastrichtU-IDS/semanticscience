"""Deprecated; use Graph."""

from rdflib.Graph import Graph

from rdflib.store.Memory import Memory

class TripleStore(Graph):
    """
    Depcrecated. Use Graph instead.
    """

    def __init__(self, location=None, backend=None):
        if backend==None:
            backend = Memory()
        super(TripleStore, self).__init__(backend=backend)
        if location:
            self.load(location)

    def prefix_mapping(self, prefix, namespace):
        self.bind(prefix, namespace)

