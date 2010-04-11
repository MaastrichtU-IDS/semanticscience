## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Mathmatical operations performed on mmLib.Strcuture.Atom objects.
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

import Constants


##
## Linear Algebra
##
def length(u):
    """Calculates the length of u.
    """
    return math.sqrt(numpy.dot(u, u))

def normalize(u):
    """Returns the normalized vector along u.
    """
    return u/math.sqrt(numpy.dot(u, u))

def cross(u, v):
    """Cross product of u and v:
    Cross[u,v] = {-u3 v2 + u2 v3, u3 v1 - u1 v3, -u2 v1 + u1 v2}
    """
    return numpy.array([ u[1]*v[2] - u[2]*v[1],
                         u[2]*v[0] - u[0]*v[2],
                         u[0]*v[1] - u[1]*v[0] ], float)


##
## Rotation/Displacement
##
def rmatrix(alpha, beta, gamma):
    """Return a rotation matrix based on the Euler angles alpha,
    beta, and gamma in radians.
    """
    cosA = math.cos(alpha)
    cosB = math.cos(beta)
    cosG = math.cos(gamma)

    sinA = math.sin(alpha)
    sinB = math.sin(beta)
    sinG = math.sin(gamma)
    
    R = numpy.array(
        [[cosB*cosG, cosG*sinA*sinB-cosA*sinG, cosA*cosG*sinB+sinA*sinG],
         [cosB*sinG, cosA*cosG+sinA*sinB*sinG, cosA*sinB*sinG-cosG*sinA ],
         [-sinB,     cosB*sinA,                cosA*cosB ]], float)

    assert numpy.allclose(linalg.determinant(R), 1.0)
    return R

def rmatrixu(u, theta):
    """Return a rotation matrix caused by a right hand rotation of theta
    radians around vector u.
    """
    if numpy.allclose(theta, 0.0) or numpy.allclose(numpy.dot(u,u), 0.0):
        return numpy.identity(3, float)

    x, y, z = normalize(u)
    sa = math.sin(theta)
    ca = math.cos(theta)

    R = numpy.array(
        [[1.0+(1.0-ca)*(x*x-1.0), -z*sa+(1.0-ca)*x*y,     y*sa+(1.0-ca)*x*z],
         [z*sa+(1.0-ca)*x*y,      1.0+(1.0-ca)*(y*y-1.0), -x*sa+(1.0-ca)*y*z],
         [-y*sa+(1.0-ca)*x*z,     x*sa+(1.0-ca)*y*z,      1.0+(1.0-ca)*(z*z-1.0)]], float)

    try:
        assert numpy.allclose(linalg.determinant(R), 1.0)
    except AssertionError:
        print "rmatrixu(%s, %f) determinant(R)=%f" % (
            u, theta, linalg.determinant(R))
        raise
    
    return R


def dmatrix(alpha, beta, gamma):
    """Returns the displacement matrix based on rotation about Euler
    angles alpha, beta, and gamma.
    """
    return rmatrix(alpha, beta, gamma) - numpy.identity(3, float)

def dmatrixu(u, theta):
    """Return a displacement matrix caused by a right hand rotation of theta
    radians around vector u.
    """
    return rmatrixu(u, theta) - numpy.identity(3, float)

def rmatrixz(vec):
    """Return a rotation matrix which transforms the coordinate system
    such that the vector vec is aligned along the z axis.
    """
    u, v, w = normalize(vec)

    d = math.sqrt(u*u + v*v)

    if d != 0.0:
        Rxz = numpy.array([ [  u/d, v/d,  0.0 ],
                            [ -v/d, u/d,  0.0 ],
                            [  0.0, 0.0,  1.0 ] ], float)
    else:
        Rxz = numpy.identity(3, float)


    Rxz2z = numpy.array([ [   w, 0.0,    -d],
                          [ 0.0, 1.0,   0.0],
                          [   d, 0.0,     w] ], float)

    R = numpy.matrixmultiply(Rxz2z, Rxz)

    try:
        assert numpy.allclose(linalg.determinant(R), 1.0)
    except AssertionError:
        print "rmatrixz(%s) determinant(R)=%f" % (vec, linalg.determinant(R))
        raise

    return R

##
## Quaternions
##
def rquaternionu(u, theta):
    """Returns a quaternion representing the right handed rotation of theta
    radians about vector u.Quaternions are typed as Numeric Python numpy.arrays of
    length 4.
    """
    u = normalize(u)

    half_sin_theta = math.sin(theta / 2.0)

    x = u[0] * half_sin_theta
    y = u[1] * half_sin_theta
    z = u[2] * half_sin_theta
    w = math.cos(theta / 2.0)

    ## create quaternion
    q = numpy.array((x, y, z, w), float)
    assert numpy.allclose(math.sqrt(numpy.dot(q,q)), 1.0)

    return q

def addquaternion(q1, q2):
    """Adds quaterions q1 and q2. Quaternions are typed as Numeric
    Python numpy.arrays of length 4.
    """
    assert numpy.allclose(math.sqrt(numpy.dot(q1,q1)), 1.0)
    assert numpy.allclose(math.sqrt(numpy.dot(q2,q2)), 1.0)
    
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2

    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 + y1*w2 + z1*x2 - x1*z2
    z = w1*z2 + z1*w2 + x1*y2 - y1*x2
    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    q = numpy.array((x, y, z, w), float)
    
    ## normalize quaternion
    q = q / math.sqrt(numpy.dot(q,q))
    assert numpy.allclose(math.sqrt(numpy.dot(q,q)), 1.0)
    
    return q

def rmatrixquaternion(q):
    """Create a rotation matrix from q quaternion rotation.
    Quaternions are typed as Numeric Python numpy.arrays of length 4.
    """
    assert numpy.allclose(math.sqrt(numpy.dot(q,q)), 1.0)
    
    x, y, z, w = q

    xx = x*x
    xy = x*y
    xz = x*z
    xw = x*w
    yy = y*y
    yz = y*z
    yw = y*w
    zz = z*z
    zw = z*w

    r00 = 1.0 - 2.0 * (yy + zz)
    r01 =       2.0 * (xy - zw)
    r02 =       2.0 * (xz + yw)

    r10 =       2.0 * (xy + zw)
    r11 = 1.0 - 2.0 * (xx + zz) 
    r12 =       2.0 * (yz - xw)

    r20 =       2.0 * (xz - yw)
    r21 =       2.0 * (yz + xw)
    r22 = 1.0 - 2.0 * (xx + yy)

    R = numpy.array([[r00, r01, r02],
               [r10, r11, r12],
               [r20, r21, r22]], float)
    
    assert numpy.allclose(linalg.determinant(R), 1.0)
    return R

def quaternionrmatrix(R):
    """Return a quaternion calculated from the argument rotation matrix R.
    """
    assert numpy.allclose(linalg.determinant(R), 1.0)

    t = numpy.trace(R) + 1.0

    if t>1e-5:
        w = math.sqrt(1.0 + numpy.trace(R)) / 2.0
        w4 = 4.0 * w

        x = (R[2,1] - R[1,2]) / w4
        y = (R[0,2] - R[2,0]) / w4
        z = (R[1,0] - R[0,1]) / w4
        
    else:
        if R[0,0]>R[1,1] and R[0,0]>R[2,2]: 
            S = math.sqrt(1.0 + R[0,0] - R[1,1] - R[2,2]) * 2.0
            x = 0.25 * S
            y = (R[0,1] + R[1,0]) / S 
            z = (R[0,2] + R[2,0]) / S 
            w = (R[1,2] - R[2,1]) / S
        elif R[1,1]>R[2,2]: 
            S = math.sqrt(1.0 + R[1,1] - R[0,0] - R[2,2]) * 2.0; 
            x = (R[0,1] + R[1,0]) / S; 
            y = 0.25 * S;
            z = (R[1,2] + R[2,1]) / S; 
            w = (R[0,2] - R[2,0]) / S;
        else:
            S = math.sqrt(1.0 + R[2,2] - R[0,0] - R[1,1]) * 2; 
            x = (R[0,2] + R[2,0]) / S; 
            y = (R[1,2] + R[2,1]) / S; 
            z = 0.25 * S;
            w = (R[0,1] - R[1,0] ) / S;

    q = numpy.array((x, y, z, w), float)
    assert numpy.allclose(math.sqrt(numpy.dot(q,q)), 1.0)    
    return q


##
## Bond Angles
##
def calc_distance(a1, a2):
    """Returns the distance between two argument atoms.
    """
    if a1 == None or a2 == None:
        return None
    return length(a1.position - a2.position)

def calc_angle(a1, a2, a3):
    """Return the angle between the three argument atoms.
    """
    if a1 == None or a2 == None or a3 == None:
        return None
    a21 = a1.position - a2.position
    a21 = a21 / (length(a21))

    a23 = a3.position - a2.position
    a23 = a23 / (length(a23))

    return math.acos(numpy.dot(a21, a23))

def calc_torsion_angle(a1, a2, a3, a4):
    """Calculates the torsion angle between the four argument atoms.
    """
    if a1 == None or a2 == None or a3 == None or a4 == None:
        return None

    a12 = a2.position - a1.position
    a23 = a3.position - a2.position
    a34 = a4.position - a3.position

    n12 = cross(a12, a23)
    n34 = cross(a23, a34)

    n12 = n12 / length(n12)
    n34 = n34 / length(n34)

    cross_n12_n34  = cross(n12, n34)
    direction      = cross_n12_n34 * a23
    scalar_product = numpy.dot(n12, n34)

    if scalar_product > 1.0:
        scalar_product = 1.0
    if scalar_product < -1.0:
        scalar_product = -1.0

    angle = math.acos(scalar_product)

#    if direction<0.0:
#        angle = -angle

    return angle


##
## Atomic ADPs
##
def calc_CCuij(U, V):
    """Calculate the cooralation coefficent for anisotropic ADP tensors U
    and V.
    """
    invU = linalg.inverse(U)
    invV = linalg.inverse(V)
    
    det_invU = linalg.determinant(invU)
    det_invV = linalg.determinant(invV)

    return ( math.sqrt(math.sqrt(det_invU * det_invV)) /
             math.sqrt((1.0/8.0) * linalg.determinant(invU + invV)) )

def calc_Suij(U, V):
    """Calculate the similarity of anisotropic ADP tensors U and V.
    """
    eqU = numpy.trace(U) / 3.0
    eqV = numpy.trace(V) / 3.0

    isoU = eqU * numpy.identity(3, float)
    isoV = eqV * numpy.identity(3, float)

    return ( calc_CCuij(U, (eqU/eqV)*V) /
             (calc_CCuij(U, isoU) * calc_CCuij(V, isoV)) )

def calc_DP2uij(U, V):
    """Calculate the square of the volumetric difference in the probability
    density function of anisotropic ADP tensors U and V.
    """
    invU = linalg.inverse(U)
    invV = linalg.inverse(V)

    det_invU = linalg.determinant(invU)
    det_invV = linalg.determinant(invV)

    Pu2 = math.sqrt( det_invU / (64.0 * Constants.PI3) )
    Pv2 = math.sqrt( det_invV / (64.0 * Constants.PI3) )
    Puv = math.sqrt(
        (det_invU * det_invV) / (8.0*Constants.PI3 * linalg.determinant(invU + invV)))

    dP2 = Pu2 + Pv2 - (2.0 * Puv)
    
    return dP2

def calc_anisotropy(U):
    """Calculates the anisotropy of a atomic ADP tensor U.  Anisotropy is
    defined as the smallest eigenvalue of U divided by the largest eigenvalue
    of U.
    """
    evals = linalg.eigenvalues(U)
    return min(evals) / max(evals)

##
## Calculations on groups of atoms
##
def calc_atom_centroid(atom_iter):
    """Calculates the centroid of all contained Atom instances and
    returns a Vector to the centroid.
    """
    num      = 0
    centroid = numpy.zeros(3, float)
    for atm in atom_iter:
        if atm.position != None:
            centroid += atm.position
            num += 1
    
    return centroid / num

def calc_atom_mean_temp_factor(atom_iter):
    """Calculates the adverage temperature factor of all contained
    Atom instances and returns the adverage temperature factor.
    """
    num_tf = 0
    adv_tf = 0.0

    for atm in atom_iter:
        if atm.temp_factor != None:
            adv_tf += atm.temp_factor
            num_tf += 1

    return adv_tf / num_tf


def calc_inertia_tensor(atom_iter, origin):
    """Calculate a moment-of-intertia tensor at the given origin assuming all
    atoms have the same mass.
    """
    I = numpy.zeros((3,3), float)
    
    for atm in atom_iter:
        x = atm.position - origin

        I[0,0] += x[1]**2 + x[2]**2
        I[1,1] += x[0]**2 + x[2]**2
        I[2,2] += x[0]**2 + x[1]**2

        I[0,1] += - x[0]*x[1]
        I[1,0] += - x[0]*x[1]

        I[0,2] += - x[0]*x[2]
        I[2,0] += - x[0]*x[2]

        I[1,2] += - x[1]*x[2]
        I[2,1] += - x[1]*x[2]

    evals, evecs = linalg.eigenvectors(I)

    ## order the tensor such that the largest
    ## principal compent is along the z-axis, and
    ## the second largest is along the y-axis
    if evals[0] >= evals[1] and evals[0] >= evals[2]:
        if evals[1] >= evals[2]:
            R = numpy.array((evecs[2], evecs[1], evecs[0]), float)
        else:
            R = numpy.array((evecs[1], evecs[2], evecs[0]), float)

    elif evals[1] >= evals[0] and evals[1] >= evals[2]:
        if evals[0] >= evals[2]:
            R = numpy.array((evecs[2], evecs[0], evecs[1]), float)
        else:
            R = numpy.array((evecs[0], evecs[2], evecs[1]), float)

    elif evals[2] >= evals[0] and evals[2] >= evals[1]:
        if evals[0] >= evals[1]:
            R = numpy.array((evecs[1], evecs[0], evecs[2]), float)
        else:
            R = numpy.array((evecs[0], evecs[1], evecs[2]), float)

    ## make sure the tensor is right-handed
    if numpy.allclose(linalg.determinant(R), -1.0):
        I = numpy.identity(3, float)
        I[0,0] = -1.0
        R = numpy.matrixmultiply(I, R)

    assert numpy.allclose(linalg.determinant(R), 1.0)
    return R


### <TESTING>
def test_module():
    import Structure

    a1 = Structure.Atom(x=0.0, y=-1.0, z=0.0)
    a2 = Structure.Atom(x=0.0, y=0.0,  z=0.0)
    a3 = Structure.Atom(x=1.0, y=0.0,  z=0.0)
    a4 = Structure.Atom(x=1.0, y=1.0,  z=-1.0)

    print "a1:",a1.position
    print "calc_angle:",calc_angle(a1, a2, a3)
    print "calc_torsion_angle:",calc_torsion_angle(a1, a2, a3, a4)

if __name__ == "__main__":
    test_module()
### </TESTING>

