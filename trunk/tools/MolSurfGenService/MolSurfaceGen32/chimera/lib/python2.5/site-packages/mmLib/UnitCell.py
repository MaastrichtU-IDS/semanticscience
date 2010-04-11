## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Classes for handling unit cell transformation.
"""
import math

try:
    import numpy
    try:
        from numpy.oldnumeric import linear_algebra as linalg
    except ImportError:
        from numpy.linalg import old as linalg
except ImportError:
    import NumericCompat as numpy
    from NumericCompat import linalg

import AtomMath
import SpaceGroups


class UnitCell(object):
    """Class for storing and performing calculations on unit cell
    parameters.  The constructor expects alpha, beta, and gamma to be in
    degrees, but converts them to radians.  Set angle_units = "rad" if
    the alpha, beta, and gamma are already in radians.
    """
    def __init__(self,
                 a = 1.0,
                 b = 1.0,
                 c = 1.0,
                 alpha = 90.0,
                 beta = 90.0,
                 gamma = 90.0,
                 space_group = "P1",
                 angle_units = "deg"):

        assert angle_units == "deg" or angle_units == "rad"

        self.a = a
        self.b = b
        self.c = c

        if angle_units == "deg":
            self.alpha = math.radians(alpha) 
            self.beta  = math.radians(beta)
            self.gamma = math.radians(gamma)
        elif angle_units == "rad":
            self.alpha = alpha
            self.beta  = beta
            self.gamma = gamma

        self.space_group  = SpaceGroups.GetSpaceGroup(space_group)
        self.orth_to_frac = self.calc_fractionalization_matrix()
        self.frac_to_orth = self.calc_orthogonalization_matrix()

        ## check our math!
        assert numpy.allclose(self.orth_to_frac, linalg.inverse(self.frac_to_orth))

    def __str__(self):
        alpha = math.degrees(self.alpha)
        beta  = math.degrees(self.beta)
        gamma = math.degrees(self.gamma)

        return "UnitCell(a=%f, b=%f, c=%f, alpha=%f, beta=%f, gamma=%f)" % (
            self.a, self.b, self.c, alpha, beta, gamma)

    def calc_alpha_deg(self):
        """Returns the alpha angle in degrees.
        """
        return math.degrees(self.alpha)
    
    def calc_beta_deg(self):
        """Returns the beta angle in degrees.
        """
        return math.degrees(self.beta)

    def calc_gamma_deg(self):
        """Returns the gamma angle in degrees.
        """
        return math.degrees(self.gamma)

    def calc_v(self):
        """Calculates the volume of the rhombohedrial created by the
        unit vectors a1/|a1|, a2/|a2|, a3/|a3|.
        """
        cos_alpha = math.cos(self.alpha)
        cos_beta  = math.cos(self.beta)
        cos_gamma = math.cos(self.gamma)
        return math.sqrt(1                       -
                         (cos_alpha * cos_alpha) -
                         (cos_beta  * cos_beta)  -
                         (cos_gamma * cos_gamma) +
                         (2 * cos_alpha * cos_beta * cos_gamma) )

    def calc_volume(self):
        """Calculates the volume of the unit cell.
        """
        return self.a * self.b * self.c * self.calc_v()

    def calc_reciprocal_unit_cell(self):
        """Corresponding reciprocal unit cell.
        """
        V = self.calc_volume()

        sin_alpha = math.sin(self.alpha)
        sin_beta  = math.sin(self.beta)
        sin_gamma = math.sin(self.gamma)

        cos_alpha = math.cos(self.alpha)
        cos_beta  = math.cos(self.beta)
        cos_gamma = math.cos(self.gamma)

        ra  = (self.b * self.c * sin_alpha) / V
        rb  = (self.a * self.c * sin_beta)  / V
        rc  = (self.a * self.b * sin_gamma) / V

        ralpha = math.acos(
            (cos_beta  * cos_gamma - cos_alpha) / (sin_beta  * sin_gamma))
        rbeta  = math.acos(
            (cos_alpha * cos_gamma - cos_beta)  / (sin_alpha * sin_gamma))
        rgamma = math.acos(
            (cos_alpha * cos_beta  - cos_gamma) / (sin_alpha * sin_beta))

        return UnitCell(ra, rb, rc, ralpha, rbeta, rgamma)

    def calc_orthogonalization_matrix(self):
        """Cartesian to fractional coordinates.
        """
        sin_alpha = math.sin(self.alpha)
        sin_beta  = math.sin(self.beta)
        sin_gamma = math.sin(self.gamma)

        cos_alpha = math.cos(self.alpha)
        cos_beta  = math.cos(self.beta)
        cos_gamma = math.cos(self.gamma)

        v = self.calc_v()

        f11 = self.a
        f12 = self.b * cos_gamma
        f13 = self.c * cos_beta
        f22 = self.b * sin_gamma
        f23 = (self.c * (cos_alpha - cos_beta * cos_gamma)) / (sin_gamma)
        f33 = (self.c * v) / sin_gamma

        orth_to_frac = numpy.array([ [f11, f12, f13],
                                     [0.0, f22, f23],
                                     [0.0, 0.0, f33] ], float)
        
        return orth_to_frac
        
    def calc_fractionalization_matrix(self):
        """Fractional to cartesian coordinates.
        """
        sin_alpha = math.sin(self.alpha)
        sin_beta  = math.sin(self.beta)
        sin_gamma = math.sin(self.gamma)

        cos_alpha = math.cos(self.alpha)
        cos_beta  = math.cos(self.beta)
        cos_gamma = math.cos(self.gamma)

        v = self.calc_v()

        o11 = 1.0 / self.a
        o12 = - cos_gamma / (self.a * sin_gamma)
        o13 = (cos_gamma * cos_alpha - cos_beta) / (self.a * v * sin_gamma)
        o22 = 1.0 / (self.b * sin_gamma)
        o23 = (cos_gamma * cos_beta - cos_alpha) / (self.b * v * sin_gamma)
        o33 = sin_gamma / (self.c * v)

        frac_to_orth = numpy.array([ [o11, o12, o13],
                                     [0.0, o22, o23],
                                     [0.0, 0.0, o33] ], float)

        return frac_to_orth

    def calc_orth_to_frac(self, v):
        """Calculates and returns the fractional coordinate vector of
        orthogonal vector v.
        """
        return numpy.matrixmultiply(self.orth_to_frac, v)

    def calc_frac_to_orth(self, v):
        """Calculates and returns the orthogonal coordinate vector of
        fractional vector v.
        """
        return numpy.matrixmultiply(self.frac_to_orth, v)

    def calc_orth_symop(self, symop):
        """Calculates the orthogonal space symmetry operation (return SymOp)
        given a fractional space symmetry operation (argument SymOp).
        """
        RF  = numpy.matrixmultiply(symop.R, self.orth_to_frac)
        ORF = numpy.matrixmultiply(self.frac_to_orth, RF)
        Ot  = numpy.matrixmultiply(self.frac_to_orth, symop.t)
        return SpaceGroups.SymOp(ORF, Ot)

    def calc_orth_symop2(self, symop):
        """Calculates the orthogonal space symmetry operation (return SymOp)
        given a fractional space symmetry operation (argument SymOp).
        """
        RF  = numpy.matrixmultiply(symop.R, self.orth_to_frac)
        ORF = numpy.matrixmultiply(self.frac_to_orth, RF)
        Rt  = numpy.matrixmultiply(symop.R, symop.t)
        ORt = numpy.matrixmultiply(self.frac_to_orth, Rt)
        
        return SpaceGroups.SymOp(ORF, ORt)

    def calc_cell(self, xyz):
        """Returns the cell integer 3-Tuple where the xyz fractional
        coordinates are located.
        """
        if xyz[0]<0.0:
            cx = int(xyz[0] - 1.0)
        else:
            cx = int(xyz[0] + 1.0)
            
        if xyz[1]<0.0:
            cy = int(xyz[1] - 1.0)
        else:
            cy = int(xyz[1] + 1.0)

        if xyz[2]<0.0:
            cz = int(xyz[2] - 1.0)
        else:
            cz = int(xyz[2] + 1.0)
            
        return (cx, cy, cz)

    def cell_search_iter(self):
        """Yields 3-tuple integer translations over a 3x3x3 cube used by
        other methods for searching nearby unit cells.
        """
        cube = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)
        
        for i in cube:
            for j in cube:
                for k in cube:
                    yield i, j, k

    def iter_struct_orth_symops(self, struct):
        """Iterate over the orthogonal-space symmetry operations which will
        place a symmetry related structure near the argument struct.
        """
        ## compute the centroid of the structure
        n = 0
        cent = numpy.zeros(3, float)
        for atm in struct.iter_all_atoms():
            n    += 1
            cent += atm.position
        centroid = cent / n

        ccell = self.calc_cell(self.calc_orth_to_frac(centroid))
        centroid_cell = numpy.array(ccell, float)

        ## compute the distance from the centroid to the
        ## farthest point from it in the structure
        max_dist = 0.0
        for frag in struct.iter_amino_acids():
            for atm in frag.iter_atoms():
                dist = AtomMath.length(atm.position - centroid)
                max_dist = max(max_dist, dist)
        max_dist2 = 2.0 * max_dist + 5.0

        for symop in self.space_group.iter_symops():
            for i, j, k in self.cell_search_iter():

                 cell_t  = numpy.array([i, j, k], float)
                 symop_t = SpaceGroups.SymOp(symop.R, symop.t+cell_t)

                 xyz       = self.calc_orth_to_frac(centroid)
                 xyz_symm  = symop_t(xyz)
                 centroid2 = self.calc_frac_to_orth(xyz_symm)
                 
                 if AtomMath.length(centroid - centroid2)<=max_dist2:
                     yield self.calc_orth_symop(symop_t)


def strRT(R, T):
    """Returns a string for a rotation/translation pair in a readable form.
    """
    x  = "[%6.3f %6.3f %6.3f %6.3f]\n" % (
        R[0,0], R[0,1], R[0,2], T[0])
    x += "[%6.3f %6.3f %6.3f %6.3f]\n" % (
        R[1,0], R[1,1], R[1,2], T[1])
    x += "[%6.3f %6.3f %6.3f %6.3f]\n" % (
        R[2,0], R[2,1], R[2,2], T[2])
    
    return x


## <testing>
def test_module():
    print "================================================="
    print "TEST CASE #1: Triclinic unit cell"
    print

    uc = UnitCell(7.877, 7.210, 7.891, 105.563, 116.245, 79.836)

    e = numpy.array([[1.0, 0.0, 0.0],
                     [0.0, 1.0, 0.0],
                     [0.0, 0.0, 1.0]], float)


    print uc
    print "volume                   = ",uc.calc_v()
    print "cell volume              = ",uc.calc_volume()
    print "fractionalization matrix =\n",uc.calc_fractionalization_matrix()
    print "orthogonalization matrix =\n",uc.calc_orthogonalization_matrix()

    print "orth * e =\n", numpy.matrixmultiply(
        uc.calc_orthogonalization_matrix(), e)


    print "calc_frac_to_orth"
    vlist = [
        numpy.array([0.0, 0.0, 0.0]),
        numpy.array([0.5, 0.5, 0.5]),
        numpy.array([1.0, 1.0, 1.0]),
        numpy.array([-0.13614, 0.15714, -0.07165]) ]
    
    for v in vlist:
        ov = uc.calc_frac_to_orth(v)
        v2 = uc.calc_orth_to_frac(ov)
        print "----"
        print "    ",v
        print "    ",ov
        print "    ",v2
        print "----"


    print "================================================="

    print
    
    print "================================================="
    print "TEST CASE #2: Reciprocal of above unit cell "
    print

    ruc = uc.calc_reciprocal_unit_cell()
    print ruc
    print "volume      = ",ruc.calc_v()
    print "cell volume = ",ruc.calc_volume()
    
    print "================================================="

    print

    print "================================================="
    print "TEST CASE #3: Orthogonal space symmetry operations"

    unitx = UnitCell(a           = 64.950,
                     b           = 64.950,
                     c           = 68.670,
                     alpha       = 90.00,
                     beta        = 90.00,
                     gamma       = 120.00,
                     space_group = "P 32 2 1")
    print unitx
    print

    for symop in unitx.space_group.iter_symops():
        print "Fractional Space SymOp:"
        print symop
        print "Orthogonal Space SymOp:"
        print unitx.calc_orth_symop(symop)
        print

if __name__=="__main__":
    test_module()
## </testing>
