# Deformation force field
#
# Written by Konrad Hinsen
# last revision: 2007-7-4
#

_undocumented = 1

from ForceField import ForceField, ForceFieldData
try:
    from MMTK_forcefield import NonbondedList, NonbondedListTerm
    from MMTK_deformation import DeformationTerm
except ImportError:
    pass
from Scientific import N as Numeric

#
# The deformation force field class
#
class DeformationForceField(ForceField):

    """Deformation force field for protein normal mode calculations

    Constructor: DeformationForceField(|range|=0.7, |cutoff|=1.2,
                                       |factor|=46402.)

    Arguments:

    |range| -- the range parameter

    |cutoff| -- the cutoff for pair interactions, should be significantly
                larger than |range|.

    |factor| -- a global scaling factor.

    Pair interactions in periodic systems are calculated using the
    minimum-image convention; the cutoff should therefore never be
    larger than half the smallest edge length of the elementary
    cell.

    The pair interaction force constant has the form
    k(r)=|factor|*exp(-(r**2-0.01)/|range|**2). The default value
    for |range| is appropriate for a C-alpha model of a protein.
    The offset of 0.01 is a convenience for defining |factor|;
    with this definition, |factor| is the force constant for a
    distance of 0.1nm.
    See [Article:Hinsen1998] for details.
    """

    def __init__(self, fc_length = 0.7, cutoff = 1.2, factor = 46402.):
        self.arguments = (fc_length, cutoff, factor)
        ForceField.__init__(self, 'deformation')
        self.arguments = (fc_length, cutoff, factor)
        self.fc_length = fc_length
        self.cutoff = cutoff
        self.factor = factor

    def ready(self, global_data):
        return 1

    def evaluatorTerms(self, universe, subset1, subset2, global_data):
        if subset1 is not None:
            for s1, s2 in [(subset1, subset2), (subset2, subset1)]:
                set = {}
                for a in s1.atomList():
                    set[a.index] = None
                for a in s2.atomList():
                    try:
                        del set[a.index]
                    except KeyError: pass
            set = {}
            for a in subset1.atomList():
                set[a.index] = None
            for a in subset2.atomList():
                set[a.index] = None
            atom_subset = set.keys()
            atom_subset.sort()
            atom_subset = Numeric.array(atom_subset)
        else:
            atom_subset = Numeric.array([], Numeric.Int)
        nothing = Numeric.zeros((0,2), Numeric.Int)
        nbl = NonbondedList(nothing, nothing, atom_subset, universe._spec,
                            self.cutoff)
        update = NonbondedListTerm(nbl)
        ev = DeformationTerm(universe._spec, nbl, self.fc_length,
                             self.cutoff, self.factor, 1.)
        return [update, ev]
