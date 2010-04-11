# -----------------------------------------------------------------------------
# Save and restore surface zone state.
#

# -----------------------------------------------------------------------------
#
def save_surface_zone_state(zone_table, file):

  s = Surface_Zone_State()
  s.state_from_zone_table(zone_table)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_surface_zones():\n')
  file.write(' surface_zone_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '   ')
  file.write('\n')
  file.write(' try:\n')
  file.write('  import SurfaceZone.session\n')
  file.write('  SurfaceZone.session.restore_surface_zone_state(surface_zone_state)\n')
  file.write(' except:\n')
  file.write("  reportRestoreError('Error restoring surface zones')\n")
  file.write('\n')
  file.write('registerAfterModelsCB(restore_surface_zones)\n')
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_surface_zone_state(surface_zone_state):

  classes = (
    Surface_Zone_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(surface_zone_state,
                                             name_to_class)
  s.restore_state()

# -----------------------------------------------------------------------------
#
class Surface_Zone_State:

  version = 2
  
  state_attributes = ('zone_table',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_zone_table(self, zone_table):

    from SessionUtil import array_to_string, floatc
    zt = {}
    for model, (points, distance) in zone_table.items():
      zt[(model.id, model.subid)] = (array_to_string(points, floatc), distance)
    self.zone_table = zt

  # ---------------------------------------------------------------------------
  #
  def restore_state(self):

    from numpy import array
    from SurfaceZone import surface_zone
    from SessionUtil import string_to_array, floatc
    
    for surface_id_subid, (points, distance) in self.zone_table.items():
      from SimpleSession import modelMap
      from _surface import SurfaceModel
      surfs = [s for s in modelMap.get(surface_id_subid, [])
               if isinstance(s,SurfaceModel)]
      if surfs:
        if self.version >= 2:
          npoints = string_to_array(points, floatc, 3)
        else:
          npoints = array(points, floatc)
        surface_zone(surfs[0], npoints, distance, auto_update = True)
      else:
        from chimera import replyobj
        replyobj.info('Warning: Could not restore surface zone on surface model\n\twith id %d.%d because that surface was not restored.\n' % surface_id_subid)
