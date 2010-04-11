# -----------------------------------------------------------------------------
# Register command to make a mesh model of a hexagonal lattice on an
# icosahedron.
#
def hkcage(*args):
    from IcosahedralCage import hkcage_command
    hkcage_command(*args)
import Midas.midas_text
Midas.midas_text.addCommand('hkcage', hkcage, help = True)
