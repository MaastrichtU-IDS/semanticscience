# This class provides access to selected data from a trajectory
# via an interface that can be accessed remotely by Pyro. It
# can be used by programs that wish to inspect a trajectory that
# resides on a different machine.
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

from Scientific.IO.NetCDF import NetCDFFile
from Scientific import N as Numeric

class TrajectoryInspector:

    def __init__(self, filename):
        self.filename = filename
        self.file = NetCDFFile(self.filename, 'r')
        try:
            self.block_size = self.file.dimensions['minor_step_number']
        except KeyError:
            self.block_size = 1
        self._countSteps()

    def close(self):
        self.file.close()

    def reopen(self):
        self.file.close()
        self.file = NetCDFFile(self.filename, 'r')
        self._countSteps()

    def _countSteps(self):
        if self.block_size == 1:
            self.nsteps = self.file.variables['step'].shape[0]
        else:
            blocks = self.file.variables['step'].shape[0]
            last_block = self.file.variables['step'][blocks-1]
            unused = Numeric.sum(Numeric.equal(last_block, -2147483647))
            self.nsteps = blocks*self.block_size-unused

    def comment(self):
        try:
            return self.file.comment
        except AttributeError:
            return ''

    def history(self):
        try:
            return self.file.history
        except AttributeError:
            return ''

    def description(self):
        return self.file.variables['description'][:].tostring()

    def numberOfAtoms(self):
        return self.file.dimensions['atom_number']

    def numberOfSteps(self):
        return self.nsteps

    def variableNames(self):
        return self.file.variables.keys()

    def readScalarVariable(self, name, first=0, last=None, step=1):
        if last is None:
            last = self.nsteps
        variable = self.file.variables[name]
        if self.block_size > 1:
            variable = Numeric.ravel(variable[:, :])
        return variable[first:last:step]

    def readConfiguration(self, index):
        if self.block_size == 1:
            try:
                cell = self.file.variables['box_size'][index]
            except KeyError:
                cell = None
            return cell, self.file.variables['configuration'][index]
        else:
            i1 = index / self.block_size
            i2 = index % self.block_size
            try:
                cell = self.file.variables['box_size'][i1, :, i2]
            except KeyError:
                cell = None
            return cell, self.file.variables['configuration'][i1, :, :, i2]
