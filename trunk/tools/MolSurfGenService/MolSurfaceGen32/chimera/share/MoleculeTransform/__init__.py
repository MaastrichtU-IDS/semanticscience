# -----------------------------------------------------------------------------
# Apply a rotation and translation to atoms.
#
def transform_atom_coordinates(atoms, xform):

    for a in atoms:
        a.setCoord(xform.apply(a.coord()))

from Matrix import euler_xform, euler_rotation
