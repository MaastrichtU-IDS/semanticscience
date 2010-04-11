# A molecule factory is used to create chemical objects
# in code, without a database definition.
#
# Written by Konrad Hinsen
# last revision: 2007-6-1
#

"""See also the example in Example:Miscellaneous.
"""

from MMTK import Bonds, ChemicalObjects
import copy

#
# Molecule factories store AtomTemplate and GroupTemplate objects.
#

class AtomTemplate:
    
    def __init__(self, element):
        self.element = element

class GroupTemplate:
    
    def __init__(self, name):
        self.name = name
        self.children = []
        self.names = {}
        self.attributes = {}
        self.positions = {}
        self.bonds = []
        self.locked = False

    def addAtom(self, atom_name, element):
        """Add an atom of |element| which is assigned the
        name |atom_name|.
        """
        if self.locked:
            raise ValueError("group is locked")
        atom = AtomTemplate(element)
        self.names[atom_name] = len(self.children)
        self.children.append(atom)

    def addSubgroup(self, subgroup_name, subgroup):
        """Add |subgroup| as a subgroup with name |subgroup_name|.
        """
        if self.locked:
            raise ValueError("group is locked")
        self.names[subgroup_name] = len(self.children)
        self.children.append(subgroup)

    def addBond(self, atom1, atom2):
        """Add a bond between |atom1| and |atom2|.
        """
        if self.locked:
            raise ValueError("group is locked")
        self.bonds.append((self.atomNameToPath(atom1),
                           self.atomNameToPath(atom2)))

    def setAttribute(self, name, value):
        if self.locked:
            raise ValueError("group is locked")
        self.attributes[name] = value

    def setPosition(self, name, vector):
        if self.locked:
            raise ValueError("group is locked")
        self.positions[name] = vector

    def getAtomReference(self, atom_name):
        path = self.atomNameToPath(atom_name)
        object = self
        for path_element in path[:-1]:
            object =  object.children[object.names[path_element]]
        atom_index = object.names[path[-1]]
        reference = 0
        for i in range(atom_index):
            if isinstance(object.children[i], AtomTemplate):
                reference += 1
        from MMTK.Database import AtomReference
        return AtomReference(reference)

    def atomNameToPath(self, atom_name):
        atom_name = atom_name.split('.')
        object = self
        try:
            for path_element in atom_name:
                object = object.children[object.names[path_element]]
            if not isinstance(object, AtomTemplate):
                raise ValueError("no atom " + atom)
        except KeyError:
            raise ValueError("no atom " + '.'.join(atom_name))
        return atom_name

    def writeXML(self, file, memo):
        if memo.get(self.name, False):
            return
        names = len(self.children)*[None]
        for name in self.names:
            names[self.names[name]] = name
        atoms = []
        subgroups = []
        for i in range(len(self.children)):
            object = self.children[i]
            name = names[i]
            if isinstance(object, GroupTemplate):
                object.writeXML(file, memo)
                subgroups.append((name, object))
            else:
                atoms.append((name, object))
        file.write('<molecule id="%s">\n' % self.name)
        for name, subgroup in subgroups:
            file.write('  <molecule ref="%s" title="%s"/>\n'
                       % (subgroup.name, name))
        if atoms:
            file.write('  <atomArray>\n')
            for name, atom in atoms:
                file.write('    <atom title="%s" elementType="%s"/>\n'
                           % (name, atom.element))
            file.write('  </atomArray>\n')
        if self.bonds:
            file.write('  <bondArray>\n')
            for a1, a2 in self.bonds:
                file.write('    <bond atomRefs2="%s %s"/>\n'
                           % (':'.join(a1), ':'.join(a2)))
            file.write('  </bondArray>\n')
        file.write('</molecule>\n')
        memo[self.name] = True

    def getXMLAtomOrder(self):
        atom_names = []
        names = len(self.children)*[None]
        for name in self.names:
            names[self.names[name]] = name
        for i in range(len(self.children)):
            oname = names[i]
            object = self.children[i]
            if isinstance(object, GroupTemplate):
                for name in object.getXMLAtomOrder():
                    atom_names.append(oname + ':' + name)
            else:
                atom_names.append(oname)
        return atom_names

#
# The MoleculeFactory class
#
class MoleculeFactory:
    
    """MoleculeFactory

    A MoleculeFactory serves to create molecules without reference to database
    definitions. Molecules and groups are defined in terms of atoms, groups, and
    bonds. Each MoleculeFactory constitutes an independent set of definitions.
    Definitions within a MoleculeFactory can refer to each other.

    Each MoleculeFactory stores a set of Class:MMTK.ChemicalObjects.Group
    objects which are referred to by names. The typical operation sequence is to
    create a new group and then add atoms, bonds, and subgroups. It is also
    possible to define coordinates and arbitrary attributes (in particular for
    force fields). In the end, a finished object can be retrieved as a
    Class:MMTK.ChemicalObjects.Molecule object.

    Constructor: MoleculeFactory()
    """

    def __init__(self):
        self.groups = {}
        self.locked_groups = {}

    def createGroup(self, name):
        "Creates a new (initially empty) group object."
        if self.groups.has_key(name):
            raise ValueError("redefinition of group " + name)
        self.groups[name] = GroupTemplate(name)

    def addSubgroup(self, group, subgroup_name, subgroup):
        """Add |subgroup| as a subgroup to |group| with name |subgroup_name|.
        """
        self.groups[group].addSubgroup(subgroup_name, self.groups[subgroup])

    def addAtom(self, group, atom_name, element):
        """Add an atom of |element| to |group| which is assigned the
        name |atom_name|."""
        self.groups[group].addAtom(atom_name, element)

    def addBond(self, group, atom1, atom2):
        "Add a bond between |atom1| and |atom2| in |group|."
        self.groups[group].addBond(atom1, atom2)

    def setAttribute(self, group, name, value):
        self.groups[group].setAttribute(name, value)

    def setPosition(self, group, atom, vector):
        self.groups[group].setPosition(atom, vector)

    def getAtomReference(self, group, atom):
        return self.groups[group].getAtomReference(atom)

    def retrieveMolecule(self, group):
        """Returns a Molecule object containing the atoms and subgroups
        of |group|.
        """
        group = self.groups[group]
        return self.makeChemicalObjects(group, True)
    
    def makeChemicalObjects(self, template, top_level):
        self.groups[template.name].locked = True
        if top_level:
            if template.attributes.has_key('sequence'):
                object = ChemicalObjects.ChainMolecule(None)
            else:
                object = ChemicalObjects.Molecule(None)
        else:
            object = ChemicalObjects.Group(None)
        object.atoms = []
        object.bonds = Bonds.BondList([])
        object.groups = []
        object.type = self.groups[template.name]
        object.parent = None
        child_objects = []
        for child in template.children:
            if isinstance(child, GroupTemplate):
                group = self.makeChemicalObjects(child, False)
                object.groups.append(group)
                object.atoms.extend(group.atoms)
                object.bonds.extend(group.bonds)
                group.parent = object
                child_objects.append(group)
            else:
                atom = ChemicalObjects.Atom(child.element)
                object.atoms.append(atom)
                atom.parent = object
                child_objects.append(atom)
        for name, index in template.names.items():
            setattr(object, name, child_objects[index])
            child_objects[index].name = name
        for name, value in template.attributes.items():
            path = name.split('.')
            setattr(self.namePath(object, path[:-1]), path[-1], value)
        for atom1, atom2 in template.bonds:
            atom1 = self.namePath(object, atom1)
            atom2 = self.namePath(object, atom2)
            object.bonds.append(Bonds.Bond((atom1, atom2)))
        for name, vector in template.positions.items():
            path = name.split('.')
            self.namePath(object, path).setPosition(vector)
        return object

    def namePath(self, object, path):
        for item in path:
            object = getattr(object, item)
        return object

    def writeXML(self, file):
        file.write('<?xml version="1.0" encoding="ISO-8859-1" ' +
                   'standalone="yes"?>\n\n')
        file.write('<templates>\n\n')
        memo = {}
        for group in self.groups:
            self.groups[group].writeXML(file, memo)
        file.write('\n</templates>\n')
