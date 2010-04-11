# This module implements classes that represent the atomic properties in a
# simulation, i.e. configurations, force vectors, etc.
#
# Written by Konrad Hinsen
# last revision: 2007-8-8
#

from MMTK import Utility
from Scientific.Geometry import Vector, isVector, Tensor, isTensor
from Scientific.indexing import index_expression
from Scientific import N
import copy

#
# Base class for all properties defined for a universe.
#
class ParticleProperty:

    """Property defined for each particle

    This is an abstract base class; for creating instances, use one of
    its subclasses: Class:MMTK.ParticleScalar, Class:MMTK.ParticleVector,
    Class:MMTK.ParticleTensor.

    ParticleProperty objects store properties that are defined per
    particle, such as mass, position, velocity, etc. The value
    corresponding to a particular atom can be retrieved or changed by
    indexing with the atom object.
    """

    def __init__(self, universe, data_rank, value_rank):
        universe.configuration()
        self.universe = universe
        self.version =  universe._version
        self.n = universe.numberOfPoints()
        self.data_rank = data_rank
        self.value_rank = value_rank

    is_particle_property = 1

    __safe_for_unpickling__ = 1
    __had_initargs__ = 1

    def __len__(self):
        return self.n

    def _checkCompatibility(self, other, allow_scalar=0):
        if isParticleProperty(other):
            if other.data_rank != self.data_rank:
                raise TypeError('Incompatible types')
            if self.universe != other.universe:
                raise ValueError('Variables are for different universes')
            if self.version != other.version:
                raise ValueError("Universe version numbers do not agree")
            if self.value_rank == other.value_rank:
                return self.return_class, other.array
            elif allow_scalar and (self.value_rank==0 or other.value_rank==0):
                if self.value_rank == 0:
                    return other.return_class, other.array
                else:
                    return self.return_class, other.array
            else:
                raise ValueError("Ranks do not match")
        elif isVector(other) or isTensor(other):
            if len(other.array.shape) > self.value_rank:
                raise TypeError('Incompatible types')
            return self.return_class, other.array
        else:
            return self.return_class, other

    def zero(self):
        """Returns an object of the element type (scalar, vector, etc.)
        with the value 0."""
        pass

    def sumOverParticles(self):
        "Returns the sum of the values for all particles."
        pass

    def _arithmetic(self, other, op, allow_scalar=0):
        a1 = self.array
        return_class, a2 = self._checkCompatibility(other, allow_scalar)
        if type(a2) != N.ArrayType:
            a2 = N.array([a2])
        if len(a1.shape) != len(a2.shape):
            if len(a1.shape) == 1:
                a1 = a1[index_expression[...] +
                        (len(a2.shape)-1)*index_expression[N.NewAxis]]
            else:
                a2 = a2[index_expression[...] +
                        (len(a1.shape)-1)*index_expression[N.NewAxis]]
        return return_class(self.universe, op(a1, a2))

    def __add__(self, other):
        return self._arithmetic(other, N.add)

    __radd__ = __add__

    def __sub__(self, other):
        return self._arithmetic(other, N.subtract)

    def __rsub__(self, other):
        return self._arithmetic(other, _rsub)

    def __mul__(self, other):
        return self._arithmetic(other, N.multiply, 1)

    __rmul__ = __mul__

    def __div__(self, other):
        return self._arithmetic(other, N.divide, 1)

    def __rdiv__(self, other):
        return self._arithmetic(other, _rdiv, 1)

    def __neg__(self):
        return self.return_class(self.universe, -self.array)

    def __copy__(self, memo = None):
        return self.__class__(self.universe, copy.copy(self.array))
    __deepcopy__ = __copy__

    def assign(self, other):
        """Copy all values from |other|, which must be a compatible
        ParticleProperty object."""
        self._checkCompatibility(other)
        self.array[:] = other.array[:]

    def scaleBy(self, factor):
        "Multiply all values by |factor| (a number)."
        self.array[:] = self.array[:]*factor

ParticleProperty.return_class = ParticleProperty

def _rsub(a , b):
    return N.subtract(b, a)

def _rdiv(a , b):
    return N.divide(b, a)


#
# One scalar per particle.
#
class ParticleScalar(ParticleProperty):

    """Scalar property defined for each particle

    A Glossary:Subclass of Class:MMTK.ParticleProperties.ParticleProperty.

    ParticleScalar objects can be added to each other and
    multiplied with scalars.
    """

    def __init__(self, universe, data_array=None):
	ParticleProperty.__init__(self, universe, 1, 0)
	if data_array is None:
	    self.array = N.zeros((self.n,), N.Float)
	else:
	    self.array = data_array
	    if data_array.shape[0] != self.n:
		raise ValueError('Data incompatible with universe')

    def __getitem__(self, item):
        if not isinstance(item, int):
            item = item.index
        return self.array[item]

    def __setitem__(self, item, value):
        if not isinstance(item, int):
            item = item.index
        self.array[item] = value

    def zero(self):
        return 0.

    def maximum(self):
        "Returns the highest value for any particle."
        return N.maximum.reduce(self.array)

    def minimum(self):
        "Returns the smallest value for any particle."
        return N.minimum.reduce(self.array)

    def sumOverParticles(self):
        return N.add.reduce(self.array)

    def applyFunction(self, function):
        """Applies |function| to each value and returns the result
        as a new ParticleScalar object."""
        return ParticleScalar(self.universe, function(self.array))


ParticleScalar.return_class = ParticleScalar

#
# One vector per particle.
#
class ParticleVector(ParticleProperty):

    """Vector property defined for each particle

    A Glossary:Subclass of Class:MMTK.ParticleProperties.ParticleProperty.

    ParticleVector objects can be added to each other and
    multiplied with scalars or Class:MMTK.ParticleScalar objects; all
    of these operations result in another ParticleVector
    object. Multiplication with a vector or another ParticleVector object
    yields a Class:MMTK.ParticleScalar object containing the dot products
    for each particle. Multiplications that treat ParticleVectors
    as vectors in a 3N-dimensional space are implemented as methods.
    """

    def __init__(self, universe, data_array=None):
	ParticleProperty.__init__(self, universe, 1, 1)
	if data_array is None:
	    self.array = N.zeros((self.n, 3), N.Float)
	else:
	    self.array = data_array
	    if data_array.shape[0] != self.n:
		raise ValueError('Data incompatible with universe')

    def __getitem__(self, item):
        if not isinstance(item, int):
            item = item.index
        return Vector(self.array[item])

    def __setitem__(self, item, value):
        if not isinstance(item, int):
            item = item.index
        self.array[item] = value.array

    def __mul__(self, other):
        if isParticleProperty(other):
            if self.universe != other.universe:
                raise ValueError('Variables are for different universes')
            if other.value_rank == 0:
                return ParticleVector(self.universe,
                                     self.array*other.array[:,N.NewAxis])
            elif other.value_rank == 1:
                return ParticleScalar(self.universe,
                                      N.add.reduce(self.array * \
                                                         other.array, -1))
            else:
                raise TypeError('not yet implemented')
        elif isVector(other):
            return ParticleScalar(self.universe,
                                  N.add.reduce(
                                     self.array*other.array[N.NewAxis,:],
                                      -1))
        elif isTensor(other):
            raise TypeError('not yet implemented')
        else:
            return ParticleVector(self.universe, self.array*other)

    __rmul__ = __mul__
    _product_with_vector = __mul__

    def zero(self):
        return Vector(0., 0., 0.)

    def length(self):
        """Returns a ParticleScalar containing the length of the vector
        for each particle."""
        return ParticleScalar(self.universe,
                              N.sqrt(N.add.reduce(self.array**2,
                                                              -1)))

    def sumOverParticles(self):
        return Vector(N.add.reduce(self.array, 0))

    def norm(self):
        """Returns the norm of the ParticleVector seen as a
        3N-dimensional vector."""
        return N.sqrt(N.add.reduce(N.ravel(self.array**2)))
    totalNorm = norm

    def scaledToNorm(self, norm):
        f = norm/self.norm()
        return ParticleVector(self.universe, f*self.array)

    def dotProduct(self, other):
        """Returns the dot product with |other| (a ParticleVector)
        treating both operands as 3N-dimensional vectors."""
        if self.universe != other.universe:
            raise ValueError('Variables are for different universes')
        return N.add.reduce(N.ravel(self.array * other.array))

    def massWeightedNorm(self):
        """Returns the mass-weighted norm of the ParticleVector seen as a
        3N-dimensional vector."""
        m = self.universe.masses().array
        return N.sqrt(N.sum(N.ravel(m[:, N.NewAxis] *
                                                      self.array**2))
                            / N.sum(m))

    def scaledToMassWeightedNorm(self, norm):
        f = norm/self.massWeightedNorm()
        return ParticleVector(self.universe, f*self.array)

    def massWeightedDotProduct(self, other):
        """Returns the mass-weighted dot product with |other|
        (a ParticleVector object) treating both operands as
        3N-dimensional vectors."""
        if self.universe != other.universe:
            raise ValueError('Variables are for different universes')
        m = self.universe.masses().array
        return N.add.reduce(N.ravel(self.array * other.array * \
                                                m[:, N.NewAxis]))

    def dyadicProduct(self, other):
        """Returns a Class:MMTK.ParticleTensor object representing the dyadic
        product with |other| (a ParticleVector)."""
        if self.universe != other.universe:
            raise ValueError('Variables are for different universes')
        return ParticleTensor(self.universe,
                              self.array[:, :, N.NewAxis] * \
                              other.array[:, N.NewAxis, :])

ParticleVector.return_class = ParticleVector

#
# Configuration variables: ParticleVector plus universe parameters
#
class Configuration(ParticleVector):

    """Configuration of a universe

    A Glossary:Subclass of Class:MMTK.ParticleVector.

    Its instances represent a configuration of a universe, consisting
    of positions for all atoms (like in a ParticleVector) plus
    the geometry of the universe itself, e.g. the cell shape for
    periodic universes.
    """

    def __init__(self, universe, data_array=None, cell = None):
	ParticleVector.__init__(self, universe, data_array)
	if cell is None:
	    self.cell_parameters = universe.cellParameters()
	else:
	    self.cell_parameters = cell

    is_configuration = 1

    def __add__(self, other):
        value = ParticleVector.__add__(self, other)
        return Configuration(self.universe, value.array, self.cell_parameters)

    def __sub__(self, other):
        value = ParticleVector.__sub__(self, other)
        return Configuration(self.universe, value.array, self.cell_parameters)

    def __copy__(self, memo = None):
        return self.__class__(self.universe, copy.copy(self.array),
                              copy.copy(self.cell_parameters))
    __deepcopy__ = __copy__

    def hasValidPositions(self):
        return N.logical_and.reduce(N.ravel(N.less(self.array,
                                                   Utility.undefined_limit)))

    def convertToBoxCoordinates(self):
        array = self.universe._realToBoxPointArray(self.array,
                                                   self.cell_parameters)
        self.array[:] = array

    def convertFromBoxCoordinates(self):
        array = self.universe._boxToRealPointArray(self.array,
                                                   self.cell_parameters)
        self.array[:] = array

#
# One tensor per particle.
#
class ParticleTensor(ParticleProperty):

    """Rank-2 tensor property defined for each particle

    A Glossary:Subclass of Class:MMTK.ParticleProperties.ParticleProperty.

    ParticleTensor objects can be added to each other and
    multiplied with scalars or Class:MMTK.ParticleScalar objects; all
    of these operations result in another ParticleTensor
    object.
    """

    def __init__(self, universe, data_array=None):
	ParticleProperty.__init__(self, universe, 1, 2)
	if data_array is None:
	    self.array = N.zeros((self.n, 3, 3), N.Float)
	else:
	    self.array = data_array
	    if data_array.shape[0] != self.n:
		raise ValueError('Data incompatible with universe')

    def __len__(self):
        return self.n

    def __getitem__(self, item):
        if not isinstance(item, int):
            item = item.index
        return Tensor(self.array[item])

    def __setitem__(self, item, value):
        if not isinstance(item, int):
            item = item.index
        self.array[item] = value.array

    def __mul__(self, other):
        if isParticleProperty(other):
            if self.universe != other.universe:
                raise ValueError('Variables are for different universes')
            if other.value_rank == 0:
                return ParticleTensor(self.universe,
                                      self.array*other.array[:,
                                                             N.NewAxis,
                                                             N.NewAxis])
            else:
                raise TypeError('not yet implemented')
        elif isVector(other):
            raise TypeError('not yet implemented')
        elif isTensor(other):
            raise TypeError('not yet implemented')
        else:
            return ParticleTensor(self.universe, self.array*other)

    __rmul__ = __mul__

    def zero(self):
        return Tensor([[0., 0., 0.], [0., 0., 0.], [0., 0., 0.]])

    def sumOverParticles(self):
        return Tensor(N.add.reduce(self.array, 0))

    def trace(self):
        return ParticleScalar(self.universe,
                              self.array[:, 0, 0] + self.array[:, 1, 1]
                              + self.array[:, 2, 2])

ParticleTensor.return_class = ParticleTensor

#
# One tensor per pair, symmetric.
#
class SymmetricPairTensor(ParticleProperty):

    def __init__(self, universe, data_array=None):
	ParticleProperty.__init__(self, universe, 2, 2)
	if data_array is None:
	    self.array = N.zeros((self.n,3, self.n,3), N.Float)
	else:
	    self.array = data_array
	    if data_array.shape[0] != self.n or \
	       data_array.shape[2] != self.n:
		raise ValueError('Data incompatible with universe')
	self.symmetrized = 0

    def __getitem__(self, item):
        i1, i2 = item
        if not isinstance(i1, int):
            i1 = i1.index
        if not isinstance(i2, int):
            i2 = i2.index
        if i1 > i2:
            i1, i2 = i2, i1
            return Tensor(N.transpose(self.array[i1,:,i2,:]))
        else:
            return Tensor(self.array[i1,:,i2,:])

    def __setitem__(self, item, value):
        i1, i2 = item
        if not isinstance(i1, int):
            i1 = i1.index
        if not isinstance(i2, int):
            i2 = i2.index
        if i1 > i2:
            i1, i2 = i2, i1
            self.array[i1,:,i2,:] = value.transpose().array
        else:
            self.array[i1,:,i2,:] = value.array

    def zero(self):
        return Tensor(3*[[0., 0., 0.]])

    def symmetrize(self):
        if not self.symmetrized:
            a = self.array
            n = a.shape[0]
            a.shape = (3*n, 3*n)
            nn = 3*n
            for i in range(nn):
                for j in range(i+1, nn):
                    a[j,i] = a[i,j]
            a.shape = (n, 3, n, 3)
            self.symmetrized = 1

    def __mul__(self, other):
        self.symmetrize()
        if isParticleProperty(other):
            if self.universe != other.universe:
                raise ValueError('Variables are for different universes')
            if other.value_rank == 1:
                n = self.array.shape[0]
                sa = N.reshape(self.array, (n, 3, 3*n))
                oa = N.reshape(other.array, (3*n, ))
                return ParticleVector(self.universe, N.dot(sa, oa))
            else:
                raise TypeError('not yet implemented')
            

SymmetricPairTensor.return_class = SymmetricPairTensor

#
# Type check function
#
def isParticleProperty(object):
    "Returns 1 if |object| is a ParticleProperty."
    return hasattr(object, 'is_particle_property')

def isConfiguration(object):
    "Returns 1 if |object| is a Configuration."
    return hasattr(object, 'is_configuration')
