import chimera.extension

# -----------------------------------------------------------------------------
#
def write_obj(path):
  import ExportOBJ 
  ExportOBJ.write_surfaces_as_wavefront_obj(path)

descrip = 'Export scene in <a href="http://www.fileformat.info/format/wavefrontobj/">Wavefront OBJ</a> file format.  Only surfaces are exported, not molecular models.  Only a single color is exported for each surface to a separate file with suffix ".mtl".  Both displayed and undisplayed surfaces are exported.'

from chimera import exports
exports.register('OBJ', '*.obj', '.obj', write_obj, descrip)
