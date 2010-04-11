# -----------------------------------------------------------------------------
# Save and restore hide dust state.
#

# -----------------------------------------------------------------------------
#
def save_hide_dust_state(dust_table, file):

  s = Hide_Dust_State()
  s.state_from_dust_table(dust_table)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_hide_dust():\n')
  file.write(' hide_dust_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '   ')
  file.write('\n')
  file.write(' try:\n')
  file.write('  import HideDust.session\n')
  file.write('  HideDust.session.restore_hide_dust_state(hide_dust_state)\n')
  file.write(' except:\n')
  file.write("  reportRestoreError('Error restoring hide dust')\n")
  file.write('\n')
  file.write('registerAfterModelsCB(restore_hide_dust)\n')
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_hide_dust_state(hide_dust_state):

  classes = (
    Hide_Dust_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(hide_dust_state,
                                             name_to_class)
  s.restore_state()

# -----------------------------------------------------------------------------
#
class Hide_Dust_State:

  version = 1
  
  state_attributes = ('dust_table',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_dust_table(self, dust_table):

    dt = {}
    for model, (method, limit) in dust_table.items():
      dt[(model.id, model.subid)] = (method, limit)
    self.dust_table = dt

  # ---------------------------------------------------------------------------
  #
  def restore_state(self):

    from numpy import array, single as floatc
    import dust
    
    for surface_id_subid, (method, limit) in self.dust_table.items():
      from SimpleSession import modelMap
      if surface_id_subid in modelMap:
        surface = modelMap[surface_id_subid][0]
        dust.hide_dust(surface, method, limit, auto_update = True)
      else:
        from chimera import replyobj
        replyobj.info('Warning: Could not restore hide dust for surface model\n\twith id %d.%d because that surface was not restored.\n' % surface_id_subid)
