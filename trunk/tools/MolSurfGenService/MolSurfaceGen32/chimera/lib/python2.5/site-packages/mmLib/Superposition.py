## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Class for least-squares structural superposition.  Uses a quaternion
method which avoids improper rotations.
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

def QuaternionToRotationMatrix(q):
    """Create a rotation matrix from q quaternion rotation.
    Quaternions are typed as Numeric Python arrays of length 4.
    """
    assert numpy.allclose(math.sqrt(numpy.dot(q,q)), 1.0)
    
    q0, q1, q2, q3 = q

    b0 = 2.0*q0
    b1 = 2.0*q1
    b2 = 2.0*q2
    b3 = 2.0*q3
    
    q00 = b0*q0-1.0
    q01 = b0*q1
    q02 = b0*q2
    q03 = b0*q3
    
    q11 = b1*q1
    q12 = b1*q2
    q13 = b1*q3  
    
    q22 = b2*q2
    q23 = b2*q3
    
    q33 = b3*q3 

    return numpy.array([ [q00+q11, q12-q03, q13+q02],
                         [q12+q03, q00+q22, q23-q01],
                         [q13-q02, q23+q01, q00+q33] ], float)


class SuperpositionResults(object):
    """Returns the results of a superposition.
    """
    def __init__(self, quaternion, source_origin, destination_origin, rmsd, num_atoms):
        self.Q = quaternion
        self.R = QuaternionToRotationMatrix(quaternion)
        self.src_origin = source_origin
        self.dst_origin = destination_origin
        self.rmsd = rmsd
        self.num_atoms = num_atoms

    def transform(self, position):
        """Transforms a source position to its aligned position.
        """
        position = position - self.src_origin
        position = numpy.matrixmultiply(self.R, position)
        position = position + self.dst_origin
        return position


def SuperimposePoints(src_points, dst_points):
    """Takes two 1:1 set of points and returns a 3x3 rotation matrix and
    translation vector.
    """
    num_points = src_points.shape[0]

    ## shift both sets of coordinates to their centroids
    src_org = numpy.add.reduce(src_points) / float(src_points.shape[0])
    dst_org = numpy.add.reduce(dst_points) / float(dst_points.shape[0])

    X = numpy.add(src_points, -src_org)
    Y = numpy.add(dst_points, -dst_org)

    xy2n = 0.0

    R = numpy.zeros((3,3), float)

    for k in xrange(num_points):
        x = X[k]
        y = Y[k]

        xy2n += numpy.add.reduce(x*x) + numpy.add.reduce(y*y)

        R[0,0] += x[0]*y[0]
        R[0,1] += x[0]*y[1]
        R[0,2] += x[0]*y[2]
        
        R[1,0] += x[1]*y[0]
        R[1,1] += x[1]*y[1]
        R[1,2] += x[1]*y[2]
        
        R[2,0] += x[2]*y[0]
        R[2,1] += x[2]*y[1]
        R[2,2] += x[2]*y[2]

    F = numpy.zeros((4,4), float)
    F[0,0] = R[0,0] + R[1,1] + R[2,2]
    F[0,1] = R[1,2] - R[2,1]
    F[0,2] = R[2,0] - R[0,2]
    F[0,3] = R[0,1] - R[1,0]

    F[1,0] = F[0,1]
    F[1,1] = R[0,0] - R[1,1] - R[2,2]
    F[1,2] = R[0,1] + R[1,0]
    F[1,3] = R[0,2] + R[2,0]

    F[2,0] = F[0,2]
    F[2,1] = F[1,2]
    F[2,2] =-R[0,0] + R[1,1] - R[2,2]
    F[2,3] = R[1,2] + R[2,1]

    F[3,0] = F[0,3]
    F[3,1] = F[1,3]
    F[3,2] = F[2,3]
    F[3,3] =-R[0,0] - R[1,1] + R[2,2]

    evals, evecs = linalg.eigenvectors(F)

    i = numpy.argmax(evals)
    eval = evals[i]
    evec = evecs[i]
    
    msd = (xy2n - 2.0*eval) / num_points
    if msd < 0.0:
        rmsd = 0.0
    else:
        rmsd = math.sqrt(msd)

    return SuperpositionResults(evec, src_org, dst_org, rmsd, num_points)


def SuperimposePositions(position_tuple_list):
    """Superimposes a list of 2-tuple atom pairs.
    """
    n = len(position_tuple_list)
    a1 = numpy.zeros((n,3), float)
    a2 = numpy.zeros((n,3), float)
    
    for i in xrange(n):
        pos1, pos2 = position_tuple_list[i]

        a1[i] = pos1
        a2[i] = pos2
    
    return SuperimposePoints(a1, a2)


def SuperimposeAtoms(atom_pair_list):
    """Superimposes a list of 2-tuple atom pairs.
    """
    n = len(atom_pair_list)
    a1 = numpy.zeros((n,3), float)
    a2 = numpy.zeros((n,3), float)
    
    for i in xrange(n):
        atm1, atm2 = atom_pair_list[i]

        a1[i] = atm1.position
        a2[i] = atm2.position
    
    return SuperimposePoints(a1, a2)


def SuperimposeAtomsOutlierRejection(alist, rmsd_cutoff = 1.0, max_cycles = 100):
    """Superimpose two homologus protein chains. The argument alist is a list of
    2-tuples.  The 2-tuples are the 1:1 atoms to superimpose.  The alignment
    procedure incrementally omits atoms with large deviations until the rmsd of
    the least squares superposition is less than or equal to rmsd_cutoff, or the
    number of cycles exceeds max_cycles.
    """
    for cycle in xrange(max_cycles):
        sresult = SuperimposeAtoms(alist)
        print "Cycle %d NA: %5d RMSD %6.2f" % (cycle, sresult.num_atoms, sresult.rmsd)
        if sresult.rmsd <= rmsd_cutoff:
            return sresult

        deviation = []
        for i in xrange(len(alist)):
            satm, datm = alist[i]            
            spos = sresult.transform(satm.position)
            deviation.append((AtomMath.length(spos - datm.position), i))
        deviation.sort()

        outliers = deviation[-10:]
        outliersr = [(x[1], x[0]) for x in outliers]
        outliersr.sort()
        outliersr.reverse()
        
        for i, d in outliersr:
            if d < rmsd_cutoff: continue
            del alist[i]

    return None
        
## <testing>
def test_module():
    import random
    import AtomMath
    import FileIO
    import Structure
    
    R = AtomMath.rmatrixu(numpy.array((0.0, 0.0, 1.0), float), math.pi/2.0)

    struct1 = FileIO.LoadStructure(fil="/home/jpaint/8rxn/8rxn.pdb")
    struct2 = FileIO.LoadStructure(fil="/home/jpaint/8rxn/8rxn.pdb")

    chn1 = struct1.get_chain("A")
    chn2 = struct2.get_chain("A")

    rc = lambda: 0.1 * (random.random() - 1.0)
    for atm in chn2.iter_atoms():
        atm.position = numpy.matrixmultiply(R, atm.position) + numpy.array((rc(),rc(),rc()),float)
        
    alist = []
 
    for atm1 in chn1.iter_atoms():
        if atm1.name != "CA":
            continue

        atm2 = chn2.get_equivalent_atom(atm1)
        if atm2 == None: continue

        alist.append((atm1, atm2))

    sup = SuperimposeAtoms(alist)

    R = sup.R
    Q = sup.Q
    print Q
    print R
    
    so = sup.src_origin
    do = sup.dst_origin
    
    sup1 = Structure.Structure(structure_id = "JMP1")
    for atm in chn1.iter_atoms():
        atm.position = numpy.matrixmultiply(R, atm.position - so)
        sup1.add_atom(atm)
    FileIO.SaveStructure(fil="super1.pdb", struct=sup1)

    sup2 = Structure.Structure(structure_id = "JMP2")
    for atm in chn2.iter_atoms():
        atm.position = atm.position - do
        sup2.add_atom(atm)
    FileIO.SaveStructure(fil="super2.pdb", struct=sup2)

if __name__ == "__main__":
    test_module()
## </testing>
