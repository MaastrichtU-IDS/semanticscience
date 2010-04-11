#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Count the neighbors of each matrix element that have lesser value.
# The 26 neighbors in the 3 by 3 by 3 cube centered at an element are examined.
# The count is shifted by -13 so that 0 represents an equal number of neighbors
# of greater and lesser value.
# The resulting volume is written in netcdf format.
#
# The purpose of this is to find ridges and valleys in data.  A ridge point
# is where most neighbors are below.  A valley is where most neighbors are
# above.
#
# Syntax: ridges.py <infile> <outfile>
#
# The file type must be one of the types handled by VolumeData.
#
import sys

from VolumeData import Grid_Data

# -----------------------------------------------------------------------------
#
def count_neighbors(inpath, outpath):

  from VolumeData import fileformats
  try:
    glist = fileformats.open_file(inpath)
  except fileformats.Unknown_File_Type, e:
    sys.stderr.write(str(e))
    sys.exit(1)

  counts = [Lower_Neighbor_Counts(g) for g in glist]

  from VolumeData.netcdf import write_grid_as_netcdf
  write_grid_as_netcdf(counts, outpath)

# -----------------------------------------------------------------------------
#
class Lower_Neighbor_Counts(Grid_Data):
  
  def __init__(self, grid_data):

    from numpy import int8
    size = map(lambda s: s-2, grid_data.size)
    xyz_origin = map(lambda o, s: o + s,
                     grid_data.origin, grid_data.step)
    Grid_Data.__init__(self, size, int8, xyz_origin, grid_data.step,
                       default_color = grid_data.rgba)
    
  # ---------------------------------------------------------------------------
  #
  def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

    ijk_size_plus_2 = map(lambda i: i+2, ijk_size)
    data = self.grid_data.matrix(ijk_origin, ijk_size_plus_2,
                                 progress = progress)
    counts = count_lower_neighbors(data)
    ist, jst, kst = ijk_step
    m = counts[::kst,::jst,::ist]
    return m

# -----------------------------------------------------------------------------
#
def count_lower_neighbors(data):

  size_minus_2 = map(lambda s: s-2, data.shape)
  from numpy import zeros, int, greater, add, subtract, int8
  compare = zeros(size_minus_2, int)
  count = zeros(size_minus_2, int)

  offsets = ((-1,-1,-1), (-1,-1,0), (-1,-1,1),
             (-1,0,-1), (-1,0,0), (-1,0,1),
             (-1,1,-1), (-1,1,0), (-1,1,1),
             (0,-1,-1), (0,-1,0), (0,-1,1),
             (0,0,-1), (0,0,1),
             (0,1,-1), (0,1,0), (0,1,1),
             (1,-1,-1), (1,-1,0), (1,-1,1),
             (1,0,-1), (1,0,0), (1,0,1),
             (1,1,-1), (1,1,0), (1,1,1))
             
  xsize, ysize, zsize = data.shape
  for xo, yo, zo in offsets:
    greater(data[1:-1,1:-1,1:-1],
            data[xo+1:xsize-1+xo,yo+1:ysize-1+yo,zo+1:zsize-1+zo],
            compare)
    add(compare, count, count)

  subtract(count, 13, count)
  
  return count.astype(int8)

# -----------------------------------------------------------------------------
#
if len(sys.argv) != 3:
  msg = ('Count the neighbors of each volume element ' +
         'that have lesser value.\n' +
         'The 26 neighbors in the 3 by 3 by 3 cube centered ' +
         'at an element are examined.\n' +
         'The count is shifted by -13 so 0 represents ' +
         'an equal number of neighbors of\n' +
         'greater and lesser value. ' +
         'The resulting volume is written in netcdf format.\n' +
         'Syntax: ridges.py <infile> <outfile>\n')
  sys.stderr.write(msg)
  sys.exit(1)

inpath = sys.argv[1]
outpath = sys.argv[2]

count_neighbors(inpath, outpath)
