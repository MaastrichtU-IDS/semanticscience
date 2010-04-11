# Detailed harmonic force field for proteins
#
# Written by Konrad Hinsen
# last revision: 2007-2-14
#

from NonBondedInteractions import NonBondedForceField
from Amber.AmberForceField import AmberBondedForceField
from MMForceField import MMAtomParameters
from ForceField import ForceField, CompoundForceField
from MMTK_deformation import DeformationTerm
from Scientific.Geometry import Transformation
from Scientific import N as Numeric

class BondForceField(AmberBondedForceField):

    def __init__(self, bonds=1, angles=1, dihedrals=1):
        AmberBondedForceField.__init__(self)
        self.arguments = (bonds, angles, dihedrals)
        self.bonded = self

    def addBondTerm(self, data, bond, object, global_data):
        if not self.arguments[0]:
            return
        a1 = bond.a1
        a2 = bond.a2
        i1 = a1.index
        i2 = a2.index
        global_data.add('excluded_pairs', (i1, i2))
        t1 = global_data.atom_type[a1]
        t2 = global_data.atom_type[a2]
        try:
            p = self.dataset.bondParameters(t1, t2)
        except KeyError:
            raise KeyError('No parameters for bond ' + `a1` +  '--' + `a2`)
        if p is not None:
            d = data.get('universe').distance(a1, a2)
            data.add('bonds', (i1, i2, d, p[1]))

    def addBondAngleTerm(self, data, angle, object, global_data):
        if not self.arguments[1]:
            return
        a1 = angle.a1
        a2 = angle.a2
        ca = angle.ca
        i1 = a1.index
        i2 = a2.index
        ic = ca.index
        global_data.add('excluded_pairs', (i1, i2))
        t1 = global_data.atom_type[a1]
        t2 = global_data.atom_type[a2]
        tc = global_data.atom_type[ca]
        try:
            p = self.dataset.bondAngleParameters(t1, tc, t2)
        except KeyError:
            raise KeyError('No parameters for angle ' + `a1` +
                            '--' + `ca` + '--' + `a2`)
        if p is not None:
            v1 = a1.position()-ca.position()
            v2 = a2.position()-ca.position()
            angle = v1.angle(v2)
            data.add('angles', (i1, ic, i2, angle) + p[1:])

    def addDihedralTerm(self, data, dihedral, object, global_data):
        if not self.arguments[2]:
            return
        a1 = dihedral.a1
        a2 = dihedral.a2
        a3 = dihedral.a3
        a4 = dihedral.a4
        i1 = a1.index
        i2 = a2.index
        i3 = a3.index
        i4 = a4.index
        global_data.add('1_4_pairs', (i1, i4))
        t1 = global_data.atom_type[a1]
        t2 = global_data.atom_type[a2]
        t3 = global_data.atom_type[a3]
        t4 = global_data.atom_type[a4]
        terms = self.dataset.dihedralParameters(t1, t2, t3, t4)
        if terms is not None:
            v1 = a1.position()-a2.position()
            v2 = a2.position()-a3.position()
            v3 = a4.position()-a3.position()
            a = v1.cross(v2).normal()
            b = v3.cross(v2).normal()
            cos = a*b
            sin = b.cross(a)*v2/v2.length()
            dihedral = Transformation.angleFromSineAndCosine(sin, cos)
            if dihedral > Numeric.pi:
                dihedral = dihedral - 2.*Numeric.pi
            for p in terms:
                if p[2] != 0.:
                    mult = p[0]
                    phase = Numeric.fmod(Numeric.pi-mult*dihedral,
                                         2.*Numeric.pi)
                    if phase < 0.:
                        phase = phase + 2.*Numeric.pi
                    data.add('dihedrals', (i1, i2, i3, i4,
                                           p[0], phase) + p[2:])

    def addImproperTerm(self, data, improper, object, global_data):
        if not self.arguments[2]:
            return
        a1 = improper.a1
        a2 = improper.a2
        a3 = improper.a3
        a4 = improper.a4
        i1 = a1.index
        i2 = a2.index
        i3 = a3.index
        i4 = a4.index
        t1 = global_data.atom_type[a1]
        t2 = global_data.atom_type[a2]
        t3 = global_data.atom_type[a3]
        t4 = global_data.atom_type[a4]
        terms = self.dataset.improperParameters(t1, t2, t3, t4)
        if terms is not None:
            atoms = [(t2,i2,a2), (t3,i3,a3), (t4,i4,a4)]
            atoms.sort(_order)
            i2, i3, i4 = tuple(map(lambda t: t[1], atoms))
            a2, a3, a4 = tuple(map(lambda t: t[2], atoms))
            v1 = a2.position()-a3.position()
            v2 = a3.position()-a1.position()
            v3 = a4.position()-a1.position()
            a = v1.cross(v2).normal()
            b = v3.cross(v2).normal()
            cos = a*b
            sin = b.cross(a)*v2/v2.length()
            dihedral = Transformation.angleFromSineAndCosine(sin, cos)
            if dihedral > Numeric.pi:
                dihedral = dihedral - 2.*Numeric.pi
            for p in terms:
                if p[2] != 0.:
                    mult = p[0]
                    phase = Numeric.fmod(Numeric.pi-mult*dihedral,
                                         2.*Numeric.pi)
                    if phase < 0.:
                        phase = phase + 2.*Numeric.pi
                    data.add('dihedrals', (i2, i3, i1, i4,
                                           p[0], phase) + p[2:])

def _order(a1, a2):
    ret = cmp(a1[0], a2[0])
    if ret == 0:
        ret = cmp(a1[1], a2[1])
    return ret

#
# Mid-range harmonic force field to complement bonded part
#
class MidrangeForceField(NonBondedForceField):

    def __init__(self, fc_length = 0.3, cutoff = 0.5, factor = 59908.8):
        NonBondedForceField.__init__(self, 'harmonic')
        self.arguments = (fc_length, cutoff, factor)
        self.fc_length = fc_length
        self.cutoff = cutoff
        self.factor = factor
        self.one_four_factor = 0.5

    def evaluatorParameters(self, universe, subset1, subset2, global_data):
        excluded_pairs, one_four_pairs, atom_subset = \
                        self.excludedPairs(subset1, subset2, global_data)
        if self.cutoff is None:
            cutoff = 0.
        else:
            cutoff = self.cutoff
        return {'deformation_term': {'cutoff': cutoff,
                                      'fc_length': self.fc_length,
                                      'scale_factor': self.factor,
                                      'one_four_factor': self.one_four_factor},
                 'nonbonded': {'excluded_pairs': excluded_pairs,
                               'one_four_pairs': one_four_pairs,
                               'atom_subset': atom_subset},
                }

    def evaluatorTerms(self, universe, subset1, subset2, global_data):
        param = self.evaluatorParameters(universe, subset1, subset2,
                                         global_data)['deformation_term']
        nblist, nblist_update = \
                self.nonbondedList(universe, subset1, subset2, global_data)
        ev = DeformationTerm(universe._spec, nblist, param['fc_length'],
                             param['cutoff'], param['scale_factor'],
                             param['one_four_factor'])
        return [nblist_update, ev]


class HarmonicForceField(MMAtomParameters, CompoundForceField):

    """Simplified harmonic force field for normal mode calculations

    Constructor: HarmonicForceField()

    This force field is made up of the bonded terms from the Amber 94
    force field with the equilibrium positions of all terms changed
    to the corresponding values in the input configuration, such that
    the input configuration becomes an energy minimum by construction.
    The nonbonded terms are replaced by a generic short-ranged
    deformation term.

    See [Article:Hinsen1999b] for a description of this force field,
    and [Article:Viduna2000] for an application to DNA.
    """

    def __init__(self, fc_length = 0.45, cutoff = 0.6, factor = 400.):
        self.arguments = (fc_length, cutoff, factor)
        self.bonded = BondForceField(1, 1, 1)
        self.midrange = MidrangeForceField(fc_length, cutoff, factor)
        apply(CompoundForceField.__init__, (self, self.bonded, self.midrange))

    description = ForceField.description


if __name__ == '__main__':

    from MMTK import *
    from MMTK.Proteins import Protein
    from MMTK.NormalModes import NormalModes
    world = InfiniteUniverse(HarmonicForceField(bonds=1,angles=1,dihedrals=1))
    world.protein = Protein('bala1')
    print world.energy()
    modes = NormalModes(world)
    for m in modes:
        print m
