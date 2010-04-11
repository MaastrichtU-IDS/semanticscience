# -----------------------------------------------------------------------------
# Save and restore color zone state.
#

# -----------------------------------------------------------------------------
#
def save_color_zone_state(color_zone_table, file):

  s = Color_Zone_State()
  s.state_from_color_zone_table(color_zone_table)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_color_zones():\n')
  file.write(' color_zone_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '   ')
  file.write('\n')
  file.write(' try:\n')
  file.write('  import ColorZone.session\n')
  file.write('  ColorZone.session.restore_color_zone_state(color_zone_state)\n')
  file.write(' except:\n')
  file.write("  reportRestoreError('Error restoring surface color zones')\n")
  file.write('\n')
  file.write('registerAfterModelsCB(restore_color_zones)\n')
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_color_zone_state(color_zone_state):

  classes = (
    Color_Zone_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(color_zone_state, name_to_class)
  s.restore_state()

# -----------------------------------------------------------------------------
#
class Color_Zone_State:

  version = 2
  
  state_attributes = ('color_zone_table',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_color_zone_table(self, color_zone_table):

    from SessionUtil import array_to_string, float32
    czt = {}
    for model, (points, colors, distance) in color_zone_table.items():
      czt[(model.id, model.subid)] = (array_to_string(points,float32),
                                      array_to_string(colors,float32),
                                      distance)
    self.color_zone_table = czt

  # ---------------------------------------------------------------------------
  #
  def restore_state(self):

    from ColorZone import color_zone
    from SessionUtil import string_to_array, float32
    
    czt = self.color_zone_table
    for surface_id_subid, (points, colors, distance) in czt.items():
      from SimpleSession import modelMap
      from _surface import SurfaceModel
      surfaces = [s for s in modelMap.get(surface_id_subid, [])
                  if isinstance(s, SurfaceModel)]
      if surfaces:
        # TODO: If more than one surface may get wrong one.
        surface = surfaces[0]
        if self.version >= 2:
          npoints = string_to_array(points, float32, 3)
          ncolors = string_to_array(colors, float32, 4)
        else:
          from numpy import array, single as floatc
          npoints = array(points, floatc)
          ncolors = array(colors, floatc)
        color_zone(surface, npoints, ncolors, distance, auto_update = True)
      else:
        from chimera import replyobj
        replyobj.info('Warning: Could not restore color zone on surface model\n\twith id %d.%d because that surface was not restored.\n' % surface_id_subid)
