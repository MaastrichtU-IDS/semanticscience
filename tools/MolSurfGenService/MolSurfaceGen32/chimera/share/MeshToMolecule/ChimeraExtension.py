# -----------------------------------------------------------------------------
# Register command to make a molecule model from a mesh.
#
def mesh_to_molecule(*args):
    import MeshToMolecule
    MeshToMolecule.mesh_to_molecule(*args)
from Midas.midas_text import addCommand
addCommand('meshmol', mesh_to_molecule, help = True)
