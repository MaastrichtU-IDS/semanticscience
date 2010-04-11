# This module implements a DCD reader/writer
#
# Written by Lutz Ehrlich
# Adapted to MMTK conventions by Konrad Hinsen
# last revision: 2006-11-27
#
import MMTK_DCD
import PDB, Trajectory, Units
from Scientific import N as Numeric
import copy, operator


class DCDReader(Trajectory.TrajectoryGenerator):

    """Reader for DCD trajectories (CHARMM/X-Plor)

    A DCDReader reads a DCD trajectory and "plays back" the
    data as if it were generated directly by an integrator.
    The universe for which the DCD file is read must be
    perfectly compatible with the data in the file, including
    an identical internal atom numbering. This can be guaranteed
    only if the universe was created from a PDB file that is
    compatible with the DCD file without leaving out any
    part of the system.

    Constructor: DCDReader(|universe|, |**options|)

    Arguments:

    |universe| -- the universe for which the information from the
                  trajectory file is read

    |options| -- keyword options:

      * dcd_file:  the name of the DCD trajecory file to be read
      * actions: a list of actions to be executed periodically (default is
                 none)

    Reading is started by calling the reader object.
    All the keyword options listed above can be specified either when
    creating the reader or when calling it.

    The following data categories and variables are available for
    output:

    - category "time": time

    - category "configuration": configuration
    """

    default_options = {}

    available_data = ['configuration', 'time']

    restart_data = None

    def __init__(self, universe, **options):
        Trajectory.TrajectoryGenerator.__init__(self, universe, options)

    def __call__(self, **options):
        self.setCallOptions(options)
        configuration = self.universe.configuration()
        MMTK_DCD.readDCD(self.universe, configuration.array,
                         self.getActions(), self.getOption('dcd_file'))

        
def writeDCD(vector_list, dcd_file_name, factor, atom_order=None,
             delta_t=0.1, conf_flag=1):
    universe = vector_list[0].universe
    natoms = universe.numberOfPoints()
    if atom_order is None:
        atom_order = Numeric.arrayrange(natoms)
    else:
        atom_order = Numeric.array(atom_order)

    i_start = 0       # always start at frame 0
    n_savc  = 1       # save every frame
    fd = MMTK_DCD.writeOpenDCD(dcd_file_name, natoms, len(vector_list),
                               i_start, n_savc, delta_t)
    for vector in vector_list:
        if conf_flag:
            vector = universe.contiguousObjectConfiguration(None, vector)
        array = factor*vector.array
        x = Numeric.take(array[:, 0], atom_order).astype(Numeric.Float16)
        y = Numeric.take(array[:, 1], atom_order).astype(Numeric.Float16)
        z = Numeric.take(array[:, 2], atom_order).astype(Numeric.Float16)
        MMTK_DCD.writeDCDStep(fd, x, y, z)
    MMTK_DCD.writeCloseDCD(fd)

def writePDB(universe, configuration, pdb_file_name):
    offset = None
    if universe is not None:
        configuration = universe.contiguousObjectConfiguration(None,
                                                               configuration)
    pdb = PDB.PDBOutputFile(pdb_file_name, 'xplor')
    pdb.write(universe, configuration)
    sequence = pdb.atom_sequence
    pdb.close()
    return sequence

def writeDCDPDB(conf_list, dcd_file_name, pdb_file_name, delta_t=0.1):
    """Write the configurations in |conf_list| (any sequence of Configuration
    objects) to a newly created DCD trajectory file with the name
    |dcd_file_name|. Also write the first configuration to a PDB file
    with the name |pdb_file_name|; this PDB file has the same atom order
    as the DCD file. The time step between configurations can be specified
    by |delta_t|.
    """
    universe = conf_list[0].universe
    sequence = writePDB(universe, conf_list[0], pdb_file_name)
    indices = map(lambda a: a.index, sequence)
    writeDCD(conf_list, dcd_file_name, 1./Units.Ang, indices, delta_t, 1)


def writeVelocityDCDPDB(vel_list, dcd_file_name, pdb_file_name, delta_t=0.1):
    """Write the velocities in |vel_list| (any sequence of ParticleVector
    objects) to a newly created DCD trajectory file with the name
    |dcd_file_name|. Also write the first configuration to a PDB file
    with the name |pdb_file_name|; this PDB file has the same atom order
    as the DCD file. The time step between configurations can be specified
    by |delta_t|.
    """
    universe = vel_list[0].universe
    sequence = writePDB(universe, universe.configuration(), pdb_file_name)
    indices = map(lambda a: a.index, sequence)
    writeDCD(vel_list, dcd_file_name, 1./(Units.Ang/Units.akma_time),
             indices, delta_t, 0)
