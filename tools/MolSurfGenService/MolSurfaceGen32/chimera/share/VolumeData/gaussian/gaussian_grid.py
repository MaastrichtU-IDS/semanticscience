# -----------------------------------------------------------------------------
# Wrap Gaussian energy maps as grid data for displaying surface, meshes,
# and volumes.
#
from VolumeData import Grid_Data

# -----------------------------------------------------------------------------
#
class Gaussian_Grid(Grid_Data):

  def __init__(self, gc, component_number):

    self.gc = gc
    self.component_number = component_number

    # TODO: Axes need not be a rotation.  Use cell_angles and rotation.
    axes = gc.grid_axes
    rot = tuple([tuple([axes[a][b] for a in (0,1,2)]) for b in (0,1,2)])

    Grid_Data.__init__(self, gc.grid_size,
                       origin = gc.origin, step = gc.step, rotation = rot,
                       path = gc.path, file_type = 'gaussian',
                       grid_id = str(component_number))

    self.polar_values = True
  
  # ---------------------------------------------------------------------------
  #
  def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

    matrix = self.gc.matrix(self.component_number, progress)
    if ijk_size != self.size:
      self.cache_data(matrix, (0,0,0), self.size, (1,1,1)) # Cache full data.
    m = self.matrix_slice(matrix, ijk_origin, ijk_size, ijk_step)
    return m

# -----------------------------------------------------------------------------
#
def read_gaussian_file(path):

    import gaussian_format
    gc = gaussian_format.Gaussian_Cube(path)

    grids = []
    for c in range(gc.num_components):
      g = Gaussian_Grid(gc, c)
      grids.append(g)

    return grids
