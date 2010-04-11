#!/usr/bin/env python
# -----------------------------------------------------------------------------
# Output header of grid file.
#
# Syntax: showheader.py <filename> ...
#
# The file type must be one of the types handled by VolumeData
#
import sys

from VolumeData import fileformats

# -----------------------------------------------------------------------------
#
def show_header(path):

  try:
    glist = fileformats.open_file(path)
  except fileformats.Unknown_File_Type:
    return False

  for grid_data in glist:
    sys.stdout.write('Header for %s\n' % grid_data.path)
    sys.stdout.write('  Data value type: %s\n' % grid_data_type(grid_data))
    sys.stdout.write('  %-12s' % 'size:' +
                     '%12d %12d %12d\n' % tuple(grid_data.size))
    sys.stdout.write('  %-12s' % 'xyz origin:' +
                     '%12.8g %12.8g %12.8g\n' % tuple(grid_data.origin))
    sys.stdout.write('  %-12s' % 'xyz step:' +
                     '%12.8g %12.8g %12.8g\n' % tuple(grid_data.step))
  return True

# -----------------------------------------------------------------------------
#
def grid_data_type(grid_data):

  tname = grid_data.value_type.name
  return tname

# -----------------------------------------------------------------------------
#
if len(sys.argv) < 2:
  sys.stderr.write('Syntax: showheader.py <filename> ...\n')
  sys.exit(1)

paths = sys.argv[1:]
failed_paths = []
for path in paths:
  if not show_header(path):
    failed_paths.append(path)

if failed_paths:
  warning = fileformats.suffix_warning(failed_paths)
  sys.stderr.write(warning)
