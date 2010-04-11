# Deformation energy module
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

"""This module implements deformational energies for use in the analysis
of motions and conformational changes in macromolecules. A description
of the techniques can be found in [Article:Hinsen1998] and
[Article:Hinsen1999].
"""

try:
    from MMTK_forcefield import NonbondedList
    from MMTK_deformation import deformation, reduceDeformation, \
                                 reduceFiniteDeformation
except ImportError:
    pass
import ParticleProperties
from Scientific import N as Numeric

#
# Deformation energy evaluations
#
class DeformationEvaluationFunction:

    def __init__(self, universe, fc_length = 0.7, cutoff = 1.2,
                   factor = 46402., form = 'exponential'):
        self.universe = universe
        self.fc_length = fc_length
        self.cutoff = cutoff
        self.factor = factor

        nothing = Numeric.zeros((0,2), Numeric.Int)
        self.pairs = NonbondedList(nothing, nothing, nothing,
                                   universe._spec, cutoff)
        self.pairs.update(universe.configuration().array)
        self.normalize = 0
        try:
            self.version = self.forms.index(form)
        except ValueError:
            raise ValueError("unknown functional form")

    forms = ['exponential', 'calpha']

    def newConfiguration(self):
        self.pairs.update(self.universe.configuration().array)


class DeformationFunction(DeformationEvaluationFunction):

    """Infinite-displacement deformation function

    Constructor:  DeformationFunction(|universe|, |range|=0.7,
                                      |cutoff|=1.2, |factor|=46402.,
                                      |form| = 'exponential')

    Arguments:

    |universe| -- the universe for which the deformation function should be
                  defined

    |range| -- the range parameter r_0 in the pair interaction term

    |cutoff| -- the cutoff used in the deformation calculation

    |factor| -- a global scaling factor

    |form| -- the functional form ('exponential' or 'calpha')

    The default values are appropriate for a C_alpha model of a protein
    with the global scaling described in the reference cited above.

    A DeformationFunction object must be called with a single parameter,
    which is a ParticleVector object containing the infinitesimal displacements
    of the atoms for which the deformation is to be evaluated.
    The return value is a ParticleScalar object containing the
    deformation value for each atom.
    """

    def __call__(self, vector):
        conf = self.universe.configuration()
        r = ParticleProperties.ParticleScalar(self.universe)
        l = deformation(conf.array, vector.array, self.pairs,
                        None, r.array, self.cutoff, self.fc_length,
                        self.factor, self.normalize, 0, self.version)
        return r

class NormalizedDeformationFunction(DeformationFunction):

    """Normalized infinite-displacement deformation function

    Constructor:  NormalizedDeformationFunction(|universe|, |range|=0.7,
                                                |cutoff|=1.2, |factor|=46402.,
                                                |form| = 'exponential')

    Arguments:

    |universe| -- the universe for which the deformation function should be
                  defined

    |range| -- the range parameter r_0 in the pair interaction term

    |cutoff| -- the cutoff used in the deformation calculation

    |factor| -- a global scaling factor

    |form| -- the functional form ('exponential' or 'calpha')

    The default values are appropriate for a C_alpha model of a protein
    with the global scaling described in the reference cited above.
    The normalization is defined by equation 10 of reference 1.
    
    A NormalizedDeformationFunction object must be called with a single
    parameter, which is a ParticleVector object containing the infinitesimal
    displacements of the atoms for which the deformation is to be evaluated.
    The return value is a ParticleScalar object containing the
    deformation value for each atom.
    """

    def __init__(self, *args, **kwargs):
        apply(DeformationFunction.__init__, (self, ) + args, kwargs)
        self.normalize = 1


class FiniteDeformationFunction(DeformationEvaluationFunction):

    """Finite-displacement deformation function

    Constructor:  FiniteDeformationFunction(|universe|, |range|=0.7,
                                            |cutoff|=1.2, |factor|=46402.,
                                            |form| = 'exponential')

    Arguments:

    |universe| -- the universe for which the deformation function should be
                  defined

    |range| -- the range parameter r_0 in the pair interaction term

    |cutoff| -- the cutoff used in the deformation calculation

    |factor| -- a global scaling factor

    |form| -- the functional form ('exponential' or 'calpha')

    The default values are appropriate for a C_alpha model of a protein
    with the global scaling described in the reference cited above.

    A FiniteDeformationFunction object must be called with a single parameter,
    which is a Configuration or a ParticleVector object containing the
    alternate configuration of the universe for which the deformation is to be
    evaluated.
    The return value is a ParticleScalar object containing the
    deformation value for each atom.
    """

    def __call__(self, vector):
        conf = self.universe.configuration()
        vector = vector-conf
        r = ParticleProperties.ParticleScalar(self.universe)
        l = deformation(conf.array, vector.array, self.pairs, None, r.array,
                        self.cutoff, self.fc_length, self.factor, 0, 1,
                        self.version)
        return r

class DeformationEnergyFunction(DeformationEvaluationFunction):

    """Infinite-displacement deformation energy function

    The deformation energy is the sum of the deformation values over
    all atoms of a system.

    Constructor:  DeformationEnergyFunction(|universe|, |range|=0.7,
                                            |cutoff|=1.2, |factor|=46402.,
                                            |form| = 'exponential')

    Arguments:

    |universe| -- the universe for which the deformation energy should be
                  defined

    |range| -- the range parameter r_0 in the pair interaction term

    |cutoff| -- the cutoff used in the deformation energy calculation

    |factor| -- a global scaling factor

    |form| -- the functional form ('exponential' or 'calpha')

    The default values are appropriate for a C_alpha model of a protein
    with the global scaling described in the reference cited above.

    A DeformationEnergyFunction is called with one or two parameters.
    The first parameter is a ParticleVector object containing the
    infinitesimal displacements of the atoms for which the deformation
    energy is to be evaluated. The optional second argument can be
    set to a non-zero value to request the gradients of the energy
    in addition to the energy itself. In that case there are two
    return values (energy and the gradients in a ParticleVector
    object), otherwise only the energy is returned.
    """

    def __call__(self, vector, gradients = None):
        conf = self.universe.configuration()
        g = None
        if gradients is not None:
            if ParticleProperties.isParticleProperty(gradients):
                g = gradients
            elif type(gradients) == Numeric.arraytype:
                g = ParticleProperties.ParticleVector(self.universe, gradients)
            elif gradients:
                g = ParticleProperties.ParticleVector(self.universe)
        if g is None:
            g_array = None
        else:
            g_array = g.array
        l = deformation(conf.array, vector.array, self.pairs,
                        g_array, None, self.cutoff, self.fc_length,
                        self.factor, self.normalize, 0, self.version)
        if g is None:
            return l
        else:
            return l, g

class NormalizedDeformationEnergyFunction(DeformationEnergyFunction):

    """Normalized infinite-displacement deformation energy function

    The normalized deformation energy is the sum of the normalized
    deformation values over all atoms of a system.

    Constructor: NormalizedDeformationEnergyFunction(|universe|, |range|=0.7,
                                                     |cutoff|=1.2,
                                                     |factor|=46402.,
                                                     |form|='exponential')

    Arguments:

    |universe| -- the universe for which the deformation energy should be
                  defined

    |range| -- the range parameter r_0 in the pair interaction term

    |cutoff| -- the cutoff used in the deformation energy calculation

    |factor| -- a global scaling factor

    |form| -- the functional form ('exponential' or 'calpha')

    The default values are appropriate for a C_alpha model of a protein
    with the global scaling described in the reference cited above.
    The normalization is defined by equation 10 of reference 1.

    A NormalizedDeformationEnergyFunction is called with one or two parameters.
    The first parameter is a ParticleVector object containing the
    infinitesimal displacements of the atoms for which the deformation
    energy is to be evaluated. The optional second argument can be
    set to a non-zero value to request the gradients of the energy
    in addition to the energy itself. In that case there are two
    return values (energy and the gradients in a ParticleVector
    object), otherwise only the energy is returned.
    """

    def __init__(self, *args):
        apply(DeformationEnergyFunction.__init__, (self,) + args)
        self.normalize = 1


class FiniteDeformationEnergyFunction(DeformationEvaluationFunction):

    """Finite-displacement deformation energy function

    The deformation energy is the sum of the
    deformation values over all atoms of a system.

    Constructor: FiniteDeformationEnergyFunction(|universe|, |range|=0.7,
                                                 |cutoff|=1.2, |factor|=46402.,
                                                 |form|='exponential')

    Arguments:

    |universe| -- the universe for which the deformation energy should be
                  defined

    |range| -- the range parameter r_0 in the pair interaction term

    |cutoff| -- the cutoff used in the deformation energy calculation

    |factor| -- a global scaling factor

    |form| -- the functional form ('exponential' or 'calpha')

    The default values are appropriate for a C_alpha model of a protein
    with the global scaling described in the reference cited above.

    A FiniteDeformationEnergyFunction is called with one or two parameters.
    The first parameter is a ParticleVector object containing the
    alternate configuration of the universe for which the deformation
    energy is to be evaluated. The optional second argument can be
    set to a non-zero value to request the gradients of the energy
    in addition to the energy itself. In that case there are two
    return values (energy and the gradients in a ParticleVector
    object), otherwise only the energy is returned.
    """

    def __call__(self, vector, gradients = None):
        conf = self.universe.configuration()
        g = None
        if gradients is not None:
            if ParticleProperties.isParticleProperty(gradients):
                g = gradients
            elif type(gradients) == Numeric.arraytype:
                g = ParticleProperties.ParticleVector(self.universe, gradients)
            elif gradients:
                g = ParticleProperties.ParticleVector(self.universe)
        if g is None:
            g_array = None
        else:
            g_array = g.array
        l = deformation(conf.array, vector.array, self.pairs, g_array, None,
                        self.cutoff, self.fc_length, self.factor,
                        0, 1, self.version)
        if g is None:
            return l
        else:
            return l, g

#
# Deformation energy minimization
#
class DeformationReducer(DeformationEvaluationFunction):

    """Iterative reduction of the deformation energy

    Constructor:  DeformationReducer(|universe|, |range|=0.7,
                                     |cutoff|=1.2, |factor|=46402.,
                                     |form|='exponential')

    Arguments:

    |universe| -- the universe for which the deformation function should be
                  defined

    |range| -- the range parameter r_0 in the pair interaction term

    |cutoff| -- the cutoff used in the deformation calculation

    |factor| -- a global scaling factor

    |form| -- the functional form ('exponential' or 'calpha')

    The default values are appropriate for a C_alpha model of a protein
    with the global scaling described in the reference cited above.

    A DeformationReducer is called with two arguments. The first
    is a ParticleVector containing the initial infinitesimal displacements
    for all atoms. The second is an integer indicating the number of
    iterations. The result is a modification of the displacements
    by steepest-descent minimization of the deformation energy.
    """

    def __call__(self, vector, niter):
        conf = self.universe.configuration()
        reduceDeformation(conf.array, vector.array, self.pairs,
                          self.cutoff, self.fc_length, self.factor, niter,
                          self.version)

class FiniteDeformationReducer(DeformationEvaluationFunction):

    """Iterative reduction of the finite-displacement deformation energy

    Constructor:  FiniteDeformationReducer(|universe|, |range|=0.7,
                                           |cutoff|=1.2, |factor|=46402.,
                                           |form|='exponential')

    Arguments:

    |universe| -- the universe for which the deformation function should be
                  defined

    |range| -- the range parameter r_0 in the pair interaction term

    |cutoff| -- the cutoff used in the deformation calculation

    |factor| -- a global scaling factor

    |form| -- the functional form ('exponential' or 'calpha')

    The default values are appropriate for a C_alpha model of a protein
    with the global scaling described in the reference cited above.

    A FiniteDeformationReducer is called with two arguments. The first
    is a ParticleVector or Configuration containing the alternate
    configuration for which the deformation energy is evaluated.
    The second is the RMS distance that defines the termination
    condition. The return value a configuration that differs from
    the input configuration by approximately the specified RMS distance,
    and which is obtained by iterative steepest-descent minimization of
    the finite-displacement deformation energy.
    """

    def __call__(self, vector, rms_reduction):
        conf = self.universe.configuration()
        vector = vector-conf
        reduceFiniteDeformation(conf.array, vector.array, self.pairs,
                                self.cutoff, self.fc_length, self.factor,
                                rms_reduction, self.version)
        return conf+vector
