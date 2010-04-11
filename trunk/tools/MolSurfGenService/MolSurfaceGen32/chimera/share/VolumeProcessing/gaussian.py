#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Convolve a Gaussian with data file and write the result as a netcdf file.
# The linewidth is specified in xyz space units and spans -1 SD to +1 SD.
#
# Syntax: gaussian.py <infile> <linewidth> <outfile>
#
# The file type must be one of the types handled by VolumeData.
#
import sys

from VolumeData import Grid_Data

# -----------------------------------------------------------------------------
#
def gaussian_convolve(inpath, linewidth, outpath):

  from VolumeData import fileformats
  try:
    glist = fileformats.open_file(inpath)
  except fileformats.Unknown_File_Type, e:
    sys.stderr.write(str(e))
    sys.exit(1)

  gaussian_data = [Gaussian_Convolution(g, linewidth) for g in glist]

  from VolumeData.netcdf import write_grid_as_netcdf
  write_grid_as_netcdf(gaussian_data, outpath)

# -----------------------------------------------------------------------------
# Convolve a grid with a Gaussian.  Linewidth is specified in xyz units
# (not ijk indices).
#
class Gaussian_Convolution(Grid_Data):
  
  def __init__(self, grid_data, linewidth):

    self.grid_data = grid_data
    self.linewidth = linewidth
    
    Grid_Data.__init__(self, grid_data.size,
                       origin = grid_data.origin, step = grid_data.step)
    
  # ---------------------------------------------------------------------------
  #
  def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

    data = self.full_matrix()
    return self.matrix_slice(data, ijk_origin, ijk_size, ijk_step)
    
  # ---------------------------------------------------------------------------
  #
  def full_matrix(self):

    ijk_origin = (0,0,0)
    ijk_size = self.size
    values = self.grid_data.matrix(ijk_origin, ijk_size)

    ijk_linewidths = map(lambda step, lw=self.linewidth: lw / step,
                         self.step)
    gvalues = gaussian_convolution(values, ijk_linewidths)
    return gvalues

# -----------------------------------------------------------------------------
#
def gaussian_convolution(data, ijk_linewidths):

  from numpy import float32, zeros, add, divide, outer, reshape
  if data.dtype.type != float32:
    data = data.astype(float32)

  from math import exp
  gaussians = []
  for a in range(3):
    size = data.shape[a]
    gaussian = zeros((size,), float32)
    hw = ijk_linewidths[2-a] / 2.0
    for i in range(size):
      u = min(i,size-i) / hw
      p = min(u*u/2, 100)               # avoid OverflowError with exp()
      gaussian[i] = exp(-p)
    area = add.reduce(gaussian)
    divide(gaussian, area, gaussian)
    gaussians.append(gaussian)

  g01 = outer(gaussians[0], gaussians[1])
  g012 = outer(g01, gaussians[2])
  g012 = reshape(g012, data.shape)
  
  cdata = zeros(data.shape, float32)

  from numpy.fft import fftn, ifftn
  # TODO: Fourier transform Gaussian analytically to reduce computation time
  #       about 30% (one of three fft calculations).
  ftg = fftn(g012)
  ftd = fftn(data)
  gd = ifftn(ftg * ftd)
  gd = gd.astype(float32)
  return gd

# -----------------------------------------------------------------------------
#
if len(sys.argv) != 4:
  msg = ('Convolve a Gaussian with grid file ' +
         'and write the result as a netcdf file.\n' +
         'The linewidth is specified in xyz space units '+
         'and spans -1 SD to +1 SD.\n' +
         'Syntax: gaussian.py <infile> <linewidth> <outfile>\n')
  sys.stderr.write(msg)
  sys.exit(1)

inpath = sys.argv[1]
linewidth = float(sys.argv[2])
outpath = sys.argv[3]

gaussian_convolve(inpath, linewidth, outpath)
