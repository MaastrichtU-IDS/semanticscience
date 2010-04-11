"""
This wrapper intercepts calls through the store interface
And implements thread-safe logging of destructive operations (adds / removes) in reverse.
This is persisted on the store instance and the reverse operations are executed
In order to return the store to the state it was when the transaction began
Since the reverse operations are persisted on the store, the store itself acts
as a transaction.  Calls to commit or rollback, flush the list of reverse operations
This provides thread-safe atomicity and isolation (assuming concurrent operations occur with different
store instances), but no durability (transactions are persisted in memory and wont
 be available to reverse operations after the systeme fails): A and I out of ACID.
"""

from rdflib.store import Store
from rdflib.Graph import Graph, ConjunctiveGraph
from pprint import pprint
import threading

destructiveOpLocks = {
    'add':None,
    'remove':None,
}

class AuditableStorage(Store):
    def __init__(self, storage):
        self.storage = storage
        self.context_aware = storage.context_aware
        #NOTE: this store can't be formula_aware as it doesn't have enough info to reverse
        #The removal of a quoted statement
        self.formula_aware = False#storage.formula_aware
        self.transaction_aware = True #This is only half true
        self.reverseOps = []
        self.rollbackLock = threading.RLock()

    def open(self, configuration, create=True):
        return self.storage.open(configuration,create)

    def close(self, commit_pending_transaction=False):
        self.storage.close()

    def destroy(self, configuration):
        self.storage.destroy(configuration)

    def add(self, (subject, predicate, object_), context, quoted=False):
        lock = destructiveOpLocks['add']
        lock = lock and lock or threading.RLock()
        lock.acquire()
        context = context is not None and context.__class__(self.storage,context.identifier) or None
        ctxId = context is not None and context.identifier or None
        self.reverseOps.append((subject,predicate,object_,ctxId,'remove'))
        if (subject,predicate,object_,ctxId,'add') in self.reverseOps:
            self.reverseOps.remove((subject,predicate,object_,context,'add'))
        self.storage.add((subject, predicate, object_), context, quoted)
        lock.release()

    def remove(self, (subject, predicate, object_), context=None):
        lock = destructiveOpLocks['remove']
        lock = lock and lock or threading.RLock()
        lock.acquire()
        #Need to determine which quads will be removed if any term is a wildcard
        context = context is not None and context.__class__(self.storage,context.identifier) or None
        ctxId = context is not None and context.identifier or None
        if None in [subject,predicate,object_,context]:
            if ctxId:                
                for s,p,o in context.triples((subject,predicate,object_)):
                    if (s,p,o,ctxId,'remove') in self.reverseOps:
                        self.reverseOps.remove((s,p,o,ctxId,'remove'))
                    else:
                        self.reverseOps.append((s,p,o,ctxId,'add'))
            else:
                for s,p,o,ctx in ConjunctiveGraph(self.storage).quads((subject,predicate,object_)):
                    if (s,p,o,ctx.identifier,'remove') in self.reverseOps:
                        self.reverseOps.remove((s,p,o,ctx.identifier,'remove'))
                    else:
                        self.reverseOps.append((s,p,o,ctx.identifier,'add'))
                
        elif (subject,predicate,object_,ctxId,'add') in self.reverseOps:
            self.reverseOps.remove((subject,predicate,object_,ctxId,'add'))
        else:
            self.reverseOps.append((subject,predicate,object_,ctxId,'add'))
        self.storage.remove((subject,predicate,object_),context)
        lock.release()

    def triples(self, (subject, predicate, object_), context=None):
        context = context is not None and context.__class__(self.storage,context.identifier) or None
        for (s,p,o),cg in self.storage.triples((subject, predicate, object_), context):
            yield (s,p,o),cg

    def __len__(self, context=None):
        context = context is not None and context.__class__(self.storage,context.identifier) or None
        return self.storage.__len__(context)

    def contexts(self, triple=None):
        for ctx in self.storage.contexts(triple):
            yield ctx

    def bind(self, prefix, namespace):
        self.storage.bind(prefix, namespace)

    def prefix(self, namespace):
        return self.storage.prefix(namespace)

    def namespace(self, prefix):
        return self.storage.namespace(prefix)

    def namespaces(self):
        return self.storage.namespaces()

    def commit(self):
        self.storage.commit()
        self.reverseOps = []

    def rollback(self):
        #Aquire Rollback lock and apply reverse operations in the forward order
        self.rollbackLock.acquire()
        for subject,predicate,obj,context,op in self.reverseOps:
            if op == 'add':
                self.storage.add((subject,predicate,obj),Graph(self.storage,context))
            else:
                self.storage.remove((subject,predicate,obj),Graph(self.storage,context))

        self.reverseOps = []
        self.rollbackLock.release()
