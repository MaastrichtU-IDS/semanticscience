# This module contains code for solvation.
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

"""See also the example Example:MolecularDynamics:solvation.py.
"""

import ChemicalObjects, Units, Universe
from MolecularSurface import surfaceAndVolume
from Minimization import SteepestDescentMinimizer
from Dynamics import VelocityVerletIntegrator, VelocityScaler, \
                     TranslationRemover, RotationRemover
from Trajectory import Trajectory, TrajectoryOutput, SnapshotGenerator, \
                       StandardLogOutput
import copy, sys

#
# Calculate the number of solvent molecules
#
def numberOfSolventMolecules(universe, solvent, density):
    """Returns the number of solvent molecules of type |solvent|
    that must be added to |universe|, in addition to whatever it
    contains already, to obtain the specified solvent |density|."""
    if type(solvent) == type(''):
	solvent = ChemicalObjects.Molecule(solvent)
    cell_volume = universe.cellVolume()
    if cell_volume is None:
	raise TypeError("universe volume is undefined")
    solute_volume = 0.
    for o in universe._objects:
	solute_volume = solute_volume + surfaceAndVolume(o)[1]
    return int(round(density*(cell_volume-solute_volume)/solvent.mass()))

#
# Add solvent to a universe containing solute molecules.
#
def addSolvent(universe, solvent, density, scale_factor=4.):
    """Scales up the universe by |scale_factor| and adds as many
    molecules of type |solvent| (a molecul object or a string)
    as are necessary to obtain the specified solvent |density|,
    taking account of the solute molecules that are already present
    in the universe. The molecules are placed at random positions
    in the scaled-up universe, but without overlaps between
    any two molecules."""

    # Calculate number of solvent molecules and universe size
    if type(solvent) == type(''):
	solvent = ChemicalObjects.Molecule(solvent)
    cell_volume = universe.cellVolume()
    if cell_volume is None:
	raise TypeError("universe volume is undefined")
    solute = copy.copy(universe._objects)
    solute_volume = 0.
    excluded_regions = []
    for o in solute:
	solute_volume = solute_volume + surfaceAndVolume(o)[1]
	excluded_regions.append(o.boundingSphere())
    n_solvent = int(round(density*(cell_volume-solute_volume)/solvent.mass()))
    solvent_volume = n_solvent*solvent.mass()/density
    cell_volume = solvent_volume + solute_volume
    universe.translateBy(-solute.position())
    universe.scaleSize((cell_volume/universe.cellVolume())**(1./3.))

    # Scale up the universe and add solvent molecules at random positions
    universe.scaleSize(scale_factor)
    universe.scale_factor = scale_factor
    for i in range(n_solvent):
	m = copy.copy(solvent)
	m.translateTo(universe.randomPoint())
	while 1:
	    s = m.boundingSphere()
	    collision = 0
	    for region in excluded_regions:
		if (s.center-region.center).length() < s.radius+region.radius:
		    collision = 1
		    break
	    if not collision:
		break
	    m.translateTo(universe.randomPoint())
	universe.addObject(m)
	excluded_regions.append(s)

#
# Shrink the universe to its final size
#
def shrinkUniverse(universe, temperature=300.*Units.K, trajectory=None,
                   scale_factor=0.95):
    """Shrinks |universe|, which must have been scaled up by
    Function:MMTK.Solvation.addSolvent, back to its original size.
    The compression is performed in small steps, in between which
    some energy minimization and molecular dynamics steps are executed.
    The molecular dynamics is run at the given |temperature|, and
    an optional |trajectory| (a MMTK.Trajectory.Trajectory object or
    a string, interpreted as a file name) can be specified in which
    intermediate configurations are stored.
    """

    # Set velocities and initialize trajectory output
    universe.initializeVelocitiesToTemperature(temperature)
    if trajectory is not None:
        if type(trajectory) == type(''):
            trajectory = Trajectory(universe, trajectory, "w",
                                    "solvation protocol")
            close_trajectory = 1
        else:
            close_trajectory = 0
        actions = [TrajectoryOutput(trajectory, ["configuration"], 0, None, 1)]
        snapshot = SnapshotGenerator(universe, actions=actions)
        snapshot()

    # Do some minimization and equilibration
    minimizer = SteepestDescentMinimizer(universe, step_size = 0.05*Units.Ang)
    actions = [VelocityScaler(temperature, 0.01*temperature, 0, None, 1),
               TranslationRemover(0, None, 20)]
    integrator = VelocityVerletIntegrator(universe, delta_t = 0.5*Units.fs,
                                          actions = actions)
    for i in range(5):
	minimizer(steps = 40)
    integrator(steps = 200)

    # Scale down the system in small steps
    i = 0
    while universe.scale_factor > 1.:
        if trajectory is not None and i % 1 == 0:
            snapshot()
        i = i + 1
	step_factor = max(scale_factor, 1./universe.scale_factor)
	for object in universe:
	    object.translateTo(step_factor*object.position())
	universe.scaleSize(step_factor)
	universe.scale_factor = universe.scale_factor*step_factor
	for i in range(3):
	    minimizer(steps = 10)
	integrator(steps = 50)

    del universe.scale_factor

    if trajectory is not None:
        snapshot()
        if close_trajectory:
            trajectory.close()
