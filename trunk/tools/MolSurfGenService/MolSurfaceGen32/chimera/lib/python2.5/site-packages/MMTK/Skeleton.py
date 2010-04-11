# This module handles the skeleton descriptions stored in trajectory files.
#
# Written by Konrad Hinsen
# last revision: 2008-1-12
#

_undocumented = 1

import MMTK
import MMTK.Environment
import MMTK.ForceFields
import copy, sys, types

#
# Atoms
#
class A:

    def __init__(self, name, index, type = None):
	self.name = name
	self.index = index
	self.type = type

    def make(self, info, conf = None):
	atom =  MMTK.Atom(self.type, name = self.name)
        self.assignIndex(atom, info, conf)
	return atom

    def assignIndex(self, atom, info, conf):
	atom.setArray(None, [self.index])
        info[self.index] = atom
        if conf is not None:
            atom.setPosition(MMTK.Vector(conf[self.index]))

#
# Composite chemical objects
#
class Composite:

    def __init__(self, name, list, type = None, **kwargs):
	self.name = name
	self.list = list
	self.type = type
	self.kwargs = kwargs

    def make(self, info, conf = None):
	object = self._class(self.type, name=self.name)
	for sub in self.list:
	    sub.assignIndex(getattr(object, sub.name), info, conf)
        if self.kwargs.has_key('dc'):
            for a1, a2, d in self.kwargs['dc']:
                object.addDistanceConstraint(info[a1], info[a2], d)
	return object

    def assignIndex(self, object, info, conf):
	for sub in self.list:
	    sub.assignIndex(getattr(object, sub.name), info, conf)

class G(Composite):
    pass

class M(Composite):
    _class = MMTK.Molecule

class C(Composite):
    _class = MMTK.Complex

class AC(Composite):

    def make(self, info, conf = None):
        atoms = map(lambda a, i=info, c=conf: a.make(i, c), self.list)
        return MMTK.AtomCluster(atoms, name = self.name)

#class X(Composite):
#    _class = MMTK.Crystal

class S(Composite):

    def make(self, info, conf = None):
        import MMTK.Proteins
	n_residues = len(self.type)/3
	residues = map(lambda i, s = self.type: s[3*i:3*i+3],
                       range(n_residues))
	self.kwargs['name'] = self.name
	chain = apply(MMTK.Proteins.PeptideChain, (residues,), self.kwargs)
	for i in range(len(self.list)):
	    self.list[i].assignIndex(chain[i], info, conf)
            chain[i].name = self.list[i].name
	return chain

class N(Composite):

    def make(self, info, conf = None):
        import MMTK.NucleicAcids
	n_residues = len(self.type)/3
	residues = map(lambda i, s = self.type: s[3*i:3*i+3].strip(),
                       range(n_residues))
	self.kwargs['name'] = self.name
	chain = apply(MMTK.NucleicAcids.NucleotideChain, (residues,),
                      self.kwargs)
	for i in range(len(self.list)):
	    self.list[i].assignIndex(chain[i], info, conf)
	return chain

#
# Collections and universes
#
class c:

    def __init__(self, creation, objects):
	self.creation = creation
	self.objects = objects

    def make(self, info, conf = None):
        collection = _evalString(self.creation)
        attr = None
	for o in self.objects:
            if isinstance(o, str):
                attr = o
            elif attr:
                setattr(collection, attr, o.make(info, conf))
            else:
                collection.addObject(o.make(info, conf))
	return collection

#
# Objects constructed from a list of other objects (e.g. proteins)
#
class l:

    def __init__(self, class_name, name, objects):
	self.class_name = class_name
	self.objects = objects
	self.name = name

    def make(self, info, conf = None):
        import MMTK.Proteins
        classes = {'Protein': MMTK.Proteins.Protein}
	return classes[self.class_name] \
	       (map(lambda o, i=info, c=conf: o.make(i, c), self.objects),
		name = self.name)

#
# Objects without subobjects
#
class o:

    def __init__(self, creation):
	self.creation = creation

    def make(self, info, conf = None):
	return _evalString(self.creation)

#
# Evaluate description string
# In case of a NameError, suppose the missing name is the name of a
# module, import that module, and try again. In case of an AttributeError,
# suppose that the missing attribute is a subpackage, import that subpackage,
# and try again.
#
def _evalString(description):
    local = {}
    namespace = copy.copy(vars(MMTK))
    imported = []
    done = False
    while not done:
        try:
            o = eval(description, namespace, local)
            done = True
        except NameError, exception:
            name = str(exception).split("'")[1]
            __import__(name)
            namespace[name] = sys.modules[name]
            imported.append(name)
        except AttributeError, exception:
            if str(exception).split("'")[1] == "module":
                name = str(exception).split("'")[3]
                for m in imported:
                    try:
                        module_name = "%s.%s" % (m, name)
                        __import__(module_name)
                        imported.append(module_name)
                    except ImportError:
                        pass
            else:
                raise
    return o
