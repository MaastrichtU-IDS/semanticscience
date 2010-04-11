# This module handles input and application of Amber parameter files.
#
# Written by Konrad Hinsen
# last revision: 2007-5-28
#

_undocumented = 1

from MMTK import Units
from Scientific.IO.FortranFormat import FortranFormat, FortranLine
from Scientific.IO.TextFile import TextFile
from Scientific.DictWithDefault import DictWithDefault
import os, string

amber_energy_unit = Units.kcal/Units.mol
amber_length_unit = Units.Ang
amber_angle_unit = Units.deg
amber_fc_angle_unit = Units.rad

#
# The force field parameter file
#
class AmberParameters:

    def __init__(self, file, modifications=[]):
        if isinstance(file, str):
            file = TextFile(file)
        title = file.readline()[:-1]

        self.atom_types = DictWithDefault(None)
        self._readAtomTypes(file)

        format = FortranFormat('20(A2,2X)')
        done = 0
        while not done:
            l = FortranLine(file.readline()[:-1], format)
            for entry in l:
                name = _normalizeName(entry)
                if len(name) == 0:
                    done = 1
                    break
                try: # ignore errors for now
                    self.atom_types[name].hydrophylic = 1
                except: pass

        self.bonds = {}
        self._readBondParameters(file)

        self.bond_angles = {}
        self._readAngleParameters(file)

        self.dihedrals = {}
        self.dihedrals_2 = {}
        self._readDihedralParameters(file)

        self.impropers = {}
        self.impropers_1 = {}
        self.impropers_2 = {}
        self._readImproperParameters(file)

        self.hbonds = {}
        self._readHbondParameters(file)

        self.lj_equivalent = {}
        format = FortranFormat('20(A2,2X)')
        while 1:
            l = FortranLine(file.readline()[:-1], format)
            if l.isBlank(): break
            name1 = _normalizeName(l[0])
            for s in l[1:]:
                name2 = _normalizeName(s)
                self.lj_equivalent[name2] = name1

        self.ljpar_sets = {}
        while 1:
            l = FortranLine(file.readline()[:-1], 'A4,6X,A2')
            if l[0] == 'END ': break
            set_name = _normalizeName(l[0])
            ljpar_set = AmberLJParameterSet(set_name, l[1])
            self.ljpar_sets[set_name] = ljpar_set
            self._readLJParameters(file, ljpar_set)

        file.close()

        for mod, ljname in modifications:
            if isinstance(mod, str):
                file = TextFile(mod)
            else:
                file = mod
            title = file.readline()[:-1]
            blank = file.readline()[:-1]
            while 1:
                keyword = file.readline()
                if not keyword: break
                keyword = string.strip(keyword)[:4]
                if keyword == 'MASS':
                    self._readAtomTypes(file)
                elif keyword == 'BOND':
                    self._readBondParameters(file)
                elif keyword == 'ANGL':
                    self._readAngleParameters(file)
                elif keyword == 'DIHE':
                    self._readDihedralParameters(file)
                elif keyword == 'IMPR':
                    self._readImproperParameters(file)
                elif keyword == 'HBON':
                    self._readHbondParameters(file)
                elif keyword == 'NONB':
                    self._readLJParameters(file, self.ljpar_sets[ljname])

    def _readAtomTypes(self, file):
        format = FortranFormat('A2,1X,F10.2')
        while 1:
            l = FortranLine(file.readline()[:-1], format)
            if l.isBlank(): break
            name = _normalizeName(l[0])
            self.atom_types[name] = AmberAtomType(name, l[1])

    def _readBondParameters(self, file):
        format = FortranFormat('A2,1X,A2,2F10.2')
        while 1:
            l = FortranLine(file.readline()[:-1], format)
            if l.isBlank(): break
            name1 = _normalizeName(l[0])
            name2 = _normalizeName(l[1])
            name1, name2 = _sort(name1, name2)
            self.bonds[(name1, name2)] = \
                               AmberBondParameters(self.atom_types[name1],
                                                   self.atom_types[name2],
                                                   l[2], l[3])

    def _readAngleParameters(self, file):
        format = FortranFormat('A2,1X,A2,1X,A2,2F10.2')
        while 1:
            l = FortranLine(file.readline()[:-1], format)
            if l.isBlank(): break
            name1 = _normalizeName(l[0])
            name2 = _normalizeName(l[1])
            name3 = _normalizeName(l[2])
            name1, name3 = _sort(name1, name3)
            self.bond_angles[(name1, name2, name3)] = \
                   AmberBondAngleParameters(self.atom_types[name1],
                                            self.atom_types[name2],
                                            self.atom_types[name3],
                                            l[3], l[4])

    def _readDihedralParameters(self, file):
        format = FortranFormat('A2,1X,A2,1X,A2,1X,A2,I4,3F15.2')
        append = None
        while 1:
            l = FortranLine(file.readline()[:-1], format)
            if l.isBlank(): break
            name1 = _normalizeName(l[0])
            name2 = _normalizeName(l[1])
            name3 = _normalizeName(l[2])
            name4 = _normalizeName(l[3])
            name1, name2, name3, name4 = _sort4(name1, name2, name3, name4)
            if append is not None:
                append.addTerm(l[4], l[5], l[6], l[7])
                if l[7] >= 0: append = None
            else:
                p = AmberDihedralParameters(self.atom_types[name1],
                                            self.atom_types[name2],
                                            self.atom_types[name3],
                                            self.atom_types[name4],
                                            l[4], l[5], l[6], l[7])
                if name1 == 'X' and name4 == 'X':
                    self.dihedrals_2[(name2, name3)] = p
                else:
                    self.dihedrals[(name1, name2, name3, name4)] = p
                if l[7] < 0: append = p

    def _readImproperParameters(self, file):
        format = FortranFormat('A2,1X,A2,1X,A2,1X,A2,I4,3F15.2')
        while 1:
            l = FortranLine(file.readline()[:-1], format)
            if l.isBlank(): break
            name1 = _normalizeName(l[0])
            name2 = _normalizeName(l[1])
            name3 = _normalizeName(l[2])
            name4 = _normalizeName(l[3])
            if name1 == 'X':
                if name2 == 'X':
                    name1 = name3
                    name2 = name4
                    name3 = 'X'
                    name4 = 'X'
                else:
                    name1 = name3
                    name2, name3 = _sort(name2, name4)
                    name4 = 'X'
            else:
                name1, name2, name3, name4 = \
                       (name3, ) + _sort3(name1, name2, name4)
            p = AmberImproperParameters(self.atom_types[name1],
                                        self.atom_types[name2],
                                        self.atom_types[name3],
                                        self.atom_types[name4],
                                        l[4], l[5], l[6], l[7])
            if name4 == 'X':
                if name3 == 'X':
                    self.impropers_2[(name1, name2)] = p
                else:
                    self.impropers_1[(name1, name2, name3)] = p
            else:
                self.impropers[(name1, name2, name3, name4)] = p

    def _readHbondParameters(self, file):
        format = FortranFormat('2X,A2,2X,A2,2X,2F10.2')
        while 1:
            l = FortranLine(file.readline()[:-1], format)
            if l.isBlank(): break
            name1 = _normalizeName(l[0])
            name2 = _normalizeName(l[1])
            name1, name2 = _sort(name1, name2)
            self.hbonds[(name1, name2)] = \
                                AmberHbondParameters(self.atom_types[name1],
                                                     self.atom_types[name2],
                                                     l[2], l[3])

    def _readLJParameters(self, file, ljpar_set):
        format = FortranFormat('2X,A2,6X,3F10.6')
        while 1:
            l = FortranLine(file.readline()[:-1], format)
            if l.isBlank(): break
            name = _normalizeName(l[0])
            ljpar_set.addEntry(name, l[1], l[2], l[3])

    def bondParameters(self, name1, name2):
        name1 = _normalizeName(name1)
        name2 = _normalizeName(name2)
        name1, name2 = _sort(name1, name2)
        p = self.bonds[(name1, name2)]
        return (p.l*amber_length_unit,
                p.k*amber_energy_unit/amber_length_unit**2)

    def bondAngleParameters(self, name1, name2, name3):
        name1 = _normalizeName(name1)
        name2 = _normalizeName(name2)
        name3 = _normalizeName(name3)
        name1, name3 = _sort(name1, name3)
        p = self.bond_angles[(name1, name2, name3)]
        return (p.angle*amber_angle_unit,
                p.k*amber_energy_unit/amber_fc_angle_unit)

    def dihedralParameters(self, name1, name2, name3, name4):
        name1 = _normalizeName(name1)
        name2 = _normalizeName(name2)
        name3 = _normalizeName(name3)
        name4 = _normalizeName(name4)
        name1, name2, name3, name4 = _sort4(name1, name2, name3, name4)
        try:
            p = self.dihedrals[(name1, name2, name3, name4)]
        except KeyError:
            try:
                p = self.dihedrals_2[(name2, name3)]
            except KeyError: p = None
        if p is None:
            return p
        else:
            return map(lambda p: (p[2], p[1]*amber_angle_unit,
                                  p[0]*amber_energy_unit),
                       p.terms)

    def improperParameters(self, name1, name2, name3, name4):
        name1 = _normalizeName(name1)
        name2 = _normalizeName(name2)
        name3 = _normalizeName(name3)
        name4 = _normalizeName(name4)
        name2, name3, name4 = _sort3(name2, name3, name4)
        p = None
        try:
            p = self.impropers[(name1, name2, name3, name4)]
        except KeyError:
            for names in [(name2, name3), (name2, name4), (name3, name4)]:
                try:
                    p = self.impropers_1[(name1,) + names]
                except KeyError: pass
            if p is None:
                for name in [name2, name3, name4]:
                    try:
                        p = self.impropers_2[(name1, name)]
                    except KeyError: pass
        if p is None:
            return p
        else:
            return map(lambda p: (p[2], p[1]*amber_angle_unit,
                                  p[0]*amber_energy_unit),
                       p.terms)

    def ljParameters(self, name, parameter_set = None):
        if parameter_set is None:
            ljp = self.default_ljpar_set
        else:
            ljp = self.ljpar_sets[parameter_set]
        try:
            name = self.lj_equivalent[name]
        except KeyError: pass
        if ljp.type == 'RE':
            p = ljp.getEntry(name)
            return (p[1]*amber_energy_unit,
                    1.78179743628*p[0]*amber_length_unit, 0)
        elif ljp.type == 'AC':
            p = ljp.getEntry(name)
            a = p[0]*amber_energy_unit*amber_length_unit**12
            c = p[1]*amber_energy_unit*amber_length_unit**6
            if c == 0.:
                eps = 0.
            else:
                eps = 0.25*c*c/a
            if a == 0.:
                sigma = 0.
            else:
                sigma = (a/c)**(1./6.)
            return (eps, sigma, 1)
        else:
            raise ValueError('Type ' + ljp.type + ' not supported.')

#
# Atom type class
#
class AmberAtomType:

    def __init__(self, name, mass):
        self.name = name
        self.mass = mass
        self.hydrophylic = 0

#
# Bond parameter class
#
class AmberBondParameters:

    def __init__(self, a1, a2, k, l):
        self.a1 = a1
        self.a2 = a2
        self.k = k
        self.l = l

#
# Bond angle parameter class
#
class AmberBondAngleParameters:

    def __init__(self, a1, a2, a3, k, angle):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.k = k
        self.angle = angle

#
# Dihedral angle parameter class
#
class AmberDihedralParameters:

    def __init__(self, a1, a2, a3, a4, divf, k, delta, n):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.terms = [(k/divf, delta, int(abs(n)))]

    def addTerm(self, divf, k, delta, n):
        self.terms.append((k/divf, delta, int(abs(n))))

    def __repr__(self):
        if self.a1 is None and self.a4 is None:
            return 'X-' + self.a2.name + '-' + self.a3.name + '-X'
        else:
            return self.a1.name + '-' + self.a2.name + '-' + \
                   self.a3.name + '-' + self.a4.name
    __str__ = __repr__

#
# Improper dihedral angle parameter class
#
class AmberImproperParameters:

    def __init__(self, a1, a2, a3, a4, divf, k, delta, n):
        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4
        self.terms = [(0.5*k, delta, int(abs(n)))]

    def addTerm(self, divf, k, delta, n):
        self.terms.append((0.5*k, delta, int(abs(n))))

    def __repr__(self):
        if self.a4 is None:
            if self.a3 is None:
                return self.a1.name + '-' + self.a2.name + '-X-X'
            else:
                return self.a1.name + '-' + self.a2.name + '-' + \
                       self.a3.name + '-X'
        else:
            return self.a1.name + '-' + self.a2.name + '-' + \
                   self.a3.name + '-' + self.a4.name
    __str__ = __repr__

#
# H-bond parameter class
#
class AmberHbondParameters:

    def __init__(self, a1, a2, a, b):
        self.a1 = a1
        self.a2 = a2
        self.a = a
        self.b = b

#
# Lennard-Jones parameter sets
#
class AmberLJParameterSet:

    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.entries = {}

    def addEntry(self, name, p1, p2, p3):
        if self.type == 'SK':
            self.entries[name] = (p1, p2, p3)
        else:
            self.entries[name] = (p1, p2)

    def getEntry(self, name):
        return self.entries[name]

#
# Utility functions
#
def _normalizeName(name):
    return name.strip()

def _sort(s1, s2):
    if s2 < s1:
        return s2, s1
    else:
        return s1, s2

def _sort3(s1, s2, s3):
    if s2 < s1:
        s1, s2 = s2, s1
    if s3 < s2:
        s2, s3 = s3, s2
    if s2 < s1:
        s1, s2 = s2, s1
    return s1, s2, s3

def _sort4(s1, s2, s3, s4):
    if s3 < s2:
        return s4, s3, s2, s1
    else:
        return s1, s2, s3, s4
