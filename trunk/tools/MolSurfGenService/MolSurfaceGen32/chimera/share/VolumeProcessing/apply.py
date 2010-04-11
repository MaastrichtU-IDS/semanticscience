#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Apply a function to a grid pointwise.
# The resulting volume is written in netcdf format.
#
# Syntax: apply.py sqrt|square|abs|exp|log <infile> <outfile>
#
# The file type must be one of the types handled by VolumeData.
#
import sys

from VolumeData import Grid_Data

# -----------------------------------------------------------------------------
#
def apply_function(array_func, inpath, outpath):

  from VolumeData import fileformats
  try:
    grids = fileformats.open_file(inpath)
  except fileformats.Unknown_File_Type, e:
    sys.stderr.write(str(e))
    sys.exit(1)

  fvalues = [Mapped_Grid(g, array_func) for g in grids]

  from VolumeData.netcdf import write_grid_as_netcdf
  write_grid_as_netcdf(fvalues, outpath)

# -----------------------------------------------------------------------------
#
class Mapped_Grid(Grid_Data):
  
  def __init__(self, grid_data, array_func):

    self.array_func = array_func
    Grid_Data.__init__(self, grid_data.size, grid_data.value_type,
                       grid_data.origin, grid_data.step,
                       name = grid_data.name, default_color = grid_data.rgba)
    
  # ---------------------------------------------------------------------------
  #
  def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

    data = self.component.matrix(ijk_origin, ijk_size, ijk_step, progress)
    fvalues = self.array_func(data)
    return fvalues

# -----------------------------------------------------------------------------
#
def syntax():
  
  msg = ('Apply a function to a grid pointwise.\n' +
         'The resulting volume is written in netcdf format.\n'
         'Syntax: apply.py sqrt|square|abs|exp|log <infile> <outfile>\n')
  sys.stderr.write(msg)
  sys.exit(1)

# -----------------------------------------------------------------------------
#
if len(sys.argv) != 4:
  syntax()

fname = sys.argv[1]
from numpy import sqrt, power, absolute, exp, log
if fname == 'sqrt':
  array_func = sqrt
elif fname == 'square':
  array_func = lambda a: power(a, 2)
elif fname == 'abs':
  array_func = absolute
elif fname == 'exp':
  array_func = exp
elif fname == 'log':
  array_func = log
else:
  syntax()
  
inpath = sys.argv[2]
outpath = sys.argv[3]

apply_function(array_func, inpath, outpath)
