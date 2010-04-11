# Energetic normal mode calculations.
#
# Written by Konrad Hinsen
# last revision: 2007-4-26
#

"""See also the Example:NormalModes example applications.
"""

from MMTK import Features, Units, ParticleProperties
from MMTK.NormalModes import Core
from Scientific import N

#
# Class for a single mode
#
class EnergeticMode(Core.Mode):

    """Single energetic normal mode

    A Glossary:Subclass of Class:MMTK.ParticleVector.

    Mode objects are created by indexing a EnergeticNormalModes object.
    They contain the atomic displacements corresponding to a
    single mode.

    Mode objects are specializations of Class:MMTK.ParticleVector
    objects and support all their operations. In addition, the
    frequency corresponding to the mode is stored in the attribute
    "frequency".
    """

    def __init__(self, universe, n, force_constant, mode):
        self.force_constant = force_constant
        Core.Mode.__init__(self, universe, n, mode)

    def __str__(self):
        return 'Mode ' + `self.number` + ' with force constant ' + \
               `self.force_constant`

    __repr__ = __str__

#
# Class for a full set of normal modes
#
class EnergeticModes(Core.NormalModes):

    """Energetic normal modes

    Constructor: EnergeticModes(|universe|, |temperature|=300,
                                |subspace|=None, |delta|=None, |sparse|=None)

    Arguments:

    |universe| -- the system for which the normal modes are calculated;
                  it must have a force field which provides the second
                  derivatives of the potential energy

    |temperature| -- the temperature for which the amplitudes of the
                     atomic displacement vectors are calculated. A
                     value of 'None' can be specified to have no scaling
                     at all. In that case the norm of each normal mode
                     vector is one.

    |subspace| -- the basis for the subspace in which the normal modes
                  are calculated (or, more precisely, a set of vectors
                  spanning the subspace; it does not have to be
                  orthogonal). This can either be a sequence of
                  Class:MMTK.ParticleVector objects or a tuple of two
                  such sequences. In the second case, the subspace is
                  defined by the space spanned by the second set of
                  vectors projected on the complement of the space
                  spanned by the first set of vectors. The first set
                  thus defines directions that are excluded from the
                  subspace.
                  The default value of None indicates a standard
                  normal mode calculation in the 3N-dimensional
                  configuration space.

    |delta| -- the rms step length for numerical differentiation.
               The default value of None indicates analytical differentiation.
               Numerical differentiation is available only when a
               subspace basis is used as well. Instead of calculating
               the full force constant matrix and then multiplying
               with the subspace basis, the subspace force constant
               matrix is obtained by numerical differentiation of the
               energy gradients along the basis vectors of the subspace.
               If the basis is much smaller than the full configuration
               space, this approach needs much less memory.

    |sparse| -- a boolean flag that indicates if a sparse representation of
                the force constant matrix is to be used. This is of
                interest when there are no long-range interactions and
                a subspace of smaller size then 3N is specified. In that
                case, the calculation will use much less memory with a sparse
                representation.

    Energetic normal modes describe the principal axes of a harmonic
    potential. They are obtained by diagonalizing the force constant
    matrix without prior mass-weighting.

    In order to obtain physically reasonable normal modes, the configuration
    of the universe must correspond to a local minimum of the potential
    energy.

    A EnergeticModes object behaves like a sequence of modes.
    Individual modes (see class Class:MMTK.NormalModes.VibrationalMode)
    can be extracted by indexing with an integer. Looping over the modes
    is possible as well.
    """

    features = []

    def __init__(self, universe=None, temperature = 300,
                 subspace = None, delta = None, sparse = False):
        if universe == None:
            return
        Features.checkFeatures(self, universe)
        Core.NormalModes.__init__(self, universe, subspace, delta, sparse,
                                  ['array', 'force_constants'])
        self.temperature = temperature

        self.weights = N.ones((1, 1), N.Float)

        self._forceConstantMatrix()
        ev = self._diagonalize()

        self.force_constants = ev
        self.sort_index = N.argsort(self.force_constants)
        self.array.shape = (self.nmodes, self.natoms, 3)

        self.cleanup()


    def __getitem__(self, item):
        index = self.sort_index[item]
        f = self.force_constants[index]
        #!!
        if self.temperature is None or item < 6:
            amplitude = 1.
        else:
            amplitude = N.sqrt(2.*self.temperature*Units.k_B
                               / self.force_constants[index])
        return EnergeticMode(self.universe, item,
                             self.force_constants[index],
                             amplitude*self.array[index])

    def rawMode(self, item):
        "Return unscaled mode vector"
        index = self.sort_index[item]
        f = self.force_constants[index]
        return EnergeticMode(self.universe, item,
                             self.force_constants[index],
                             self.array[index])

    def fluctuations(self, first_mode=6):
        """Returns a Class:MMTK.ParticleScalar containing the thermal
        fluctuations for each atom in the universe."""
        f = ParticleProperties.ParticleScalar(self.universe)
        for i in range(first_mode, self.nmodes):
            mode = self.rawMode(i)
            f += (mode*mode)/mode.force_constant
        f.array *= Units.k_B*self.temperature
        return f

    def anisotropicFluctuations(self, first_mode=6):
        """Returns a Class:MMTK.ParticleTensor containing the thermal
        fluctuations for each atom in the universe."""
        f = ParticleProperties.ParticleTensor(self.universe)
        for i in range(first_mode, self.nmodes):
            mode = self.rawMode(i)
            array = mode.array
            f.array += (array[:, :, N.NewAxis]*array[:, N.NewAxis, :]) \
                       / mode.force_constant
        f.array *= Units.k_B*self.temperature
        return f
