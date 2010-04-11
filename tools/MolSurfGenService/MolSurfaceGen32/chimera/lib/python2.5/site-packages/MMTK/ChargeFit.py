# This module contains code for charge fitting.
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

"""This module implements a numerically stable method (based on
Singular Value Decomposition) to fit point charges to values of an
electrostatic potential surface. Two types of constraints are
avaiable: a constraint on the total charge of the system or a subset
of the system, and constraints that force the charges of several atoms
to be equal. There is also a utility function that selects suitable
evaluation points for the electrostatic potential surface. For the
potential evaluation itself, some quantum chemistry program is needed.

The charge fitting method is described in [Article:Hinsen1997].
See also Example:Miscellaneous:charge_fit.py.
"""


from MMTK import Random, Units, Utility
from Scientific import N as Numeric
from Scientific import LA as LinearAlgebra
from Scientific.Geometry import Vector
import operator

class ChargeFit:

    """Fit of point charges to an electrostatic potential surface

    Constructor: ChargeFit(|system|, |points|, |constraints|=None)

    Arguments:

    |system| -- any chemical object, usually a molecule

    |points| -- a list of point/potential pairs (a vector for the
                evaluation point, a number for the potential),
                or a dictionary whose keys are Configuration objects
                and whose values are lists of point/potential pairs.
                The latter case permits combined fits for several
                conformations of the system.

    |constraints| -- a list of constraint objects (TotalChargeConstraint
                     and/or EqualityConstraint objects). If the constraints
                     are inconsistent, a warning is printed and the result
                     will satisfy the constraints only in a least-squares
                     sense.

    A ChargeFit object acts like a dictionary that stores the fitted charge
    value for each atom in the system.
    """

    def __init__(self, object, points, constraints = None):
        self.atoms = object.atomList()
        if type(points) != type({}):
            points = {None: points}
        if constraints is not None:
            constraints = ChargeConstraintSet(self.atoms, constraints)
        npoints = reduce(operator.add, map(len, points.values()))
        natoms = len(self.atoms)
        if npoints < natoms:
            raise ValueError("Not enough data points for fit")

        m = Numeric.zeros((npoints, natoms), Numeric.Float)
        phi = Numeric.zeros((npoints,), Numeric.Float)
        i = 0
        for conf, pointlist in points.items():
            for r, p in pointlist:
                for j in range(natoms):
                    m[i, j] = 1./(r-self.atoms[j].position(conf)).length()
                phi[i] = p
                i = i + 1
        m = m*Units.electrostatic_energy

        m_test = m
        phi_test = phi

        if constraints is not None:
            phi = phi-Numeric.dot(m, constraints.bi_c)
            m = Numeric.dot(m, constraints.p)
            c_rank = constraints.rank
        else:
            c_rank = 0

        u, s, vt = LinearAlgebra.singular_value_decomposition(m)
        s_test = s[:len(s)-c_rank]
        cutoff = 1.e-10*Numeric.maximum.reduce(s_test)
        nonzero = Numeric.repeat(s_test, Numeric.not_equal(s_test, 0.))
        self.rank = len(nonzero)
        self.condition = Numeric.maximum.reduce(nonzero) / \
                         Numeric.minimum.reduce(nonzero)
        self.effective_rank = Numeric.add.reduce(Numeric.greater(s, cutoff))
        if self.effective_rank < self.rank:
            self.effective_condition = Numeric.maximum.reduce(nonzero) / cutoff
        else:
            self.effective_condition = self.condition
        if self.effective_rank < natoms-c_rank:
            Utility.warning('Not all charges are uniquely determined' +
                            ' by the available data')

        for i in range(natoms):
            if s[i] > cutoff:
                s[i] = 1./s[i]
            else:
                s[i] = 0.
        q = Numeric.dot(Numeric.transpose(vt),
                        s*Numeric.dot(Numeric.transpose(u)[:natoms, :], phi))
        if constraints is not None:
            q = constraints.bi_c + Numeric.dot(constraints.p, q)

        deviation = Numeric.dot(m_test, q)-phi_test
        self.rms_error = Numeric.sqrt(Numeric.dot(deviation, deviation))
        deviation = Numeric.fabs(deviation/phi_test)
        self.relative_rms_error = Numeric.sqrt(Numeric.dot(deviation,
                                                           deviation))

        self.charges = {}
        for i in range(natoms):
            self.charges[self.atoms[i]] = q[i]

    def __getitem__(self, item):
        return self.charges[item]


class TotalChargeConstraint:

    """Constraint on the total system charge

    To be used with Class:MMTK.ChargeFit.ChargeFit.

    Constructor:  TotalChargeConstraint(|object|, |charge|)

    Arguments:

    |object| -- any object whose total charge is to be constrained

    |charge| -- the total charge value
    """

    def __init__(self, object, charge):
        self.atoms = object.atomList()
        self.charge = charge

    def __len__(self):
        return 1

    def setCoefficients(self, atoms, b, c, i):
        for a in self.atoms:
            j = atoms.index(a)
            b[i, j] = 1.
        c[i] = self.charge


class EqualityConstraint:

    """Constraint forcing two charges to be equal

    To be used with Class:MMTK.ChargeFit.ChargeFit.

    Constructor:  EqualityConstraint(|atom1|, |atom2|), where
    |atom1| and |atom2| are the two atoms whose charges should be
    equal.

    Any atom may occur in more than one EqualityConstraint object,
    in order to keep the charges of more than two atoms equal.
    """

    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2

    def __len__(self):
        return 1

    def setCoefficients(self, atoms, b, c, i):
        b[i, atoms.index(self.a1)] = 1.
        b[i, atoms.index(self.a2)] = -1.
        c[i] = 0.


class ChargeConstraintSet:

    def __init__(self, atoms, constraints):
        self.atoms = atoms
        natoms = len(self.atoms)
        nconst = reduce(operator.add, map(len, constraints))
        b = Numeric.zeros((nconst, natoms), Numeric.Float)
        c = Numeric.zeros((nconst,), Numeric.Float)
        i = 0
        for cons in constraints:
            cons.setCoefficients(self.atoms, b, c, i)
            i = i + len(cons)
        u, s, vt = LinearAlgebra.singular_value_decomposition(b)
        self.rank = 0
        for i in range(min(natoms, nconst)):
            if s[i] > 0.:
                self.rank = self.rank + 1
        self.b = b
        self.bi = LinearAlgebra.generalized_inverse(b)
        self.p = Numeric.identity(natoms)-Numeric.dot(self.bi, self.b)
        self.c = c
        self.bi_c = Numeric.dot(self.bi, c)
        c_test = Numeric.dot(self.b, self.bi_c)
        if Numeric.add.reduce((c_test-c)**2)/nconst > 1.e-12:
            Utility.warning("The charge constraints are inconsistent."
                            " They will be applied as a least-squares"
                            " condition.")


def evaluationPoints(object, n, smallest = 0.3, largest = 0.5):
    """Returns a list of |n| points suitable for the evaluation of
    the electrostatic potential around |object|. The points are chosen
    at random and uniformly in a shell around the object such that
    no point has a distance larger than |largest| from any atom or
    smaller than |smallest| from any non-hydrogen atom.
    """
    atoms = object.atomList()
    p1, p2 = object.boundingBox()
    margin = Vector(largest, largest, largest)
    p1 = p1 - margin
    p2 = p2 + margin
    a, b, c = tuple(p2-p1)
    offset = 0.5*Vector(a, b, c)
    points = []
    while len(points) < n:
        p = p1 + Random.randomPointInBox(a, b, c) + offset
        m = 2*largest
        ok = 1
        for atom in atoms:
            d = (p-atom.position()).length()
            m = min(m, d)
            if d < smallest and atom.symbol != 'H':
                ok = 0
            if not ok: break
        if ok and m <= largest:
            points.append(p)
    return points


if __name__ == '__main__':

    from MMTK import *

    a1 = Atom('C', position=Vector(-0.05,0.,0.))
    a2 = Atom('C', position=Vector( 0.05,0.,0.))
    system = Collection(a1, a2)

    a1.charge = -0.75
    a2.charge = 0.15

    points = []
    for r in evaluationPoints(system, 50):
        p = 0.
        for atom in system.atomList():
            p = p + atom.charge/(r-atom.position()).length()
        points.append((r, p*Units.electrostatic_energy))

    constraints = [TotalChargeConstraint(system, 0.)]
    constraints = [EqualityConstraint(a1, a2)]
    constraints = None

    f = ChargeFit(system, points, constraints)
    print f[a1], a1.charge
    print f[a2], a2.charge
