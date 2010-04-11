# This module implements energy minimizers.
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

import Features, ThreadManager, Trajectory, Units
from MMTK_minimization import conjugateGradient, steepestDescent
from Scientific import N as Numeric
import operator

try:
    import threading
    if not hasattr(threading, 'Thread'):
	threading = None
except ImportError:
    threading = None

#
# Thread subclass
#
if threading:

    class MinimizerThread(threading.Thread):

        def __init__(self, universe, target, args):
            threading.Thread.__init__(self, group = None,
                                      name = 'Energy minimization',
                                      target = target,
                                      args = args)
            self.universe = universe
            self.function = (target, args)
            self.start()
            ThreadManager.registerThread(self)

        def run(self):
            self.universe.acquireConfigurationChangeLock()
            apply(apply, self.function)
            self.universe.releaseConfigurationChangeLock()

#
# Minimizer base class
#
class Minimizer(Trajectory.TrajectoryGenerator):

    def __init__(self, universe, options):
	Trajectory.TrajectoryGenerator.__init__(self, universe, options)

    default_options = {'steps': 100, 'step_size': 0.02*Units.Ang,
		       'convergence': 0.01*Units.kJ/(Units.mol*Units.nm),
                       'background': 0, 'threads': None,
                       'mpi_communicator': None, 'actions': []}

    available_data = ['energy', 'configuration', 'gradients']

    restart_data = ['configuration', 'energy']

    def __call__(self, options):
	raise AttributeError

#
# Steepest descent minimizer
#
class SteepestDescentMinimizer(Minimizer):

    """Steepest-descent minimizer

    The minimizer can handle fixed atoms, but no distance constraints.
    It is fully thread-safe.

    Constructor: SteepestDescentMinimizer(|universe|, |**options|)

    Arguments:

    |universe| -- the universe on which the minimizer acts

    |options| -- keyword options:

      * steps: the number of minimization steps (default is 100)
      * step_size: the initial size of a minimization step
                   (default is 0.002 nm)
      * convergence: the root-mean-square gradient length at which
                     minimization stops (default is 0.01 kJ/mol/nm)
      * actions: a list of actions to be executed periodically (default is
                 none)
      * threads: the number of threads to use in energy evaluation
                 (default set by MMTK_ENERGY_THREADS)
      * background: if true, the minimization is executed as a separate thread
                    (default: 0)
      * mpi_communicator: an MPI communicator object, or None, meaning
                          no parallelization (default: None)

    The minimization is started by calling the minimizer object.
    All the keyword options listed above can be specified either when
    creating the minimizer or when calling it.

    The following data categories and variables are available for
    output:

    - category "configuration": configuration and box size (for
      periodic universes)

    - category "gradients": energy gradients for each atom

    - category "energy": potential energy and
                         norm of the potential energy gradient
    """

    def __init__(self, universe, **options):
	Minimizer.__init__(self, universe, options)
	self.features = [Features.FixedParticleFeature,
			 Features.NoseThermostatFeature,
                         Features.AndersenBarostatFeature]

    def __call__(self, **options):
	self.setCallOptions(options)
	Features.checkFeatures(self, self.universe)
	configuration = self.universe.configuration()
	fixed = self.universe.getAtomBooleanArray('fixed')
        nt = self.getOption('threads')
        comm = self.getOption('mpi_communicator')
	evaluator = self.universe.energyEvaluator(threads=nt,
                                                  mpi_communicator=comm)
        evaluator = evaluator.CEvaluator()
	args = (self.universe,
                configuration.array, fixed.array, evaluator,
                self.getOption('steps'), self.getOption('step_size'),
                self.getOption('convergence'), self.getActions(),
                'Steepest descent minimization with ' +
                self.optionString(['convergence', 'step_size', 'steps']))
        if self.getOption('background'):
            if not threading:
                raise OSError("background processing not available")
            return MinimizerThread(self.universe, steepestDescent, args)
        else:
            apply(steepestDescent, args)

#
# Conjugate gradient minimizer
#
class ConjugateGradientMinimizer(Minimizer):

    """Conjugate gradient minimizer

    The minimizer can handle fixed atoms, but no distance constraints.
    It is fully thread-safe.

    Constructor: ConjugateGradientMinimizer(|universe|, |**options|)

    Arguments:

    |universe| -- the universe on which the minimizer acts

    |options| -- keyword options:

      * steps: the number of minimization steps (default is 100)
      * step_size: the initial size of a minimization step
                   (default is 0.002 nm)
      * convergence: the root-mean-square gradient length at which
                     minimization stops (default is 0.01 kJ/mol/nm)
      * actions: a list of actions to be executed periodically (default is
                 none)
      * threads: the number of threads to use in energy evaluation
                 (default set by MMTK_ENERGY_THREADS)
      * background: if true, the minimization is executed as a separate thread
                    (default: 0)

    The minimization is started by calling the minimizer object.
    All the keyword options listed above can be specified either when
    creating the minimizer or when calling it.

    The following data categories and variables are available for
    output:

    - category "configuration": configuration and box size (for
      periodic universes)

    - category "gradients": energy gradients for each atom

    - category "energy": potential energy and
                         norm of the potential energy gradient
    """

    def __init__(self, universe, **options):
	Minimizer.__init__(self, universe, options)
	self.features = [Features.FixedParticleFeature,
			 Features.NoseThermostatFeature]

    def __call__(self, **options):
	self.setCallOptions(options)
	Features.checkFeatures(self, self.universe)
	configuration = self.universe.configuration()
	fixed = self.universe.getAtomBooleanArray('fixed')
        nt = self.getOption('threads')
	evaluator = self.universe.energyEvaluator(threads=nt).CEvaluator()
	args =(self.universe,
               configuration.array, fixed.array, evaluator,
               self.getOption('steps'), self.getOption('step_size'),
               self.getOption('convergence'), self.getActions(),
               'Conjugate gradient minimization with ' +
               self.optionString(['convergence', 'step_size', 'steps']))
        if self.getOption('background'):
            if not threading:
                raise OSError("background processing not available")
            return MinimizerThread(self.universe, conjugateGradient, args)
        else:
            apply(conjugateGradient, args)
