# This module implements classes that represent force fields
# for bonded interactions.
#
# Written by Konrad Hinsen
# last revision: 2007-7-4
#

_undocumented = 1

from ForceField import ForceField, ForceFieldData
from MMTK import Utility
from Scientific.Geometry import Vector
from Scientific import N as Numeric

#
# The base class BondedForceField provides the common
# functionality for all bonded interactions. The derived
# classes have to deal with determining functional forms
# and parameters and providing the evaluation code
#
class BondedForceField(ForceField):

    def __init__(self, name):
        ForceField.__init__(self, name)
        self.type = 'bonded'

    def evaluatorParameters(self, universe, subset1, subset2, global_data):
        data = ForceFieldData()
        data.set('universe', universe)
        if subset1 is not None:
            label1 = Utility.uniqueAttribute()
            label2 = Utility.uniqueAttribute()
            for atom in subset1.atomList():
                setattr(atom, label1, None)
            for atom in subset2.atomList():
                setattr(atom, label2, None)
        for o in universe:
            for bu in o.bondedUnits():
                if not hasattr(bu, 'bonds'): continue
                options = {'bonds': 1, 'bond_angles': 1,
                           'dihedrals': 1, 'impropers': 1}
                self.getOptions(bu, options)
                if options['bonds']:
                    if subset1 is None:
                        for bond in bu.bonds:
                            self.addBondTerm(data, bond, bu, global_data)
                    else:
                        for bond in bu.bonds:
                            atoms = [bond.a1, bond.a2]
                            if _checkSubset(atoms, label1, label2):
                                self.addBondTerm(data, bond, bu, global_data)
                if options['bond_angles']:
                    if subset1 is None:
                        for angle in bu.bonds.bondAngles():
                            self.addBondAngleTerm(data, angle, bu, global_data)
                    else:
                        for angle in bu.bonds.bondAngles():
                            atoms = [angle.a1, angle.a2, angle.ca]
                            if _checkSubset(atoms, label1, label2):
                                self.addBondAngleTerm(data, angle, bu,
                                                      global_data)
                d = options['dihedrals']
                i = options['impropers']
                if d or i:
                    if subset1 is None:
                        for angle in bu.bonds.dihedralAngles():
                            if angle.improper and i:
                                self.addImproperTerm(data, angle, bu,
                                                     global_data)
                            elif not angle.improper and d:
                                self.addDihedralTerm(data, angle, bu,
                                                     global_data)
                    else:
                        for angle in bu.bonds.dihedralAngles():
                            atoms = [angle.a1, angle.a2, angle.a3, angle.a4]
                            if _checkSubset(atoms, label1, label2):
                                if angle.improper and i:
                                    self.addImproperTerm(data, angle, bu,
                                                         global_data)
                                elif not angle.improper and d:
                                    self.addDihedralTerm(data, angle, bu,
                                                         global_data)
        if subset1 is not None:
            for atom in subset1.atomList():
                delattr(atom, label1)
            for atom in subset2.atomList():
                delattr(atom, label2)
        global_data.add('initialized', 'bonded')
        return {'harmonic_distance_term': data.get('bonds'),
                'harmonic_angle_term': data.get('angles'),
                'cosine_dihedral_term': data.get('dihedrals')}

    def evaluatorTerms(self, universe, subset1, subset2, global_data):
        from MMTK_forcefield import HarmonicDistanceTerm, HarmonicAngleTerm, \
             CosineDihedralTerm
        param = self.evaluatorParameters(universe, subset1, subset2,
                                         global_data)
        eval_list = []
        bonds = param['harmonic_distance_term']
        if bonds:
            indices = Numeric.array(map(lambda b: b[:2], bonds))
            parameters = Numeric.array(map(lambda b: b[2:], bonds))
            eval_list.append(HarmonicDistanceTerm(universe._spec,
                                                  indices, parameters))
        angles = param['harmonic_angle_term']
        if angles:
            indices = Numeric.array(map(lambda a: a[:3], angles))
            parameters = Numeric.array(map(lambda a: a[3:], angles))
            eval_list.append(HarmonicAngleTerm(universe._spec,
                                               indices, parameters))
        dihedrals = param['cosine_dihedral_term']
        if dihedrals:
            def _dihedral_parameters(p):
                return [p[4], Numeric.cos(p[5]), Numeric.sin(p[5]), p[6]]
            indices = Numeric.array(map(lambda d: d[:4], dihedrals))
            parameters = Numeric.array(map(_dihedral_parameters, dihedrals))
            eval_list.append(CosineDihedralTerm(universe._spec,
                                                indices, parameters))
        return eval_list

    def bondedForceFields(self):
        return [self]

    # The following methods must be overridden by derived classes.
    def addBondTerm(self, data, bond, object, global_data):
        raise AttributeError
    def addBondAngleTerm(self, data, angle, object, global_data):
        raise AttributeError
    def addDihedralTerm(self, data, dihedral, object, global_data):
        raise AttributeError
    def addImproperTerm(self, data, improper, object, global_data):
        raise AttributeError

    # The following methods are recommended for derived classes.
    # They allow to read out the force field specification, e.g. for
    # interfacing to other programs.
    def bonds(self, global_data):
        raise AttributeError
    def angles(self, global_data):
        raise AttributeError
    def dihedrals(self, global_data):
        raise AttributeError

# Check if an energy term matches the specified atom subset
def _checkSubset(atoms, label1, label2):
    s1 = 0
    s2 = 0
    for a in atoms:
        flag = 0
        if hasattr(a, label1):
            s1 = 1
            flag = 1
        if hasattr(a, label2):
            s2 = 1
            flag = 1
        if not flag:
            return 0
    return s1 and s2
