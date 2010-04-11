# -----------------------------------------------------------------------------
# Register GRASP surface file reader.
#
def open_cb(path):
    import GraspSurface
    m = GraspSurface.read_grasp_surface(path)
    return [m]

import chimera
fi = chimera.fileInfo
fi.register('GRASP surface', open_cb, ['.srf'], ['graspsurf'],
            canDecompress = False, category = fi.SURFACE)

# -----------------------------------------------------------------------------
# Register keyboard accelerator to write surfaces as a GRASP format file.
#
def write_grasp():
    from GraspSurface.writegrasp import write_grasp_surface_file
    write_grasp_surface_file()

from Accelerators import add_accelerator
add_accelerator('wg', 'Write GRASP surface file', write_grasp)
