#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Reduce grid data to a smaller size by averaging over cells of specified
# size and write the output as a netcdf file.  xyz_origin and xyz_step
# attributes are adjusted.
#
# Syntax: downsize.py [-t ave|max|maxmag|median|min|sample]
#                     <x-cell-size> <y-cell-size> <z-cell-size>
#                     <in-file> <netcdf-out-file>
#
import sys

from VolumeData import Grid_Data

# -----------------------------------------------------------------------------
#
def downsize(mode, cell_size, inpath, outpath):

  from VolumeData import fileformats
  try:
    glist = fileformats.open_file(inpath)
  except fileformats.Unknown_File_Type, e:
    sys.stderr.write(str(e))
    sys.exit(1)
    
  reduced = [Reduced_Grid(g, mode, cell_size) for g in glist]

  from VolumeData.netcdf import write_grid_as_netcdf
  write_grid_as_netcdf(reduced, outpath)

# -----------------------------------------------------------------------------
# Average over cells to produce reduced size grid object.
#
# If the grid data sizes are not multiples of the cell size then the
# final data values along the dimension are not included in the reduced
# data (ie ragged blocks are not averaged).
#
class Reduced_Grid(Grid_Data):
  
  def __init__(self, grid_data, mode, cell_size):

    self.grid_data = grid_data
    self.mode = mode
    self.cell_size = cell_size

    size = map(lambda s, cs: s / cs, grid_data.size, cell_size)
    if mode == 'sample':
      xyz_origin = grid_data.origin
    else:
      xyz_origin = map(lambda a,b,c: a + b*0.5*(c-1),
                       grid_data.origin, grid_data.step, cell_size)
    xyz_step = map(lambda step, cs: step*cs, grid_data.step, cell_size)
    value_type = grid_data.value_type
    
    Grid_Data.__init__(self, size, value_type, xyz_origin, xyz_step)
    
  # ---------------------------------------------------------------------------
  #
  def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

    ijk_full_origin = map(lambda i, cs: i * cs, ijk_origin, self.cell_size)
    ijk_full_size = map(lambda s, cs: s*cs, ijk_size, self.cell_size)
    values = self.grid_data.matrix(ijk_full_origin, ijk_full_size,
                                   progress = progress)

    mode = self.mode
    if mode == 'ave':
      m = average_down(values, self.cell_size)
    elif mode == 'max':
      from numpy import maximum
      m = max_or_min_over_cells(values, maximum, self.cell_size)
    elif mode == 'maxmag':
      m = maxmag_over_cells(values, self.cell_size)
    elif mode == 'median':
      m = cell_medians(values, self.cell_size)
    elif mode == 'min':
      from numpy import minimum
      m = max_or_min_over_cells(values, minimum, self.cell_size)
    elif mode == 'sample':
      istep, jstep, kstep = cell_size
      m = values[::kstep,::jstep,::istep]

    ist,jst,kst = ijk_step
    m = m[::kst,::jst,::ist]

    return m
  
# ---------------------------------------------------------------------------
#
def average_down(values, cell_size):

  istep, jstep, kstep = cell_size
  rshape = values[::kstep,::jstep,::istep].shape
  from numpy import zeros, float, add, multiply
  reduced = zeros(rshape, float)
  
  for ko in range(kstep):
    for jo in range(jstep):
      for io in range(istep):
        add(reduced, values[ko::kstep,jo::jstep,io::istep], reduced)

  scale = 1.0 / (istep * jstep * kstep)
  multiply(reduced, scale, reduced)

  return reduced.astype(values.dtype)
    
# ---------------------------------------------------------------------------
#
def max_or_min_over_cells(values, max_or_min, cell_size):

  istep, jstep, kstep = cell_size
  from numpy import array
  reduced = array(values[::kstep,::jstep,::istep])
  
  for ko in range(kstep):
    for jo in range(jstep):
      for io in range(istep):
        subgrid = values[ko::kstep,jo::jstep,io::istep]
        max_or_min(reduced, subgrid, reduced)
        
  return reduced
    
# ---------------------------------------------------------------------------
#
def maxmag_over_cells(values, cell_size):

  from numpy import maximum, minimum, absolute, greater, where
  cmax = max_or_min_over_cells(values, maximum, cell_size)
  cmin = max_or_min_over_cells(values, minimum, cell_size)
  acmin = absolute(cmin)
  min_bigger = greater(acmin, cmax)
  reduced = where(min_bigger, cmin, cmax)
  return reduced
  
# ---------------------------------------------------------------------------
#
def cell_medians(values, cell_size):

  istep, jstep, kstep = cell_size
  ksize, jsize, isize = values.shape
  rshape = values[::kstep,::jstep,::istep].shape
  from numpy import zeros, ravel, sort
  median = zeros(rshape, values.dtype)
  
  for k in range(0,ksize,kstep):
    for j in range(0,jsize,jstep):
      for i in range(0,isize,istep):
        cv = ravel(values[k:k+kstep,j:j+jstep,i:i+istep])
        median[k/kstep,j/jstep,i/istep] = sort(cv)[len(cv)/2]

  return median
    
# -----------------------------------------------------------------------------
#
def parse_command_line(argv):

  args = list(argv)

  mode = 'sample'               # Default
  if '-t' in args:
    a = args.index('-t')
    if a+1 >= len(args):
      syntax()
    mode = args[a+1]
    if not (mode in ('ave', 'max', 'maxmag', 'median', 'min', 'sample')):
      syntax()
    del args[a:a+2]
    
  if len(args) != 6:
    syntax()

  try:
    cell_size = map(int, args[1:4])
  except ValueError:
    syntax()
    
  inpath = args[4]
  outpath = args[5]

  return mode, cell_size, inpath, outpath
    
# -----------------------------------------------------------------------------
#
def syntax():

  msg = ('Reduce the size of a grid file by taking the average, ' +
         'maximum, minimum,\n' +
         'or signed value of maximum magnitude over cells.  ' +
         'The default mode is average.\n' +
         'Produces a netcdf output file.\n' +
         'Syntax: downsize.py [-t ave|max|maxmag|median|min|sample]\n' +
         '                    <x-cell-size> <y-cell-size> <z-cell-size>\n' +
         '                    <in-file> <netcdf-out-file>\n')
  sys.stderr.write(msg)
  sys.exit(1)
    
# -----------------------------------------------------------------------------
#
mode, cell_size, in_path, out_path = parse_command_line(sys.argv)

downsize(mode, cell_size, in_path, out_path)
