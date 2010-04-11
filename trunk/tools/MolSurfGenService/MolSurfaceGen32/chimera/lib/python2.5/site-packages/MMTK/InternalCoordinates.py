# Manipulation of internal coordinates
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

import MMTK
from Scientific import N
from copy import copy

#
# The abstract base class
#
class InternalCoordinate:

    def __init__(self, atoms):
        self.atoms = atoms
        self.molecule = None
        for m in atoms[0].topLevelChemicalObject().bondedUnits():
            if atoms[0] in m.atomList():
                self.molecule = m
                break
        if self.molecule is None:
            raise ValueError("inconsistent data structure")
        for a in atoms[1:]:
            if a not in self.molecule.atomList():
                raise ValueError("atoms not in the same molecule")
        self.universe = self.molecule.universe()
        if self.universe is None:
            self.universe = MMTK.InfiniteUniverse()

    def bondTest(self):
        for i in range(len(self.atoms)-1):
            if not self.atoms[i] in self.atoms[i+1].bondedTo():
                raise ValueError("no bond between %s and %s"
                                  % (self.atoms[i], self.atoms[i+1]))

    def findFragments(self, spec1, spec2):
        self.fragment1 = MMTK.Collection()
        self.fragment2 = MMTK.Collection()
        spec1 = (self.fragment1,) + spec1
        spec2 = (self.fragment2,) + spec2
        self.molecule.setBondAttributes()
        try:
            self.bondTest()
            for fragment, start, excluded, error_check in [spec1, spec2]:
                atoms = {start: 1}
                new_atoms = []
                for a in start.bondedTo():
                    if a is not excluded and a is not start:
                        atoms[a] = 1
                        new_atoms.append(a)
                while new_atoms:
                    check = new_atoms
                    new_atoms = []
                    for a in check:
                        for na in a.bondedTo():
                            if atoms.get(na, 0) == 0:
                                atoms[na] = 1
                                new_atoms.append(na)
                if atoms.get(error_check, 0) == 1:
                    raise ValueError("cyclic bond structure")
                for a in atoms.keys():
                    fragment.addObject(a)
        finally:
            self.molecule.clearBondAttributes()

#
# Bond length
#
class BondLength(InternalCoordinate):

    """Bond length

    A bond length object permits calculating and modifying the
    length of a bond in a molecule, under the condition that
    the bond is not part of a circular bond structure (but it
    is not a problem to have a circular bond structure elsewhere
    in the molecule). Modifying the bond length moves the parts
    of the molecule on both sides of the bond along the bond direction
    in such a way that the center of mass of the molecule does not
    move.

    The initial construction of the BondLength object can be
    expensive (the bond structure of the molecule must be
    analyzed). It is therefore advisable to keep the object
    rather than recreate it frequently. Note that if you only
    want to calculate bond lengths (no modification), the
    method Universe.distance is simpler and faster.
    
    Constructor: BondLength(|atom1|, |atom2|)

    Arguments:

    |atom1|, |atom2| -- the atom objects that define the bond.
                        Note that there must actually be a bond
                        between those two atoms.
    """

    def __init__(self, atom1, atom2):
        InternalCoordinate.__init__(self, [atom1, atom2])
        self.findFragments((atom1, atom2, atom2), (atom2, atom1, atom1))

    def getValue(self, conf = None):
        """Returns the length of the bond in the configuration |conf|,
        which defaults to the current configuration.
        """
        return self.universe.distance(self.atoms[0], self.atoms[1], conf)

    def setValue(self, value):
        "Sets the length of the bond to |value|."
        v = self.universe.distanceVector(self.atoms[0], self.atoms[1])
        axis = v.normal()
        distance = value - v.length()
        m1 = self.fragment1.mass()
        m2 = self.fragment2.mass()
        d1 = -m2*distance/(m1+m2)
        d2 = m1*distance/(m1+m2)
        self.fragment1.translateBy(d1*axis)
        self.fragment2.translateBy(d2*axis)

#
# Bond angles
#
class BondAngle(InternalCoordinate):

    """Bond angle

    A bond angle object permits calculating and modifying the
    angle between two bonds in a molecule, under the condition that
    the bonds are not part of a circular bond structure (but it
    is not a problem to have a circular bond structure elsewhere
    in the molecule). Modifying the bond angle rotates the parts
    of the molecule on both sides of the central atom around
    an axis passing through the central atom and perpendicular
    to the plane defined by the two bonds in such a way that
    there is no overall rotation of the molecule. The central
    atom and any other atoms bonded to it do not move.

    The initial construction of the BondAngle object can be
    expensive (the bond structure of the molecule must be
    analyzed). It is therefore advisable to keep the object
    rather than recreate it frequently. Note that if you only
    want to calculate bond angles (no modification), the
    method Universe.angle is simpler and faster.
    
    Constructor: BondAngle(|atom1|, |atom2|, |atom3|)

    Arguments:

    |atom1|, |atom2|, |atom3| -- the atom objects that define the angle.
                                 Note that there must actually be a bond
                                 between |atom1| and |atom2| (the central
                                 atom) and between |atom2| and |atom3|.
    """

    def __init__(self, atom1, atom2, atom3):
        InternalCoordinate.__init__(self, [atom1, atom2, atom3])
        self.findFragments((atom1, atom2, atom3), (atom3, atom2, atom1))

    def getValue(self, conf = None):
        """Returns the size of the angle in the configuration |conf|,
        which defaults to the current configuration.
        """
        return self.universe.angle(self.atoms[0], self.atoms[1],
                                   self.atoms[2], conf)

    def setValue(self, value):
        "Sets the angle to |value|."
        from Scientific.Geometry.TensorModule import delta
        v1 = self.universe.distanceVector(self.atoms[1], self.atoms[0])
        v2 = self.universe.distanceVector(self.atoms[1], self.atoms[2])
        angle = v1.angle(v2)
        if N.fabs(angle - N.pi) < 1.e-4:
            raise ValueError("angle too close to pi")
        axis = v1.cross(v2).normal()
        d = angle-value
        cm1, th1 = self.fragment1.centerAndMomentOfInertia()
        r1 = self.universe.distanceVector(self.atoms[1], cm1)
        th1 -= self.fragment1.mass()*((r1*r1)*delta-r1.dyadicProduct(r1))
        i1 = axis*(th1*axis)
        cm2, th2 = self.fragment2.centerAndMomentOfInertia()
        r2 = self.universe.distanceVector(self.atoms[1], cm2)
        th2 -= self.fragment2.mass()*((r2*r2)*delta-r2.dyadicProduct(r2))
        i2 = axis*(th2*axis)
        d1 = i2*d/(i1+i2)
        d2 = d1-d
        self.fragment1.rotateAroundAxis(self.atoms[1].position(),
                                        self.atoms[1].position()+axis,
                                        d1)
        self.fragment2.rotateAroundAxis(self.atoms[1].position(),
                                        self.atoms[1].position()+axis,
                                        d2)

#
# Dihedral angles
#
class DihedralAngle(InternalCoordinate):

    """Dihedral angle

    A dihedral angle object permits calculating and modifying the
    dihedral angle defined by three consecutive bonds in a molecule,
    under the condition that the central bond is not part of a
    circular bond structure (but it is not a problem to have a
    circular bond structure elsewhere in the molecule). Modifying the
    dihedral angle rotates the parts of the molecule on both sides of
    the central bond around this central bond in such a way that there
    is no overall rotation of the molecule.

    The initial construction of the DihedralAngle object can be
    expensive (the bond structure of the molecule must be
    analyzed). It is therefore advisable to keep the object
    rather than recreate it frequently. Note that if you only
    want to calculate bond angles (no modification), the
    method Universe.dihedral is simpler and faster.
    
    Constructor: DihedralAngle(|atom1|, |atom2|, |atom3|, |atom4|)

    Arguments:

    |atom1|, |atom2|, |atom3|, |atom4|
            -- the atom objects that define the dihedral.
               Note that there must actually be a bond
               between |atom1| and |atom2|, between |atom2| and |atom3|
               (the central bond), and between |atom3| and |atom4|.
    """

    def __init__(self, atom1, atom2, atom3, atom4):
        InternalCoordinate.__init__(self, [atom1, atom2, atom3, atom4])
        self.findFragments((atom2, atom3, atom3), (atom3, atom2, atom2))

    def getValue(self, conf = None):
        """Returns the size of the angle in the configuration |conf|,
        which defaults to the current configuration.
        """
        return self.universe.dihedral(self.atoms[0], self.atoms[1],
                                      self.atoms[2], self.atoms[3], conf)

    def setValue(self, value):
        "Sets the angle to |value|."
        from Scientific.Geometry.TensorModule import delta
        angle  = self.universe.dihedral(self.atoms[0], self.atoms[1],
                                        self.atoms[2], self.atoms[3])
        v = self.universe.distanceVector(self.atoms[1], self.atoms[2])
        axis = v.normal()
        d = N.fmod(angle-value, 2.*N.pi)
        cm1, th1 = self.fragment1.centerAndMomentOfInertia()
        r1 = self.universe.distanceVector(self.atoms[1], cm1)
        th1 -= self.fragment1.mass()*((r1*r1)*delta-r1.dyadicProduct(r1))
        i1 = axis*(th1*axis)
        cm2, th2 = self.fragment2.centerAndMomentOfInertia()
        r2 = self.universe.distanceVector(self.atoms[2], cm2)
        th2 -= self.fragment2.mass()*((r2*r2)*delta-r2.dyadicProduct(r2))
        i2 = axis*(th2*axis)
        d1 = i2*d/(i1+i2)
        d2 = d1-d
        self.fragment1.rotateAroundAxis(self.atoms[1].position(),
                                        self.atoms[1].position()+axis,
                                        d1)
        self.fragment2.rotateAroundAxis(self.atoms[2].position(),
                                        self.atoms[2].position()+axis,
                                        d2)

