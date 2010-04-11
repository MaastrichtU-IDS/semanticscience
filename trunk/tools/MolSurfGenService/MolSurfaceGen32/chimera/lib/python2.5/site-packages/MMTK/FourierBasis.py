# Fourier basis for low-frequency normal mode calculations.
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

"""This module provides a basis that is suitable for the
calculation of low-frequency normal modes. The basis is
derived from vector fields whose components are stationary
waves in a box surrounding the system. For a description
see [Article:Hinsen1998].
"""

import ParticleProperties
from Scientific.Geometry import Vector
from Scientific import N as Numeric

class FourierBasis:

    """Collective-motion basis for low-frequency normal mode calculations

    To be used with Class:MMTK.NormalModes.SubspaceNormalModes.

    Constructor: FourierBasis(|universe|, |cutoff|)

    Arguments:

    |universe| -- the universe for which the basis will be used

    |cutoff| -- the wavelength cutoff. A smaller value means a larger basis.

    A FourierBasis object behaves like a sequence of
    Class:MMTK.ParticleVector objects. The vectors are *not*
    orthonormal, because orthonormalization is handled automatically
    by the class Class:MMTK.NormalModes.SubspaceNormalModes.
    """

    def __init__(self, universe, cutoff):
        p1, p2 = universe.boundingBox()
        p2 = p2 + Vector(cutoff, cutoff, cutoff)
        l = (p2-p1).array
        n_max = (0.5*l/cutoff+0.5).astype(Numeric.Int)

        wave_numbers = []
        for nx in range(-n_max[0], n_max[0]+1):
            for ny in range(-n_max[1], n_max[1]+1):
                for nz in range(-n_max[2], n_max[2]+1):
                    if (nx/l[0])**2 + (ny/l[1])**2 + (nz/l[2])**2 \
                                    < 0.25/cutoff**2:
                        wave_numbers.append((nx, ny, nz))

        atoms = universe.atomList()
        natoms = len(atoms)
        basis = Numeric.zeros((3*len(wave_numbers)+3, natoms, 3),
                              Numeric.Float)
        cm = universe.centerOfMass()
        i = 0
        for rotation in [Vector(1.,0.,0.), Vector(0.,1.,0.),
                         Vector(0.,0.,1.)]:
            v = ParticleProperties.ParticleVector(universe, basis[i])
            for a in atoms:
                v[a] = rotation.cross(a.position()-cm)
            i = i + 1
        conf = universe.configuration().array-p1.array
        for n in wave_numbers:
            k = 2.*Numeric.pi*Numeric.array(n)/l
            w = self._w(conf[:, 0], k[0]) * self._w(conf[:, 1], k[1]) * \
                self._w(conf[:, 2], k[2])
            basis[i, :, 0] = w
            basis[i+1, :, 1] = w
            basis[i+2, :, 2] = w
            i = i + 3

        self.array = basis
        self.universe = universe

    __safe_for_unpickling__ = 1
    __had_initargs__ = 1

    def _w(self, x, k):
        if k < 0:
            return Numeric.sin(-k*x)
        else:
            return Numeric.cos(k*x)

    def __len__(self):
        return self.array.shape[0]

    def __getitem__(self, item):
        return ParticleProperties.ParticleVector(self.universe,
                                                 self.array[item])


# Estimate number of basis vectors for a given cutoff

def countBasisVectors(universe, cutoff):
    """Returns the number of basis vectors in a FourierBasis for
    the given |universe| and |cutoff|."""
    p1, p2 = universe.boundingBox()
    p2 = p2 + Vector(cutoff, cutoff, cutoff)
    l = (p2-p1).array
    n_max = (0.5*l/cutoff+0.5).astype(Numeric.Int)
    wave_numbers = []
    for nx in range(-n_max[0], n_max[0]+1):
        for ny in range(-n_max[1], n_max[1]+1):
            for nz in range(-n_max[2], n_max[2]+1):
                if (nx/l[0])**2 + (ny/l[1])**2 + (nz/l[2])**2 < 0.25/cutoff**2:
                    wave_numbers.append((nx, ny, nz))
    return 3*len(wave_numbers)+3


# Estimate cutoff for a given number of basis vectors

def estimateCutoff(universe, nmodes):
    """Returns an estimate for the cutoff that will yield a basis of
    |nmodes| vectors for the given |universe|. The two return values
    are the cutoff and the precise number of basis vectors for this cutoff."""
    natoms = universe.numberOfCartesianCoordinates()
    if nmodes > natoms:
        nmodes = 3*natoms
        cutoff = None
    else:
        p1, p2 = universe.boundingBox()
        cutoff_max = (p2-p1).length()
        cutoff = 0.5*cutoff_max
        nmodes_opt = nmodes
        nmodes = countBasisVectors(universe, cutoff)
        while nmodes > nmodes_opt:
            cutoff = cutoff + 0.1
            if cutoff > cutoff_max:
                cutoff = cutoff_max
                break
            nmodes = countBasisVectors(universe, cutoff)
        while nmodes < nmodes_opt:
            cutoff = cutoff - 0.1
            if cutoff < 0.1:
                cutoff = 0.1
                break
            nmodes = countBasisVectors(universe, cutoff)
    return cutoff, nmodes
