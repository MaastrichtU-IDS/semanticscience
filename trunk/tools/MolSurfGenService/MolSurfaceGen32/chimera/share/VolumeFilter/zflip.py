# -----------------------------------------------------------------------------
# Reverse order of z planes.  Origin and grid spacing remain the same.
#
# This is not the same as inverting the z axis if cell angles are not
# 90 degrees.  Does not change rotation or symmetries.
#
from VolumeData import Grid_Data
class Z_Flip_Grid(Grid_Data):

    def __init__(self, grid_data):

        d = grid_data
        self.data = d

        Grid_Data.__init__(self, d.size, d.value_type,
                           d.origin, d.step, d.cell_angles,
                           d.rotation, d.symmetries,
                           name = d.name + ' z flip',
                           file_type = d.file_type,
                           default_color = d.rgba)
        self.data_cache = None      # Caching done by underlying grid.
        
    # -------------------------------------------------------------------------
    #
    def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

        origin = self.flipped_origin(ijk_origin, ijk_size)
        m = self.data.matrix(origin, ijk_size, ijk_step, progress)
        return m[::-1,:,:]
        
    # -------------------------------------------------------------------------
    #
    def cached_data(self, ijk_origin, ijk_size, ijk_step):

        origin = self.flipped_origin(ijk_origin, ijk_size)
        m = self.data.cached_data(origin, ijk_size, ijk_step)
        if m is None:
            return m
        return m[::-1,:,:]
        
    # -------------------------------------------------------------------------
    #
    def flipped_origin(self, ijk_origin, ijk_size):

        origin = list(ijk_origin)
        origin[2] = self.data.size[2] - (ijk_origin[2] + ijk_size[2])
        return origin

    # -------------------------------------------------------------------------
    #
    def clear_cache(self):

        self.data.clear_cache()

# -----------------------------------------------------------------------------
#
def zflip(m):

    n = m.shape[0]
    for k in range(n/2-1):
        p = m[k,:,:].copy()
        m[k,:,:] = m[n-1-k,:,:]
        m[n-1-k,:,:] = p
