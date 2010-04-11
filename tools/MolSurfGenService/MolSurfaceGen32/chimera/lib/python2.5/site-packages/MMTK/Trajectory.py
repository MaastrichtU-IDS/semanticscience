# This module implements trajetories and trajectory generators.
#
# Written by Konrad Hinsen
# last revision: 2007-6-15
#

import Collections, Units, Universe, Utility, ParticleProperties, Visualization
from Scientific.Geometry import Vector
from Scientific import N as Numeric
import copy, os, string, sys, types

# Report error if the netCDF module is not available.
try:
    from Scientific.IO import NetCDF
except ImportError:
    raise Utility.MMTKError("Trajectories are not available " +
                             "because the netCDF module is missing.")

#
# Trajectory class
#
class Trajectory:

    """Trajectory file

    Constructor: Trajectory(|object|, |filename|, |mode|="r",
                            |comment|=None, |double_precision|=0, |cycle|=0,
                            |block_size|=1)

    Arguments:

    |object| -- the object whose data is stored in the trajectory file.
                This can be 'None' when opening a file for reading;
                in that case, a universe object is constructed from the
                description stored in the trajectory file. This universe
                object can be accessed via the attribute 'universe'
                of the trajectory object.

    |filename| -- the name of the trajectory file

    |mode| -- one of "r" (read-only), "w" (create new file for writing),
              or "a" (append to existing file or create if the file does
              not exist)

    |comment| -- optional comment that is stored in the file; allowed only
                 with mode="r"

    |double_precision| -- if non-zero, data in the file is stored using
                          double precision; default is single precision.
                          Note that all I/O via trajectory objects is
                          double precision; conversion from and to single
                          precision file variables is handled automatically.

    |cycle| -- if non-zero, a trajectory is created for a fixed number
               of steps equal to the value of |cycle|, and these steps
               are used cyclically. This is meant for restart trajectories.

    |block_size| -- an optimization parameter that influences the file
                    structure and the I/O performance for very large
                    files. A block size of 1 is optimal for sequential
                    access to configurations etc., whereas a block size
                    equal to the number of steps is optimal for reading
                    coordinates or scalar variables along the time axis.
                    The default value is 1. Note that older MMTK releases
                    always used a block size of 1 and cannot handle
                    trajectories with different block sizes.

    The data in a trajectory file can be accessed by step or by
    variable. If 't' is a Trajectory object, then:

    - 'len(t)' is the number of steps

    - 't[i]' is the data for step i, in the form of a dictionary that
      maps variable names to data

    - 't[i:j]' and 't[i:j:n]' return a SubTrajectory object that refers
       to a subset of the total number of steps (no data is copied)

    - 't.variable' returns the value of the named variable at all
      time steps. If the variable is a simple scalar, it is read
      completely and returned as an array. If the variable contains
      data for each atom, a TrajectoryVariable object is returned
      from which data at specific steps can be obtained by further
      indexing operations.

    The routines that generate trajectories decide what variables
    are used and what they contain. The most frequently used variable
    is "configuration", which stores the positions of all atoms.
    Other common variables are "time", "velocities", "temperature",
    "pressure", and various energy terms whose name end with "_energy".
    """

    def __init__(self, object, filename, mode = 'r', comment = None,
                 double_precision = 0, cycle = 0, block_size = 1):
        filename = os.path.expanduser(filename)
        self.filename = filename
        if object is None and mode == 'r':
            file = NetCDF.NetCDFFile(filename, 'r')
            description = file.variables['description'][:].tostring()
            try:
                self.block_size = file.dimensions['minor_step_number']
            except KeyError:
                self.block_size = 1
            conf = None
            cell = None
            if self.block_size == 1:
                try:
                    conf_var = file.variables['configuration']
                    conf = conf_var[0, :, :]
                except KeyError: pass
                try:
                    cell = file.variables['box_size'][0, :]
                except KeyError: pass
            else:
                try:
                    conf_var = file.variables['configuration']
                    conf = conf_var[0, :, :, 0]
                except KeyError: pass
                try:
                    cell = file.variables['box_size'][0, :, 0]
                except KeyError: pass
            file.close()
            import Skeleton
            local = {}
            skeleton = eval(description, vars(Skeleton), local)
            universe = skeleton.make({}, conf)
            universe.setCellParameters(cell)
            object = universe
            initialize = 1
        else:
            universe = object.universe()
            if universe is None:
                raise ValueError("objects not in the same universe")
            description = None
            initialize = 0
        universe.configuration()
        if object is universe:
            index_map = None
            inverse_map = None
        else:
            if mode == 'r':
                raise ValueError("can't read trajectory for a non-universe")
            index_map = Numeric.array(map(lambda a:a.index, object.atomList()))
            inverse_map = universe.numberOfPoints()*[None]
            for i in range(len(index_map)):
                inverse_map[index_map[i]] = i
            toplevel = {}
            for o in Collections.Collection(object):
                toplevel[o.topLevelChemicalObject()] = 1
            object = Collections.Collection(toplevel.keys())
        if description is None:
            description = universe.description(object, inverse_map)
        import MMTK_trajectory
        self.trajectory = MMTK_trajectory.Trajectory(universe, description,
                                                     index_map, filename,
                                                     mode + 's',
                                                     double_precision, cycle,
                                                     block_size)
        self.universe = universe
        self.index_map = index_map
        try:
            self.block_size = \
                       self.trajectory.file.dimensions['minor_step_number']
        except KeyError:
            self.block_size = 1
        if comment is not None:
            if mode == 'r':
                raise IOError('cannot add comment in read-only mode')
            self.trajectory.file.comment = comment
        if initialize and conf is not None:
            self.universe.setFromTrajectory(self)
        self.particle_trajectory_reader = ParticleTrajectoryReader(self)

    def close(self):
        """Close the trajectory file. Must be called after writing to
        ensure that all buffered data is written to the file. No data
        access is possible after closing a file."""
        self.trajectory.close()

    def __len__(self):
        return self.trajectory.nsteps

    def __getitem__(self, item):
        if not isinstance(item, int):
            return SubTrajectory(self, Numeric.arange(len(self)))[item]
        if item < 0:
            item = item + len(self)
        if item >= len(self):
            raise IndexError
        data = {}
        for name, var in self.trajectory.file.variables.items():
            if 'step_number' not in var.dimensions:
                continue
            if 'atom_number' in var.dimensions:
                if 'xyz' in var.dimensions:
                    array = ParticleProperties.ParticleVector(self.universe,
                                self.trajectory.readParticleVector(name, item))
                else:
                    array = ParticleProperties.ParticleScalar(self.universe,
                                self.trajectory.readParticleScalar(name, item))
            else:
                bs = self.block_size
                if bs == 1:
                    array = var[item]
                else:
                    if len(var.shape) == 2:
                        array = var[item/bs, item%bs]
                    else:
                        array = var[item/bs, ..., item%bs]
            data[name] = 0.+array
        if data.has_key('configuration'):
            box = data.get('box_size', None)
            if box is not None:
                box = box.astype(Numeric.Float)
            conf = data['configuration']
            data['configuration'] = \
               ParticleProperties.Configuration(conf.universe, conf.array, box)
        return data

    def __getslice__(self, first, last):
        return self[(slice(first, last),)]

    def __getattr__(self, name):
        try:
            var = self.trajectory.file.variables[name]
        except KeyError:
            raise AttributeError("no variable named " + name)
        if 'atom_number' in var.dimensions:
            return TrajectoryVariable(self.universe, self, name)
        else:
            return Numeric.ravel(Numeric.array(var))[:len(self)]

    def defaultStep(self):
        try:
            step = int(self.trajectory.file.last_step[0])
        except AttributeError:
            step = 0
        return step

    def readParticleTrajectory(self, atom, first=0, last=None, skip=1,
                               variable = "configuration"):
        """Read the values of the specified |variable| for the specified
        |atom| at all time steps from |first| to |last| with an
        increment of |skip|. The result is a ParticleTrajectory object.
        If the variable is "configuration", the resulting trajectory
        is made continuous by eliminating all jumps caused by periodic
        boundary conditions. The pseudo-variable "box_coordinates"
        can be read to obtain the values of the variable "configuration"
        scaled to box coordinates. For non-periodic universes there is
        no difference between box coordinates and real coordinates."""
        return ParticleTrajectory(self, atom, first, last, skip, variable)

    def readRigidBodyTrajectory(self, object, first=0, last=None, skip=1,
                                reference = None):
        """Read the positions for the specified |object| at all time steps
        from |first| to |last| with an increment of |skip| and extract
        the rigid-body motion (center-of-mass position plus orientation as
        a quaternion) by an optimal-transformation fit. The result is a
        RigidBodyTrajectory object."""
        return RigidBodyTrajectory(self, object, first, last, skip, reference)

    def variables(self):
        """Returns a list of the names of all variables that are stored
        in the trajectory."""
        vars = copy.copy(self.trajectory.file.variables.keys())
        vars.remove('step')
        try:
            vars.remove('description')
        except ValueError: pass
        return vars

    def view(self, first=0, last=None, step=1, object = None):
        """Show an animation of |object| using the positions in the
        trajectory at all time steps from |first| to |last| with an
        increment of |skip|. |object| defaults to the entire universe."""
        Visualization.viewTrajectory(self, first, last, step, object)

    def _boxTransformation(self, pt_in, pt_out, to_box=0):
        from MMTK_trajectory import boxTransformation
        try:
            box_size = self.trajectory.recently_read_box_size
        except AttributeError:
            return
        boxTransformation(self.universe._spec,
                          pt_in, pt_out, box_size, to_box)

class SubTrajectory:

    """Reference to a subset of a trajectory

    A SubTrajectory object is created by slicing a Trajectory object
    or another SubTrajectory object. It provides all the operations
    defined on Trajectory objects.
    """

    def __init__(self, trajectory, indices):
        self.trajectory = trajectory
        self.indices = indices
        self.universe = trajectory.universe

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.trajectory[self.indices[item]]
        else:
            return SubTrajectory(self.trajectory, self.indices[item])

    def __getslice__(self, first, last):
        return self[(slice(first, last),)]

    def __getattr__(self, name):
        return SubVariable(getattr(self.trajectory, name), self.indices)

    def readParticleTrajectory(self, atom, first=0, last=None, skip=1,
                               variable = "configuration"):
        if last is None:
            last = len(self.indices)
        indices = self.indices[first:last:skip]
        first = indices[0]
        last = indices[-1]+1
        if len(self.indices) > 1:
            skip = self.indices[1]-self.indices[0]
        else:
            skip = 1
        return self.trajectory.readParticleTrajectory(atom, first, last,
                                                      skip, variable)

    def readRigidBodyTrajectory(self, object, first=0, last=None, skip=1,
                                reference = None):
        if last is None:
            last = len(self.indices)
        indices = self.indices[first:last:skip]
        first = indices[0]
        last = indices[-1]+1
        if len(self.indices) > 1:
            skip = self.indices[1]-self.indices[0]
        else:
            skip = 1
        return RigidBodyTrajectory(self.trajectory, object,
                                   first, last, skip, reference)

    def variables(self):
        return self.trajectory.variables()

    def view(self, first=0, last=None, step=1, subset = None):
        Visualization.viewTrajectory(self, first, last, step, subset)

    def close(self):
        del self.trajectory

    def _boxTransformation(self, pt_in, pt_out, to_box=0):
        Trajectory._boxTransformation(self.trajectory, pt_in, pt_out, to_box)

#
# Trajectory variables
#
class TrajectoryVariable:

    """Variable in a trajectory

    A TrajectoryVariable object is created by extracting a variable from
    a Trajectory object if that variable contains data for each atom and
    is thus potentially large. No data is read from the trajectory file
    when a TrajectoryVariable object is created; the read operation
    takes place when the TrajectoryVariable is indexed with a specific
    step number.

    If 't' is a TrajectoryVariable object, then:

    - 'len(t)' is the number of steps

    - 't[i]' is the data for step i, in the form of a ParticleScalar,
      a ParticleVector, or a Configuration object, depending on the
      variable

    - 't[i:j]' and 't[i:j:n]' return a SubVariable object that refers
       to a subset of the total number of steps
    """
    
    def __init__(self, universe, trajectory, name):
        self.universe = universe
        self.trajectory = trajectory
        self.name = name
        self.var = self.trajectory.trajectory.file.variables[self.name]
        if self.name == 'configuration':
            try:
                self.box_size = \
                        self.trajectory.trajectory.file.variables['box_size']
            except KeyError:
                self.box_size = None

    def __len__(self):
        return len(self.trajectory)

    def __getitem__(self, item):
        if not isinstance(item, int):
            return SubVariable(self, Numeric.arange(len(self)))[item]
        if item < 0:
            item = item + len(self.trajectory)
        if item >= len(self.trajectory):
            raise IndexError
        if self.name == 'configuration':
            if self.box_size is None:
                box = None
            elif len(self.box_size.shape) == 3:
                bs = self.trajectory.block_size
                box = self.box_size[item/bs, :, item%bs].astype(Numeric.Float)
            else:
                box = self.box_size[item].astype(Numeric.Float)
            array = ParticleProperties.Configuration(self.universe,
                self.trajectory.trajectory.readParticleVector(self.name, item),
                box)
        elif 'xyz' in self.var.dimensions:
            array = ParticleProperties.ParticleVector(self.universe,
                self.trajectory.trajectory.readParticleVector(self.name, item))
        else:
            array = ParticleProperties.ParticleScalar(self.universe,
                self.trajectory.trajectory.readParticleScalar(self.name, item))
        return array

    def __getslice__(self, first, last):
        return self[(slice(first, last),)]

    def average(self):
        sum = self[0]
        for value in self[1:]:
            sum = sum + value
        return sum/len(self)

class SubVariable(TrajectoryVariable):

    """Reference to a subset of a TrajectoryVariable

    A Glossary:Subclass of Class:MMTK.Trajectory.TrajectoryVariable.

    A SubVariable object is created by slicing a TrajectoryVariable
    object or another SubVariable object. It provides all the operations
    defined on TrajectoryVariable objects.
    """

    def __init__(self, variable, indices):
        self.variable = variable
        self.indices = indices

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.variable[self.indices[item]]
        else:
            return SubVariable(self.variable, self.indices[item])

    def __getslice__(self, first, last):
        return self[(slice(first, last),)]

#
# Trajectory consisting of multiple files
#
class TrajectorySet:

    """Trajectory file set

    A trajectory set permits to treat a sequence of trajectory files
    like a single trajectory for reading data. It behaves like an
    object of the class Class:MMTK.Trajectory.Trajectory. The
    trajectory files must all contain data for the same system.
    The variables stored in the individual files need not be the
    same, but only variables common to all files can be accessed.

    Constructor: TrajectorySet(|object|, |filename_list|)

    Arguments:

    |object| -- the object whose data is stored in the trajectory files.
                This can be (and usually is) 'None';
                in that case, a universe object is constructed from the
                description stored in the first trajectory file. This universe
                object can be accessed via the attribute 'universe'
                of the trajectory set object.

    |filename_list| -- a list of trajectory file names or
                       (filename, first_step, last_step, increment)
                       tuples.


    Note: depending on how the sequence of trajectories was constructed,
    the first configuration of each trajectory might be the same as the
    last one in the preceding trajectory. To avoid counting it twice,
    specify (filename, 1, None, 1) for all but the first trajectory in
    the set.
    """

    def __init__(self, object, filenames):
        first = Trajectory(object, filenames[0])
        if type(first) == type(()):
            first = first[0]
        self.universe = first.universe
        self.trajectories = [first]
        self.nsteps = [0, len(first)]
        self.cell_parameters = []
        for file in filenames[1:]:
            if type(file) == type(()):
                t = Trajectory(self.universe, file[0])[file[1]:file[2]:file[3]]
            else:
                t = Trajectory(self.universe, file)
            self.trajectories.append(t)
            self.nsteps.append(self.nsteps[-1]+len(t))
            try:
                self.cell_parameters.append(t[0]['box_size'])
            except KeyError:
                pass
        vars = {}
        for t in self.trajectories:
            for v in t.variables():
                vars[v] = vars.get(v, 0) + 1
        self.vars = []
        for v, count in vars.items():
            if count == len(self.trajectories):
                self.vars.append(v)

    def close(self):
        for t in self.trajectories:
            t.close()

    def __len__(self):
        return self.nsteps[-1]

    def __getitem__(self, item):
        if not isinstance(item, int):
            return SubTrajectory(self, Numeric.arange(len(self)))[item]
        if item >= len(self):
            raise IndexError
        tindex = Numeric.add.reduce(Numeric.greater_equal(item, self.nsteps))-1
        return self.trajectories[tindex][item-self.nsteps[tindex]]

    def __getslice__(self, first, last):
        return self[(slice(first, last),)]

    def __getattr__(self, name):
        if name not in self.vars:
            raise AttributeError("no variable named " + name)
        var = self.trajectories[0].trajectory.file.variables[name]
        if 'atom_number' in var.dimensions:
            return TrajectorySetVariable(self.universe, self, name)
        else:
            data = []
            for t in self.trajectories:
                var = t.trajectory.file.variables[name]
                data.append(Numeric.ravel(Numeric.array(var))[:len(t)])
            return Numeric.concatenate(data)

    def readParticleTrajectory(self, atom, first=0, last=None, skip=1,
                               variable = "configuration"):
        total = None
        self.steps_read = []
        for i in range(len(self.trajectories)):
            if self.nsteps[i+1] <= first:
                self.steps_read.append(0)
                continue
            if last is not None and self.nsteps[i] >= last:
                break
            n = max(0, (self.nsteps[i]-first+skip-1)/skip)
            start = first+skip*n-self.nsteps[i]
            n = (self.nsteps[i+1]-first+skip-1)/skip
            stop = first+skip*n
            if last is not None:
                stop = min(stop, last)
            stop = stop-self.nsteps[i]
            if start >= 0 and start < self.nsteps[i+1]-self.nsteps[i]:
                t = self.trajectories[i]
                pt = t.readParticleTrajectory(atom, start, stop, skip,
                                              variable)
                self.steps_read.append((stop-start)/skip)
                if total is None:
                    total = pt
                else:
                    if variable == "configuration" \
                       and self.cell_parameters[0] is not None:
                        jump = pt.array[0]-total.array[-1]
                        mult = -(jump/self.cell_parameters[i-1]).astype('i')
                        if len(Numeric.nonzero(mult)) > 0:
                            t._boxTransformation(pt.array, pt.array, 1)
                            Numeric.add(pt.array, mult[Numeric.NewAxis, : ],
                                        pt.array)
                            t._boxTransformation(pt.array, pt.array, 0)
                            jump = pt.array[0] - total.array[-1]
                        mask = Numeric.less(jump,
                                            -0.5*self.cell_parameters[i-1])- \
                               Numeric.greater(jump,
                                               0.5*self.cell_parameters[i-1])
                        if len(Numeric.nonzero(mask)) > 0:
                            t._boxTransformation(pt.array, pt.array, 1)
                            Numeric.add(pt.array, mask[Numeric.NewAxis, :],
                                        pt.array)
                            t._boxTransformation(pt.array, pt.array, 0)
                    elif variable == "box_coordinates" \
                       and self.cell_parameters[0] is not None:
                        jump = pt.array[0]-total.array[-1]
                        mult = -jump.astype('i')
                        if len(Numeric.nonzero(mult)) > 0:
                            Numeric.add(pt.array, mult[Numeric.NewAxis, : ],
                                        pt.array)
                            jump = pt.array[0] - total.array[-1]
                        mask = Numeric.less(jump, -0.5)- \
                               Numeric.greater(jump, 0.5)
                        if len(Numeric.nonzero(mask)) > 0:
                            Numeric.add(pt.array, mask[Numeric.NewAxis, :],
                                        pt.array)
                    total.array = Numeric.concatenate((total.array, pt.array))
            else:
                self.steps_read.append(0)
        return total

    def readRigidBodyTrajectory(self, object, first=0, last=None, skip=1,
                                reference = None):
        return RigidBodyTrajectory(self, object, first, last, skip, reference)

    def _boxTransformation(self, pt_in, pt_out, to_box=0):
        n = 0
        for i in range(len(self.steps_read)):
            t = self.trajectories[i]
            steps = self.steps_read[i]
            if steps > 0:
                t._boxTransformation(pt_in[n:n+steps], pt_out[n:n+steps],
                                     to_box)
            n = n + steps

##      def readRigidBodyTrajectory(self, object, first=0, last=None, skip=1,
##                                  reference = None):
##          total = None
##          for i in range(len(self.trajectories)):
##              if self.nsteps[i+1] <= first:
##                  continue
##              if last is not None and self.nsteps[i] >= last:
##                  break
##              n = max(0, (self.nsteps[i]-first+skip-1)/skip)
##              start = first+skip*n-self.nsteps[i]
##              n = (self.nsteps[i+1]-first+skip-1)/skip
##              stop = first+skip*n
##              if last is not None:
##                  stop = min(stop, last)
##              stop = stop-self.nsteps[i]
##              if start >= 0 and start < self.nsteps[i+1]-self.nsteps[i]:
##                  t = self.trajectories[i]
##                  rbt = t.readRigidBodyTrajectory(object, start, stop, skip,
##                                                  reference)
##                  if total is None:
##                      total = rbt
##                  else:
##                      if self.cell_parameters[0] is not None:
##                          jump = rbt.cms[0]-total.cms[-1]
##                          mask = Numeric.less(jump,
##                                              -0.5*self.cell_parameters[i-1])- \
##                                 Numeric.greater(jump,
##                                                 0.5*self.cell_parameters[i-1])
##                          t._boxTransformation(rbt.cms, rbt.cms, 1)
##                          Numeric.add(rbt.cms, mask[Numeric.NewAxis, :],
##                                      rbt.cms)
##                          t._boxTransformation(rbt.cms, rbt.cms, 0)
##                      total.cms = Numeric.concatenate((total.cms, rbt.cms))
##                      total.quaternions = Numeric.concatenate((total.quaternions,
##                                                               rbt.quaternions))
##                      total.fit = Numeric.concatenate((total.fit, rbt.fit))
##          return total

    def variables(self):
        return self.vars

    def view(self, first=0, last=None, step=1, object = None):
        Visualization.viewTrajectory(self, first, last, step, object)


class TrajectorySetVariable(TrajectoryVariable):

    """Variable in a trajectory set

    A TrajectorySetVariable object is created by extracting a variable from
    a TrajectorySet object if that variable contains data for each atom and
    is thus potentially large. It behaves exactly like a TrajectoryVariable
    object.
    """
    
    def __init__(self, universe, trajectory_set, name):
        self.universe = universe
        self.trajectory_set = trajectory_set
        self.name = name

    def __len__(self):
        return len(self.trajectory_set)

    def __getitem__(self, item):
        if not isinstance(item, int):
            return SubVariable(self, Numeric.arange(len(self)))[item]
        if item >= len(self.trajectory_set):
            raise IndexError
        tindex = Numeric.add.reduce(Numeric.greater_equal(item,
                                         self.trajectory_set.nsteps))-1
        step = item-self.trajectory_set.nsteps[tindex]
        t = self.trajectory_set.trajectories[tindex]
        return getattr(t, self.name)[step]

#
# Cache for atom trajectories
#
class ParticleTrajectoryReader:

    def __init__(self, trajectory):
        self.trajectory = trajectory
        self.natoms = self.trajectory.universe.numberOfAtoms()
        self._trajectory = trajectory.trajectory
        self.cache = {}
        self.cache_lifetime = 2

    def __call__(self, atom, variable, first, last, skip, correct, box):
        if not isinstance(atom, int):
            index = atom.index
        else:
            index = atom
        key = (index, variable, first, last, skip, correct, box)
        data, count = self.cache.get(key, (None, 0))
        if data is not None:
            self.cache[key] = (data, self.cache_lifetime)
            return data
        delete = []
        for k, value in self.cache.items():
            data, count = value
            count = count - 1
            if count == 0:
                delete.append(k)
            else:
                self.cache[k] = (data, count)
        for k in delete:
            del self.cache[k]
        cache_size = min(10, max(1, 100000/max(1, len(self.trajectory))))
        natoms = min(cache_size, self.natoms-index)
        data = self._trajectory.readParticleTrajectories(index, natoms,
                                                         variable,
                                                         first, last, skip,
                                                         correct, box)
        for i in range(natoms):
            key = (index+i, variable, first, last, skip, correct, box)
            self.cache[key] = (data[i], self.cache_lifetime)
        return data[0]

#
# Single-atom trajectory
#
class ParticleTrajectory:

    """Trajectory data for a single particle

    A ParticleTrajectory object is created by calling the method
    'readParticleTrajectory' on a Trajectory object.
    If 'pt' is a ParticleTrajectory object, then

    - 'len(pt)' is the number of steps stored in it

    - 'pt[i]' is the value at step 'i' (a vector)
    """
    
    def __init__(self, trajectory, atom, first=0, last=None, skip=1,
                 variable = "configuration"):
        if last is None:
            last = len(trajectory)
        if variable == "box_coordinates":
            variable = "configuration"
            box = 1
        else:
            box = 0
        reader = trajectory.particle_trajectory_reader
        self.array = reader(atom, variable, first, last, skip,
                            variable == "configuration", box)


    def __len__(self):
        return self.array.shape[0]

    def __getitem__(self, index):
        return Vector(self.array[index])

    def translateBy(self, vector):
        """Adds |vector| to the values at all steps. This does *not*
        change the data in the trajectory file."""
        Numeric.add(self.array, vector.array[Numeric.NewAxis, :], self.array)

#
# Rigid-body trajectory
#
class RigidBodyTrajectory:

    """Rigid-body trajectory data

    A RigidBodyTrajectory object is created by calling the method
    'readRigidBodyTrajectory' on a Trajectory object.
    If 'rbt' is a RigidBodyTrajectory object, then

    - 'len(rbt)' is the number of steps stored in it

    - 'rbt[i]' is the value at step 'i' (a vector for the center of mass
               and a quaternion for the orientation)
    """
    
    def __init__(self, trajectory, object, first=0, last=None, skip=1,
                 reference = None):
        self.trajectory = trajectory
        universe = trajectory.universe
        if last is None: last = len(trajectory)
        first_conf = trajectory.configuration[first]
        offset = universe.contiguousObjectOffset([object], first_conf, 1)
        if reference is None:
            reference = first_conf
        reference = universe.contiguousObjectConfiguration([object],
                                                           reference)
        steps = (last-first+skip-1)/skip
        mass = object.mass()
        ref_cms = object.centerOfMass(reference)
        atoms = object.atomList()

        possq = Numeric.zeros((steps,), Numeric.Float)
        cross = Numeric.zeros((steps, 3, 3), Numeric.Float)
        rcms = Numeric.zeros((steps, 3), Numeric.Float)

        # cms of the CONTIGUOUS object made of CONTINUOUS atom trajectories 
        for a in atoms:
            r = trajectory.readParticleTrajectory(a, first, last, skip,
                                                  "box_coordinates").array
            w = a._mass/mass
            Numeric.add(rcms, w*r, rcms)
            if offset is not None:
                Numeric.add(rcms, w*offset[a].array, rcms)
        
        # relative coords of the CONTIGUOUS reference
        r_ref = Numeric.zeros((len(atoms), 3), Numeric.Float)
        for a in range(len(atoms)):
            r_ref[a] = atoms[a].position(reference).array - ref_cms.array

        # main loop: storing data needed to fill M matrix 
        for a in range(len(atoms)):
            r = trajectory.readParticleTrajectory(atoms[a],
                                                  first, last, skip,
                                                  "box_coordinates").array
            r = r - rcms # (a-b)**2 != a**2 - b**2
            if offset is not None:
                Numeric.add(r, offset[atoms[a]].array,r)
            trajectory._boxTransformation(r, r)
            w = atoms[a]._mass/mass
            Numeric.add(possq, w*Numeric.add.reduce(r*r, -1), possq)
            Numeric.add(possq, w*Numeric.add.reduce(r_ref[a]*r_ref[a],-1),
                        possq)
            Numeric.add(cross, w*r[:,:,Numeric.NewAxis]*r_ref[Numeric.NewAxis,
                                                              a,:],cross)
        self.trajectory._boxTransformation(rcms, rcms)

        # filling matrix M (formula no 40)
        k = Numeric.zeros((steps, 4, 4), Numeric.Float)
        k[:, 0, 0] = -cross[:, 0, 0]-cross[:, 1, 1]-cross[:, 2, 2]
        k[:, 0, 1] = cross[:, 1, 2]-cross[:, 2, 1]
        k[:, 0, 2] = cross[:, 2, 0]-cross[:, 0, 2]
        k[:, 0, 3] = cross[:, 0, 1]-cross[:, 1, 0]
        k[:, 1, 1] = -cross[:, 0, 0]+cross[:, 1, 1]+cross[:, 2, 2]
        k[:, 1, 2] = -cross[:, 0, 1]-cross[:, 1, 0]
        k[:, 1, 3] = -cross[:, 0, 2]-cross[:, 2, 0]
        k[:, 2, 2] = cross[:, 0, 0]-cross[:, 1, 1]+cross[:, 2, 2]
        k[:, 2, 3] = -cross[:, 1, 2]-cross[:, 2, 1]
        k[:, 3, 3] = cross[:, 0, 0]+cross[:, 1, 1]-cross[:, 2, 2]
        del cross
        for i in range(1, 4):
            for j in range(i):
                k[:, i, j] = k[:, j, i]
        Numeric.multiply(k, 2., k)
        for i in range(4):
            Numeric.add(k[:,i,i], possq, k[:,i,i])
        del possq

        quaternions = Numeric.zeros((steps, 4), Numeric.Float)
        fit = Numeric.zeros((steps,), Numeric.Float)
        from Scientific.LA import eigenvectors
        for i in range(steps):
            e, v = eigenvectors(k[i])
            j = Numeric.argmin(e)
            if e[j] < 0.:
                fit[i] = 0.
            else:
                fit[i] = Numeric.sqrt(e[j])
            if v[j,0] < 0.: quaternions[i] = -v[j] # eliminate jumps
            else: quaternions[i] = v[j]
        self.fit = fit
        self.cms = rcms
        self.quaternions = quaternions

    def __len__(self):
        return self.cms.shape[0]

    def __getitem__(self, index):
        from Scientific.Geometry.Quaternion import Quaternion
        return Vector(self.cms[index]), Quaternion(self.quaternions[index])

#
# Type check for trajectory objects
#
def isTrajectory(object):
    "Returns 1 if |object| is a trajectory."
    import MMTK_trajectory
    return type(object) == MMTK_trajectory.trajectory_type or \
           (type(object) == types.InstanceType and
            object.__class__ == Trajectory)

#
# Base class for all objects that generate trajectories
#
class TrajectoryGenerator:

    def __init__(self, universe, options):
        self.universe = universe
        self.options = options

    def setCallOptions(self, options):
        self.call_options = options

    def getActions(self):
        try:
            self.actions = self.getOption('actions')
        except ValueError:
            self.actions = []
        try:
            steps = self.getOption('steps')
        except ValueError:
            steps = None
        return map(lambda a, t=self, s=steps: a.getSpecificationList(t, s),
                   self.actions)

    def cleanupActions(self):
        for a in self.actions:
            a.cleanup()

    def getOption(self, option):
        try:
            value = self.call_options[option]
        except KeyError:
            try:
                value = self.options[option]
            except KeyError:
                try:
                    value = self.default_options[option]
                except KeyError:
                    raise ValueError('undefined option: ' + option)
        return value

    def optionString(self, options):
        s = ''
        for o in options:
            s = s + o + '=' + `self.getOption(o)` + ', '
        return s[:-2]

#
# Trajectory action base class
#
class TrajectoryAction:

    def __init__(self, first, last, skip):
        self.first = first
        self.last = last
        self.skip = skip

    spec_type = 'function'

    def _getSpecificationList(self, trajectory_generator, steps):
        first = self.first
        last = self.last
        if first < 0:
            first = first + steps
        if last is None:
            import MMTK_trajectory
            last = MMTK_trajectory.maxint
        elif last < 0:
            last = last + steps+1
        return (self.spec_type, first, last, self.skip)

    def getSpecificationList(self, trajectory_generator, steps):
        return self._getSpecificationList(trajectory_generator, steps) \
               + (self.Cfunction, self.parameters)

    def cleanup(self):
        pass

class TrajectoryOutput(TrajectoryAction):

    """Trajectory output action

    A TrajectoryOutput object is used in the action list of any
    trajectory-generating operation. It writes any of the available
    data to a trajectory file. It is possible to use several
    TrajectoryOutput objects at the same time in order to produce
    multiple trajectories from a single run.

    Constructor: TrajectoryOutput(|trajectory|, |data|=None,
                                  |first|=0, |last|=None, |skip|=1)

    Arguments:

    |trajectory| -- a trajectory object or a string, which is interpreted
                    as the name of a file that is opened as a trajectory
                    in append mode

    |data| -- a list of data categories. All variables provided by the
              trajectory generator that fall in any of the listed categories
              are written to the trajectory file. See the descriptions of
              the trajectory generators for a list of variables and
              categories. By default (|data| = 'None') the categories
              "configuration", "energy", "thermodynamic", and "time"
              are written.

    |first| -- the number of the first step at which the action is executed

    |last| -- the number of the last step at which the action is executed.
              A value of 'None' indicates that the action should be
              executed indefinitely.

    |skip| -- the number of steps to skip between two applications of the
              action
    """

    def __init__(self, destination, categories = None,
                 first=0, last=None, skip=1):
        TrajectoryAction.__init__(self, first, last, skip)
        self.destination = destination
        self.categories = categories
        self.must_be_closed = None

    spec_type = 'trajectory'

    def getSpecificationList(self, trajectory_generator, steps):
        if type(self.destination) == type(''):
            destination = self._setupDestination(self.destination,
                                                 trajectory_generator.universe)
        else:
            destination = self.destination
        if self.categories is None:
            categories = self._defaultCategories(trajectory_generator)
        else:
            if self.categories == 'all' or self.categories == ['all']:
                categories = trajectory_generator.available_data
            else:
                categories = self.categories
                for item in categories:
                    if item not in trajectory_generator.available_data:
                        raise ValueError('data item %s is not available' % item)
        return self._getSpecificationList(trajectory_generator, steps) \
               + (destination, categories)

    def _setupDestination(self, destination, universe):
        self.must_be_closed = Trajectory(universe, destination, 'a')
        return self.must_be_closed
        
    def cleanup(self):
        if self.must_be_closed is not None:
            self.must_be_closed.close()

    def _defaultCategories(self, trajectory_generator):
        available = trajectory_generator.available_data
        return tuple(filter(lambda x, a=available: x in a, self.default_data))

    default_data = ['configuration', 'energy', 'thermodynamic', 'time']

class RestartTrajectoryOutput(TrajectoryOutput):

    """Restart trajectory output action

    A RestartTrajectoryOutput object is used in the action list of any
    trajectory-generating operation. It writes those variables to a
    trajectory that the trajectory generator declares as necessary
    for restarting.

    Constructor: RestartTrajectoryOutput(|trajectory|, |skip|=100, |length|=3)

    Arguments:

    |trajectory| -- a trajectory object or a string, which is interpreted
                    as the name of a file that is opened as a trajectory
                    in append mode with a cycle length of |length| and
                    double-precision variables

    |skip| -- the number of steps between two write operations to the
              restart trajectory

    |length| -- the number of steps stored in the restart trajectory;
                used only if |trajectory| is a string
    """

    def __init__(self, trajectory, skip=100, length=3):
        TrajectoryAction.__init__(self, 0, None, skip)
        self.destination = trajectory
        self.categories = None
        self.length = length

    def _setupDestination(self, destination, universe):
        self.must_be_closed = Trajectory(universe, destination, 'a',
                                         'Restart trajectory', 1, self.length)
        return self.must_be_closed
        
    def _defaultCategories(self, trajectory_generator):
        if trajectory_generator.restart_data is None:
            raise ValueError("Trajectory generator does not permit restart")
        return trajectory_generator.restart_data

class LogOutput(TrajectoryOutput):

    """Protocol file output action

    A LogOutput object is used in the action list of any
    trajectory-generating operation. It writes any of the available
    data to a text file.

    Constructor: LogOutput(|file|, |data|, |first|=0, |last|=None, |skip|=1)

    Arguments:

    |file| -- a file object or a string, which is interpreted as the name
              of a file that is opened in write mode

    |data| -- a list of data categories. All variables provided by the
              trajectory generator that fall in any of the listed categories
              are written to the trajectory file. See the descriptions of
              the trajectory generators for a list of variables and
              categories. By default (|data| = 'None') the categories
              "energy" and "time" are written.

    |first| -- the number of the first step at which the action is executed

    |last| -- the number of the last step at which the action is executed.
              A value of 'None' indicates that the action should be
              executed indefinitely.

    |skip| -- the number of steps to skip between two applications of the
              action
    """

    def _setupDestination(self, destination, universe):
        self.must_be_closed = open(destination, 'w')
        return self.must_be_closed

    spec_type = 'print'

    default_data = ['energy', 'time']

class StandardLogOutput(LogOutput):

    """Standard protocol output action

    A StandardLogOutput object is used in the action list of any
    trajectory-generating operation. It is a specialization of
    LogOutput to the most common case and writes data in the categories
    "time" and "energy" to the standard output stream.

    Constructor: StandardLogOutput(|skip|=50)

    Arguments:

    |skip| -- the number of steps to skip between two applications of the
              action
    """

    def __init__(self, skip=50):
        LogOutput.__init__(self, sys.stdout, None, 0, None, skip)

#
# Snapshot generator
#
class SnapshotGenerator(TrajectoryGenerator):

    """Trajectory generator for single steps

    A SnapshotGenerator is used for manual assembly of trajectory
    files. At each call it writes one step to the trajectory,
    using the current state of the universe (configuration, velocities, etc.)
    and data provided explicitly with the call.

    Constructor: SnapshotGenerator(|universe|, |**options|)

    Arguments:

    |universe| -- the universe on which the integrator acts

    |options| -- keyword options:

      * data: a dictionary that supplies values for variables
              that are not part of the universe state (e.g. potential energy)
      * actions: a list of actions to be executed periodically (default is
                 none)

    Each call to the SnapshotGenerator object produces one step.
    All the keyword options listed above can be specified either when
    creating the generator or when calling it.
    """

    def __init__(self, universe, **options):
        TrajectoryGenerator.__init__(self, universe, options)
        self.available_data = []
        try:
            e, g = self.universe.energyAndGradients()
        except: pass
        else:
            self.available_data.append('energy')
            self.available_data.append('gradients')
        try:
            self.universe.configuration()
            self.available_data.append('configuration')
        except: pass
        if self.universe.cellVolume() is not None:
            self.available_data.append('thermodynamic')
        if self.universe.velocities() is not None:
            self.available_data.append('velocities')
            self.available_data.append('energy')
            self.available_data.append('thermodynamic')

    default_options = {'steps': 0, 'actions': []}

    def __call__(self, **options):
        self.setCallOptions(options)
        from MMTK_trajectory import snapshot
        data = copy.copy(options.get('data', {}))
        energy_terms = 0
        for name in data.keys():
            if name == 'time' and 'time' not in self.available_data:
                self.available_data.append('time')
            if  name[-7:] == '_energy':
                energy_terms = energy_terms + 1
                if 'energy' not in self.available_data:
                    self.available_data.append('energy')
            if (name == 'temperature' or name == 'pressure') \
               and 'thermodynamic' not in self.available_data:
                self.available_data.append('thermodynamic')
            if name == 'gradients' and 'gradients' not in self.available_data:
                self.available_data.append('gradients')
        actions = self.getActions()
        for action in actions:
            categories = action[-1]
            for c in categories:
                if c == 'energy' and not data.has_key('kinetic_energy'):
                    v = self.universe.velocities()
                    if v is not None:
                        m = self.universe.masses()
                        e = (v*v*m*0.5).sumOverParticles()
                        data['kinetic_energy'] = e
                        df = self.universe.degreesOfFreedom()
                        data['temperature'] = 2.*e/df/Units.k_B/Units.K
                if c == 'configuration':
                    if  data.has_key('configuration'):
                        data['configuration'] = data['configuration'].array
                    else:
                        data['configuration'] = \
                                         self.universe.configuration().array
                if c == 'velocities':
                    if  data.has_key('velocities'):
                        data['velocities'] = data['velocities'].array
                    else:
                        data['velocities'] = self.universe.velocities().array
                if c == 'gradients':
                    if  data.has_key('gradients'):
                        data['gradients'] = data['gradients'].array
                p = self.universe.cellParameters()
                if p is not None:
                    data['box_size'] = p
                volume = self.universe.cellVolume()
                if volume is not None:
                    data['volume'] = volume
                try:
                    m = self.universe.masses()
                    data['masses'] = m.array
                except: pass
        snapshot(self.universe, data, actions, energy_terms)

#
# Trajectory reader (not yet functional...)
#
class TrajectoryReader(TrajectoryGenerator):

    def __init__(self, trajectory, options):
        TrajectoryGenerator.__init__(self, trajectory.universe, options)
        self.input = trajectory
        self.available_data = trajectory.variables()

    default_options = {'trajectory': None, 'log': None, 'options': []}

    def __call__(self, **options):
        self.setCallOptions(options)
        from MMTK_trajectory import readTrajectory
        readTrajectory(self.universe, self.input.trajectory,
                       [self.getOption('trajectory'),
                        self.getOption('log')] +
                       self.getOption('options'))

#
# Print information about trajectory file
#
def trajectoryInfo(filename):
    """Return a string with summarial information about the trajectory
    file identified by |filename|."""
    from Scientific.IO import NetCDF
    file = NetCDF.NetCDFFile(filename, 'r')
    nsteps = file.variables['step'].shape[0]
    if 'minor_step_number' in file.dimensions.keys():
        nsteps = nsteps*file.variables['step'].shape[1]
    s = 'Information about trajectory file ' + filename + ':\n'
    try:
        s = s + file.comment + '\n'
    except AttributeError:
        pass
    s = s + `file.dimensions['atom_number']` + ' atoms\n'
    s = s +  `nsteps` + ' steps\n'
    s = s +  file.history
    file.close()
    return s
