# -----------------------------------------------------------------------------
# Register topography command to surface from volume plane.
#
def topo(*args):
    from Topography import topography_command
    topography_command(*args)
from Midas.midas_text import addCommand
addCommand('topography', topo, help = True)
