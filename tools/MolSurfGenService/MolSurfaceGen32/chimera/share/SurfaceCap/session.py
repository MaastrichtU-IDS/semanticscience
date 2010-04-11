# -----------------------------------------------------------------------------
# Save and restore surface capping state.
#
  
# -----------------------------------------------------------------------------
#
def save_capper_state(capper_dialog, file):

  s = Capper_Dialog_State()
  s.state_from_dialog(capper_dialog)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_surface_capping():\n')
  file.write(' capper_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '  ')
  file.write('\n')
  file.write(' import SurfaceCap.session\n')
  file.write(' SurfaceCap.session.restore_capper_state(capper_state)\n')
  file.write('\n')
  file.write('try:\n')
  file.write('  restore_surface_capping()\n')
  file.write('except:\n')
  file.write("  reportRestoreError('Error restoring surface capping')\n")
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_capper_state(capper_dialog_basic_state):

  classes = (
    Capper_Dialog_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(capper_dialog_basic_state,
                                             name_to_class)

  import SurfaceCap.gui
  d = SurfaceCap.gui.capper_dialog(create = 1)

  set_dialog_state(s, d)

# -----------------------------------------------------------------------------
#
def set_dialog_state(capper_dialog_state, capper_dialog):

  capper_dialog_state.restore_state(capper_dialog)

# -----------------------------------------------------------------------------
#
class Capper_Dialog_State:

  version = 1
  
  state_attributes = ('is_visible',
                      'geometry',
		      'show_caps',
		      'color_caps',
		      'cap_rgba',
		      'cap_style',
		      'subdivision_factor',
                      'cap_offset',
		      'version',
                      )
  
  # ---------------------------------------------------------------------------
  #
  def state_from_dialog(self, capper_dialog):

    d = capper_dialog

    self.is_visible = d.isVisible()
    t = d.uiMaster().winfo_toplevel()
    self.geometry = t.wm_geometry()

    self.show_caps = d.show_caps.get()
    self.color_caps = d.use_cap_color.get()
    self.cap_rgba = d.cap_color.rgba
    self.cap_style = d.cap_style.get()
    self.subdivision_factor = d.subdivision_factor.get()
    self.cap_offset = d.cap_offset.get()

  # ---------------------------------------------------------------------------
  #
  def restore_state(self, capper_dialog):

    d = capper_dialog
    if self.is_visible:
      d.enter()

    t = d.uiMaster().winfo_toplevel()
    t.wm_geometry(self.geometry)
    t.wm_geometry('')		# restore standard size

    d.show_caps.set(self.show_caps, invoke_callbacks = False)
    d.use_cap_color.set(self.color_caps, invoke_callbacks = False)
    d.cap_color.showColor(self.cap_rgba, doCallback = False)
    d.cap_style.set(self.cap_style, invoke_callbacks = 0)
    d.subdivision_factor.set(self.subdivision_factor, invoke_callbacks = 0)
    d.cap_offset.set(self.cap_offset, invoke_callbacks = 0)

    d.settings_changed_cb()
