# This module implements classes that represent lists of bonds,
# bond angles, and dihedral angles.
#
# Written by Konrad Hinsen
# last revision: 2005-11-7
#

_undocumented = 1

from UserList import UserList
import Database, Utility
from copy import copy

#
# Bonds
#
# Bond objects are created from the specifications in the data base.
#
class Bond:

    def __init__(self, blueprint, memo = None):
        if type(blueprint) is type(()):
            self.a1 = blueprint[0]
            self.a2 = blueprint[1]
        else:
            self.a1 = Database.instantiate(blueprint.a1, memo)
            self.a2 = Database.instantiate(blueprint.a2, memo)
        if Utility.uniqueID(self.a2) < Utility.uniqueID(self.a1):
            self.a1, self.a2 = self.a2, self.a1
        Utility.uniqueID.registerObject(self)

    blueprintclass = Database.BlueprintBond

    __safe_for_unpickling__ = 1
    __had_initargs__ = 1

    def __repr__(self):
        return 'Bond(' + `self.a1` + ', ' + `self.a2` + ')'
    __str__ = __repr__

    def hasAtom(self, a):
        return a is self.a1 or a is self.a2

    def otherAtom(self, a):
        if a is self.a1:
            return self.a2
        elif a is self.a2:
            return self.a1
        else:
            raise ValueError('atom not in bond')

    def _graphics(self, conf, distance_fn, model, module, options):
        objects = []
        #PJC change:
        if model == 'ball_and_stick' or model == 'vdw_and_stick':
            radius = options.get('stick_radius', 0.01)
        elif model == 'wireframe':
            radius = None
        else:
            return []
        p1 = self.a1.position(conf)
        p2 = self.a2.position(conf)
        if p1 is not None and p2 is not None:
            bond_vector = 0.5*distance_fn(self.a1, self.a2, conf)
            cut = bond_vector != 0.5*(p2-p1)
            color1 = self.a1._atomColor(self.a1, options)
            color2 = self.a2._atomColor(self.a2, options)
            material1 = module.EmissiveMaterial(color1)
            material2 = module.EmissiveMaterial(color2)
            if color1 == color2 and not cut:
                if radius is None:
                    objects.append(module.Line(p1, p2, material = material1))
                else:
                    objects.append(module.Cylinder(p1, p2, radius,
                                                   material = material1))
            else:
                if radius is None:
                    objects.append(module.Line(p1, p1+bond_vector,
                                               material = material1))
                    objects.append(module.Line(p2, p2-bond_vector,
                                               material = material2))
                else:
                    objects.append(module.Cylinder(p1, p1+bond_vector, radius,
                                                   material = material1))
                    objects.append(module.Cylinder(p2, p2-bond_vector, radius,
                                                   material = material2))
        return objects

Database.registerInstanceClass(Bond.blueprintclass, Bond)

#
# Bond angles
#
class BondAngle:

    def __init__(self, b1, b2, ca):
        self.b1 = b1 # bond 1
        self.b2 = b2 # bond 2
        self.ca = ca # common atom
        if Utility.uniqueID(self.b2) < Utility.uniqueID(self.b1):
            self.b1, self.b2 = self.b2, self.b1
        self.a1 = b1.otherAtom(ca)
        self.a2 = b2.otherAtom(ca)
        Utility.uniqueID.registerObject(self)

    def __repr__(self):
        return 'BondAngle(' + `self.a1` +',' + `self.ca` +','+ `self.a2` +')'

    def otherBond(self, bond):
        if bond is self.b1:
            return self.b2
        elif bond is self.b2:
            return self.b1
        else:
            raise ValueError('bond not in bond angle')

#
# Dihedral angles
#
class DihedralAngle:

    def __init__(self, ba1, ba2, cb):
        self.ba1 = ba1 # bond angle 1
        self.ba2 = ba2 # bond angle 2
        # cb is the common bond, i.e. the central bond for a proper dihedral
        if Utility.uniqueID(self.ba2) < Utility.uniqueID(self.ba1):
            self.ba1, self.ba2 = self.ba2, self.ba1
        self.improper = (self.ba1.ca is self.ba2.ca)
        if self.improper:
            self.b1 = self.ba1.otherBond(cb)
            self.b2 = cb
            self.b3 = self.ba2.otherBond(cb)
            self.a1 = self.ba1.ca # central atom
            self.a2 = self.b1.otherAtom(self.ba1.ca)
            self.a3 = cb.otherAtom(self.ba1.ca)
            self.a4 = self.b3.otherAtom(self.ba2.ca)
            # each improper dihedral will come in three versions;
            # identify an arbitrary unique one for constructing the list
            self.normalized = Utility.uniqueID(cb) < Utility.uniqueID(self.b1)\
                              and Utility.uniqueID(cb) < \
                                  Utility.uniqueID(self.b3)
        else:
            self.b1 = self.ba1.otherBond(cb)
            self.b2 = cb
            self.b3 = self.ba2.otherBond(cb)
            self.a1 = self.b1.otherAtom(self.ba1.ca)
            self.a2 = self.ba1.ca # these two are
            self.a3 = self.ba2.ca #   on the common bond
            self.a4 = self.b3.otherAtom(self.ba2.ca)
            self.normalized = self.a1 is not self.a4

    def __repr__(self):
        if self.improper:
            return 'ImproperDihedral(' + `self.a1` +','+ `self.a2` +','+ \
                   `self.a3` +','+ `self.a4` +')'
        else:
            return 'Dihedral(' + `self.a1` +','+ `self.a2` +','+ \
                   `self.a3` +','+ `self.a4` +')'

#
# Bond lists
#
# Bond lists can create bond angle and dihedral angle lists
# for themselves. These are cached for efficiency. The cached
# copy is deleted whenever the bond list is modified.
#
class BondList(UserList):

    def __init__(self, list=None):
        UserList.__init__(self, list)
        self._clearCache()

    __safe_for_unpickling__ = 1

    def __getinitargs__(self):
        return (None,)

    def __getstate__(self):
        self._clearCache()
        return self.__dict__

    def __copy__(self):
        return BondList(copy(self.data))

    def __setitem__(self, i, item):
        self.data[i] = item
        self._clearCache()

    def __setslice__(self, i, j, list):
        if type(list) == type(self.data):
            self.data[i:j] = list
        else:
            self.data[i:j] = list.data
        self._clearCache()

    def __delslice__(self, i, j):
        del self.data[i:j]
        self._clearCache()

    def append(self, item):
        self.data.append(item)
        self._clearCache()

    def extend(self, items):
        self.data.extend(items)
        self._clearCache()

    def insert(self, i, item):
        self.data.insert(i, item)
        self._clearCache()

    def remove(self, item):
        self.data.remove(item)
        self._clearCache()

    def _clearCache(self):
        self.bond_angles = None
        self.dihedral_angles = None

    def bondAngles(self):
        if self.bond_angles is None:
            # find all atoms that are involved in more than one bond
            bonds = {}
            atom_list = []
            for bond in self.data:
                try:
                    bl = bonds[bond.a1]
                except KeyError:
                    bl = []
                    bonds[bond.a1] = bl
                    atom_list.append(bond.a1)
                bl.append(bond)
                try:
                    bl = bonds[bond.a2]
                except KeyError:
                    bl = []
                    bonds[bond.a2] = bl
                    atom_list.append(bond.a2)
                bl.append(bond)
            angles = []
            for atom in atom_list:
                # each pair of bonds at the same atom defines a bond angle
                for p in Utility.pairs(bonds[atom]):
                    angles.append(BondAngle(p[0], p[1], atom))
            self.bond_angles = BondAngleList(angles)
        return self.bond_angles

    def dihedralAngles(self):
        if self.dihedral_angles is None:
            self.dihedral_angles = self.bondAngles().dihedralAngles()
        return self.dihedral_angles

    def bondedTo(self, atom):
        list = []
        for b in self.data:
            if b.hasAtom(atom):
                list.append(b.otherAtom(atom))
        return list

    def bondsOf(self, atom):
        list = []
        for b in self.data:
            if b.hasAtom(atom):
                list.append(b)
        return list

    def setBondAttributes(self):
        for b in self.data:
            b.a1.setBondAttribute(b.a2)
            b.a2.setBondAttribute(b.a1)

#
# Bond angle lists
#
class BondAngleList:

    def __init__(self, angles):
        self.data = angles

    def __repr__(self):
        return repr(self.data)
    def __len__(self):
        return len(self.data)
    def __getitem__(self, i):
        return self.data[i]

    def dihedralAngles(self):
        # find all bonds that are involved in more than one bond angle
        angles = {}
        bond_list = []
        for angle in self.data:
            try:
                al = angles[angle.b1]
            except KeyError:
                al = []
                angles[angle.b1] = al
                bond_list.append(angle.b1)
            al.append(angle)
            try:
                al = angles[angle.b2]
            except KeyError:
                al = []
                angles[angle.b2] = al
                bond_list.append(angle.b2)
            al.append(angle)
        dihedrals = []
        for bond in bond_list:
            # each pair of bond angles with a common bond defines a dihedral
            for p in Utility.pairs(angles[bond]):
                d = DihedralAngle(p[0], p[1], bond)
                if d.normalized:
                    dihedrals.append(d)
        return DihedralAngleList(dihedrals)

#
# Dihedral angle lists
#
class DihedralAngleList:

    def __init__(self, dihedrals):
        self.data = dihedrals

    def __repr__(self):
        return repr(self.data)
    def __len__(self):
        return len(self.data)
    def __getitem__(self, i):
        return self.data[i]

#
# Dummy bond length database, for constraints without a force field
#
class DummyBondLengthDatabase:

    def __init__(self, universe):
        pass

    def bondLength(self, bond):
        return None

    def bondAngle(self, angle):
        return None
