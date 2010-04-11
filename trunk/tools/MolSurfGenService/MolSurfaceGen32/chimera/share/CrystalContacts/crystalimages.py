# -----------------------------------------------------------------------------
# Script to make crystal contact images for a set of PDB files.
# Written for Cathy Lawson, Aug 8, 2006.
#
pdb_directory = '/usr/local/src/staff/goddard/virus-xtal-pdb'
image_directory = '/usr/local/src/staff/goddard/virus-images'

from os import listdir
pdb_file_names = [p for p in listdir(pdb_directory)
                  if p.endswith('.pdb') and not p.startswith('.')]

from os.path import join, basename
from chimera import viewer, runCommand

viewer.windowSize = (512, 512)  # Set Chimera window size

for file_name in pdb_file_names:
    pdb_path = join(pdb_directory, file_name)
    base_name = basename(file_name)
    image_path = join(image_directory, base_name + '.jpg')
    runCommand('open pdb 0 %s' % pdb_path)
    runCommand('crystalcontacts #0 1.0')
    runCommand('copy file %s jpeg' % image_path)
    runCommand('close all')
