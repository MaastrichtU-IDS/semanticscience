# Harmonic restraint terms that can be added to a force field.
#
# Written by Konrad Hinsen
# last revision: 2008-1-10
#

"""This module contains harmonic restraint terms that can be added
to any force field.

Example:

from MMTK import *
from MMTK.ForceFields import Amber94ForceField
from MMTK.ForceFields.Restraints import HarmonicDistanceRestraint

universe = InfiniteUniverse()
universe.protein = Protein('bala1')
force_field = Amber94ForceField() + \
              HarmonicDistanceRestraint(universe.protein[0][1].peptide.N,
                                        universe.protein[0][1].peptide.O,
                                        0.5, 10.)
universe.setForceField(force_field)
"""

from ForceField import ForceField
from MMTK_forcefield import HarmonicDistanceTerm, HarmonicAngleTerm, \
                            CosineDihedralTerm
from Scientific import N as Numeric

class HarmonicDistanceRestraint(ForceField):

    """Harmonic distance restraint between two atoms

    Constructor: HarmonicDistanceRestraint(|atom1|, |atom2|,
                                           |distance|, |force_constant|)

    Arguments:

    |atom1|, |atom2| -- the two atoms whose distance is restrained

    |distance| -- the distance at which the restraint is zero

    |force_constant| -- the force constant of the restraint term

    The functional form of the restraint is
    |force_constant|*((r1-r2).length()-|distance|)**2, where
    r1 and r2 are the positions of the two atoms.
    """

    def __init__(self, atom1, atom2, distance, force_constant):
        self.index1, self.index2 = self.getAtomParameterIndices((atom1, atom2))
        self.arguments = (self.index1, self.index2, distance, force_constant) 
        self.distance = distance
        self.force_constant = force_constant
        ForceField.__init__(self, 'harmonic distance restraint')

    def evaluatorParameters(self, universe, subset1, subset2, global_data):
        if subset1 is not None:
            s1 = subset1.atomList()
            s2 = subset2.atomList()
            if not ((self.atom1 in s1 and self.atom2 in s2) or \
                    (self.atom1 in s2 and self.atom2 in s1)):
                raise ValueError("restraint outside subset")
        return {'harmonic_distance_term':
                [(self.index1, self.index2,
                  self.distance, self.force_constant)]}

    def evaluatorTerms(self, universe, subset1, subset2, global_data):
        params = self.evaluatorParameters(universe, subset1, subset2,
                                          global_data)['harmonic_distance_term']
        assert len(params) == 1
        indices = Numeric.array([params[0][:2]])
        parameters = Numeric.array([params[0][2:]])
        return [HarmonicDistanceTerm(universe._spec, indices, parameters,
                                     self.name)]

    def description(self):
        return 'ForceFields.Restraints.' + self.__class__.__name__ + \
               `self.arguments`


class HarmonicAngleRestraint(ForceField):

    """Harmonic angle restraint between three atoms

    Constructor: HarmonicAngleRestraint(|atom1|, |atom2|, |atom3|,
                                        |angle|, |force_constant|)

    Arguments:

    |atom1|, |atom2|, |atom3| -- the three atoms whose angle is restrained;
    |atom2| is the central atom

    |angle| -- the angle at which the restraint is zero

    |force_constant| -- the force constant of the restraint term

    The functional form of the restraint is
    |force_constant|*(phi-|angle|)**2, where
    phi is the angle |atom1|-|atom2|-|atom3|.
    """

    def __init__(self, atom1, atom2, atom3, angle, force_constant):
        self.index1, self.index2, self.index3 = \
                    self.getAtomParameterIndices((atom1, atom2, atom3))
        self.arguments = (self.index1, self.index2, self.index3,
                          angle, force_constant) 
        self.angle = angle
        self.force_constant = force_constant
        ForceField.__init__(self, 'harmonic angle restraint')

    def evaluatorParameters(self, universe, subset1, subset2, global_data):
        return {'harmonic_angle_term':
                 [(self.index1, self.index2, self.index3,
                   self.angle, self.force_constant)]}

    def evaluatorTerms(self, universe, subset1, subset2, global_data):
        params = self.evaluatorParameters(universe, subset1, subset2,
                                          global_data)['harmonic_angle_term']
        assert len(params) == 1
        indices = Numeric.array([params[0][:3]])
        parameters = Numeric.array([params[0][3:]])
        return [HarmonicAngleTerm(universe._spec, indices, parameters,
                                  self.name)]

class HarmonicDihedralRestraint(ForceField):

    """Harmonic dihedral angle restraint between three atoms

    Constructor: HarmonicDihedralRestraint(|atom1|, |atom2|, |atom3|, |atom4|,
                                           |angle|, |force_constant|)

    Arguments:

    |atom1|, |atom2|, |atom3|, |atom4| -- the four atoms whose dihedral angle
    is restrained; |atom2| and |atom3| are on the common axis

    |angle| -- the dihedral angle at which the restraint is zero

    |force_constant| -- the force constant of the restraint term

    The functional form of the restraint is
    |force_constant|*(phi-|distance|)**2, where
    phi is the dihedral angle |atom1|-|atom2|-|atom3|-|atom4|.
    """

    def __init__(self, atom1, atom2, atom3, atom4, dihedral, force_constant):
        self.index1, self.index2, self.index3, self.index4 = \
                   self.getAtomParameterIndices((atom1, atom2, atom3, atom4))
        self.dihedral = dihedral
        self.force_constant = force_constant
        self.arguments = (self.index1, self.index2, self.index3, self.index4,
                          dihedral, force_constant) 
        ForceField.__init__(self, 'harmonic dihedral restraint')

    def evaluatorParameters(self, universe, subset1, subset2, global_data):
        return {'cosine_dihedral_term': [(self.index1, self.index2,
                                          self.index3, self.index4,
                                          0., self.dihedral,
                                          0., self.force_constant)]}

    def evaluatorTerms(self, universe, subset1, subset2, global_data):
        params = self.evaluatorParameters(universe, subset1, subset2,
                                          global_data)['cosine_dihedral_term']
        assert len(params) == 1
        indices = Numeric.array([params[:4]])
        parameters = Numeric.array([params[4:]])
        return [CosineDihedralTerm(universe._spec, indices, parameters,
                                   self.name)]
