# ---------------------------------------------------------------------------
#
def split_volume_by_color_zone(v = None):

  if v is None:
    from VolumeViewer import active_volume
    v = active_volume()
    if v is None:
      return

  m = v.surface_model()
  import ColorZone
  if not ColorZone.coloring_zone(m):
    return

  points, colors, radius = ColorZone.zone_points_colors_and_distance(m)

  grids = split_zones_by_color(v, points, colors, radius)
  from VolumeViewer import volume_from_grid_data
  drlist = [volume_from_grid_data(g, show_data = False) for g in grids]
  n = len(v.surface_colors)
  for dr in drlist:
    dr.copy_settings_from(v, copy_region = False)
    dr.set_parameters(surface_colors = [dr.data.zone_color]*n)
    dr.show()
  v.unshow()
  
  return drlist
  
# ---------------------------------------------------------------------------
#
def split_zones_by_color(data_region, points, point_colors, radius):

  ctable = {}
  cc = 0
  for c in point_colors:
    tc = tuple(c)
    if not tc in ctable:
      cc += 1
      ctable[tc] = cc
  point_indices = [ctable[tuple(c)] for c in point_colors]

  ijk_min, ijk_max, ijk_step = data_region.region
  from VolumeData import Grid_Subregion
  sg = Grid_Subregion(data_region.data, ijk_min, ijk_max)

  # Get volume mask with values indicating nearest color within given radius.
  from VolumeData import zone_mask, masked_grid_data
  mask = zone_mask(sg, points, radius, zone_point_mask_values = point_indices)

  grids = []
  for m in range(cc+1):
      g = masked_grid_data(sg, mask, m)
      g.name = data_region.data.name + (' %d' % m)
      grids.append(g)

  # Record colors.
  for color, m in ctable.items():
    grids[m].zone_color = color
  grids[0].zone_color = data_region.surface_colors[0]
  
  return grids
