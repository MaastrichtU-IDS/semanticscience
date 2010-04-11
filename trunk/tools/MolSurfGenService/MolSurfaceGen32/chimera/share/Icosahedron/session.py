# -----------------------------------------------------------------------------
# Save and restore icosahedron state.
#
  
# -----------------------------------------------------------------------------
#
def save_icosahedron_state(icosahedron_dialog, file):

  s = Icosahedron_Dialog_State()
  s.state_from_dialog(icosahedron_dialog)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_icosahedron():\n')
  file.write(' icosahedron_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '  ')
  file.write('\n')
  file.write(' from Icosahedron import session\n')
  file.write(' session.restore_icosahedron_state(icosahedron_state)\n')
  file.write('\n')
  file.write('try:\n')
  file.write('  restore_icosahedron()\n')
  file.write('except:\n')
  file.write("  reportRestoreError('Error restoring icosahedron')\n")
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_icosahedron_state(icosahedron_dialog_basic_state):

  from SessionUtil.stateclasses import Model_State, Xform_State
  classes = (
    Icosahedron_Dialog_State,
    Model_State,
    Xform_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(icosahedron_dialog_basic_state,
                                             name_to_class)

  import Icosahedron.gui
  d = Icosahedron.gui.icosahedron_dialog(create = True)

  set_dialog_state(s, d)

# -----------------------------------------------------------------------------
#
def set_dialog_state(icosahedron_dialog_state, icosahedron_dialog):

  icosahedron_dialog_state.restore_state(icosahedron_dialog)

# -----------------------------------------------------------------------------
#
class Icosahedron_Dialog_State:

  version = 1
  
  state_attributes = ('is_visible',
                      'geometry',
		      'radius',
		      'sphere_factor',
		      'orientation',
		      'subdivision_factor',
                      'style',
                      'color',
                      'surface_model',
		      'version',
                      )
  
  # ---------------------------------------------------------------------------
  #
  def state_from_dialog(self, icosahedron_dialog):

    d = icosahedron_dialog

    self.is_visible = d.isVisible()
    t = d.uiMaster().winfo_toplevel()
    self.geometry = t.wm_geometry()

    self.radius = d.radius.value(d.default_radius)
    self.sphere_factor = d.sphere_factor.value(0)
    self.orientation = d.orientation.get()
    from CGLtk import Hybrid
    self.subdivision_factor = Hybrid.float_variable_value(d.subdivision_factor,
                                                          1)
    self.style = d.surface_style.get()
    self.color = d.color.rgba

    if d.surface_model is None:
      self.surface_model = None
    else:
      from SessionUtil.stateclasses import Model_State
      self.surface_model = Model_State()
      self.surface_model.state_from_model(d.surface_model)

  # ---------------------------------------------------------------------------
  #
  def restore_state(self, icosahedron_dialog):

    d = icosahedron_dialog
    if self.is_visible:
      d.enter()

    t = d.uiMaster().winfo_toplevel()
    t.wm_geometry(self.geometry)
    t.wm_geometry('')		# restore standard size

    d.radius.set_value(self.radius, invoke_callbacks = False)
    d.sphere_factor.set_value(self.sphere_factor, invoke_callbacks = False)
    d.orientation.set(self.orientation, invoke_callbacks = False)
    d.subdivision_factor.set(self.subdivision_factor, invoke_callbacks = False)
    d.surface_style.set(self.style, invoke_callbacks = False)
    d.color.showColor(self.color, doCallback = False)

    sms = self.surface_model
    if not sms is None:
      from SimpleSession import modelOffset
      d.show_cb(model_id = (sms.id + modelOffset, sms.subid))
      sms.restore_state(d.surface_model)
