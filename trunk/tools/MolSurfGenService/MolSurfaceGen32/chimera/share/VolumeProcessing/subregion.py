#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Write a grid file subregion in netcdf format.
#
# Syntax: subregion.py <infile> <imin> <imax>
#                       <jmin> <jmax> <kmin> <kmax> <netcdf-outfile>
#
# The file type must be one of the types handled by VolumeData.
#
import sys

# -----------------------------------------------------------------------------
#
def syntax():
  msg = ('Write a subregion of a grid file in netcdf format.\n' +
         'Syntax: subregion.py <infile>\n' + 
         '                     <imin> <imax> <jmin> <jmax> <kmin> <kmax>\n' +
         '                     <netcdf-outfile>\n')
  sys.stderr.write(msg)
  sys.exit(1)

# -----------------------------------------------------------------------------
#
if len(sys.argv) != 9:
  syntax()

inpath = sys.argv[1]
try:
  imin = int(sys.argv[2])
  imax = int(sys.argv[3])
  jmin = int(sys.argv[4])
  jmax = int(sys.argv[5])
  kmin = int(sys.argv[6])
  kmax = int(sys.argv[7])
except:
  syntax()
  
outpath = sys.argv[8]

from VolumeData import fileformats
try:
  glist = fileformats.open_file(inpath)
except fileformats.Unknown_File_Type, e:
  sys.stderr.write(str(e))
  sys.exit(1)

from VolumeData import Grid_Subregion
r = [Grid_Subregion(g, (imin, jmin, kmin), (imax, jmax, kmax)) for g in glist]

from VolumeData.netcdf import write_grid_as_netcdf
write_grid_as_netcdf(r, outpath)
