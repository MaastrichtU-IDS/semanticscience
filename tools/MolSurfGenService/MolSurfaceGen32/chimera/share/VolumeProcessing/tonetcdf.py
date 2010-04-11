#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Write a grid file in netcdf format.
#
# Syntax: tonetcdf.py <infile> <outfile>
#                     [-origin <xorigin> <yorigin> <zorigin>]
#                     [-step <xstep> <ystep> <zstep>]
#
# The input file type must be one of the types handled by VolumeData.
#
import sys

# -----------------------------------------------------------------------------
#
def syntax():

  msg = ('Write a grid file in netcdf format.\n' +
         'The position and scale of the matrix in xyz coordinate space ' +
         'can be changed.\n' +
         'Syntax: tonetcdf.py <infile> <outfile>\n' +
         '                    [-origin <xorigin> <yorigin> <zorigin>]\n' +
         '                    [-step <xstep> <ystep> <zstep>]\n')
  sys.stderr.write(msg)
  sys.exit(1)

# -----------------------------------------------------------------------------
#
def parse_arguments(argv):

  args = argv[1:]

  xyz_origin = parse_triple(args, '-origin')
  xyz_step = parse_triple(args, '-step')
    
  if len(args) != 2:
    syntax()
    
  inpath, outpath = args

  return inpath, outpath, xyz_origin, xyz_step

# -----------------------------------------------------------------------------
#
def parse_triple(args, option):

  try:
    i = args.index(option)
  except ValueError:
    return None

  try:
    values = map(float, args[i+1:i+4])
  except ValueError:
    syntax()

  if len(values) < 3:
    syntax()
    
  del args[i:i+4]

  return values

# -----------------------------------------------------------------------------
#
def write_netcdf(inpath, outpath, xyz_origin, xyz_step):

  from VolumeData import fileformats
  try:
    glist = fileformats.open_file(inpath)
  except fileformats.Unknown_File_Type, e:
    sys.stderr.write(str(e))
    sys.exit(1)

  if xyz_origin:
    for g in glist:
      g.origin = xyz_origin
  if xyz_step:
    for g in glist:
      g.step = xyz_step
    
  from VolumeData.netcdf import write_grid_as_netcdf
  write_grid_as_netcdf(glist, outpath)

# -----------------------------------------------------------------------------
#
inpath, outpath, xyz_origin, xyz_step = parse_arguments(sys.argv)
write_netcdf(inpath, outpath, xyz_origin, xyz_step)
