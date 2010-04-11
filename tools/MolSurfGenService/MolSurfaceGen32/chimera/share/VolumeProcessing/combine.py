#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Combine two grid data files by adding, subtracting or multiplying pointwise
# and write the result as a netcdf file.
#
# Syntax: combine.py add|subtract|multiply <infile1> <infile2> <outfile>
#
# The input file types must be among those handled by VolumeData.
#
import sys

from VolumeData import Grid_Data

# -----------------------------------------------------------------------------
#
def combine_grids(mode, inpath1, inpath2, outpath):

  from VolumeData import fileformats

  grids = []
  failed_paths = []
  for path in (inpath1, inpath2):
    try:
      glist = fileformats.open_file(path)
      grids.append(glist)
    except fileformats.Unknown_File_Type:
      failed_paths.append(path)

  if failed_paths:
    warning = fileformats.suffix_warning(failed_paths)
    sys.stderr.write(warning)
    sys.exit(1)

  combined = map(lambda g1,g2: Combined_Grid(mode, g1, g2), grids[0], grids[1])

  from VolumeData.netcdf import write_grid_as_netcdf
  write_grid_as_netcdf(combined, outpath)

# -----------------------------------------------------------------------------
#
class Combined_Grid(Grid_Data):
  
  def __init__(self, mode, grid_data_1, grid_data_2):

    if grid_data_1.size != grid_data_2.size:
      sys.stderr.write('Grid sizes %s %s differ\n'
                       % (str(grid_data_1.size), str(grid_data_2.size)))
      sys.exit(1)

    self.mode = mode
    self.grid_data_1 = grid_data_1
    self.grid_data_2 = grid_data_2
    
    Grid_Data.__init__(self, grid_data_1.size, grid_data_1.value_type,
                       grid_data_1.origin, grid_data_1.step,
                       default_color = grid_data_1.rgba)
    
  # ---------------------------------------------------------------------------
  #
  def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

    matrix1 = self.grid_data_1.matrix(ijk_origin, ijk_size, ijk_step, progress)
    matrix2 = self.grid_data_2.matrix(ijk_origin, ijk_size, ijk_step, progress)
    from numpy import add, subtract, multiply
    if mode == 'add':
      combined = add(matrix1, matrix2)
    elif mode == 'subtract':
      combined = subtract(matrix1, matrix2)
    elif mode == 'multiply':
      combined = multiply(matrix1, matrix2)
    return combined

# -----------------------------------------------------------------------------
#
def syntax():
  
  msg = ('Add, subtract or multiply two grid data files pointwise\n' +
         'and write the result as a netcdf file.\n' + 
         'Syntax: combine.py add|subtract|multiply ' +
         '<infile1> <infile2> <outfile>\n')
  sys.stderr.write(msg)
  sys.exit(1)

# -----------------------------------------------------------------------------
#
if len(sys.argv) != 5:
  syntax()

mode = sys.argv[1]
if not (mode in ('add', 'subtract', 'multiply')):
  syntax()
  
inpath1 = sys.argv[2]
inpath2 = sys.argv[3]
outpath = sys.argv[4]

combine_grids(mode, inpath1, inpath2, outpath)
