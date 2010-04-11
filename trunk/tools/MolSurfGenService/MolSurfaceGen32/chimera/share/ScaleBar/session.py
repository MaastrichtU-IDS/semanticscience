# -----------------------------------------------------------------------------
# Save and restore scale bar state.
#
  
# -----------------------------------------------------------------------------
#
def save_scale_bar_state(scale_bar_dialog, file):

  s = Scale_Bar_Dialog_State()
  s.state_from_dialog(scale_bar_dialog)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_scale_bar():\n')
  file.write(' scale_bar_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '  ')
  file.write('\n')
  file.write(' import ScaleBar.session\n')
  file.write(' ScaleBar.session.restore_scale_bar_state(scale_bar_state)\n')
  file.write('\n')
  file.write('try:\n')
  file.write('  restore_scale_bar()\n')
  file.write('except:\n')
  file.write("  reportRestoreError('Error restoring scale bar')\n")
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_scale_bar_state(scale_bar_dialog_basic_state):

  from SessionUtil.stateclasses import Model_State, Xform_State

  classes = (
    Scale_Bar_Dialog_State,
    Model_State,
    Xform_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(scale_bar_dialog_basic_state,
                                             name_to_class)

  import ScaleBar
  d = ScaleBar.scale_bar_dialog(create = 1)

  set_dialog_state(s, d)

# -----------------------------------------------------------------------------
#
def set_dialog_state(scale_bar_dialog_state, scale_bar_dialog):

  scale_bar_dialog_state.restore_state(scale_bar_dialog)

# -----------------------------------------------------------------------------
#
class Scale_Bar_Dialog_State:

  version = 1
  
  state_attributes = ('is_visible',
                      'geometry',
		      'show_scalebar',
		      'bar_length',
		      'bar_thickness',
		      'bar_rgba',
		      'label_text',
		      'label_x_offset',
		      'label_y_offset',
		      'label_rgba',
		      'orientation',
		      'preserve_position',
		      'screen_x_position',
		      'screen_y_position',
		      'move_scalebar',
		      'frozen_models',
		      'model',
		      'version',
                      )
  
  # ---------------------------------------------------------------------------
  #
  def state_from_dialog(self, scale_bar_dialog):

    d = scale_bar_dialog

    self.is_visible = d.isVisible()
    self.geometry = d.toplevel_widget.wm_geometry()

    self.show_scalebar = d.show_scalebar.get()
    self.bar_length = d.bar_length.get()
    self.bar_thickness = d.bar_thickness.get()
    self.bar_rgba = d.bar_color.rgba
    self.label_text = d.label_text.get()
    self.label_x_offset = d.label_x_offset.get()
    self.label_y_offset = d.label_y_offset.get()
    self.label_rgba = d.label_color.rgba
    self.orientation = d.orientation.get()
    self.preserve_position = d.preserve_position.get()
    self.screen_x_position = d.screen_x_position.get()
    self.screen_y_position = d.screen_y_position.get()
    self.move_scalebar = d.move_scalebar.get()
    self.frozen_models = map(lambda m: (m.id, m.subid), d.frozen_models())

    if d.model:
      from SessionUtil.stateclasses import Model_State
      self.model = Model_State()
      self.model.state_from_model(d.model)
    else:
      self.model = None

  # ---------------------------------------------------------------------------
  #
  def restore_state(self, scale_bar_dialog):

    d = scale_bar_dialog
    if self.is_visible:
      d.enter()
    d.toplevel_widget.wm_geometry(self.geometry)
    d.toplevel_widget.wm_geometry('')		# restore standard size

    d.show_scalebar.set(self.show_scalebar, invoke_callbacks = 0)
    d.bar_length.set(self.bar_length, invoke_callbacks = 0)
    d.bar_thickness.set(self.bar_thickness, invoke_callbacks = 0)
    d.bar_color.showColor(self.bar_rgba, doCallback = 0)
    d.label_text.set(self.label_text, invoke_callbacks = 0)
    d.label_x_offset.set(self.label_x_offset, invoke_callbacks = 0)
    d.label_y_offset.set(self.label_y_offset, invoke_callbacks = 0)
    d.label_color.showColor(self.label_rgba, doCallback = 0)
    d.orientation.set(self.orientation, invoke_callbacks = 0)
    d.preserve_position.set(self.preserve_position, invoke_callbacks = 0)
    d.screen_x_position.set(self.screen_x_position, invoke_callbacks = 0)
    d.screen_y_position.set(self.screen_y_position, invoke_callbacks = 0)
    d.move_scalebar.set(self.move_scalebar, invoke_callbacks = 0)
    m = self.model
    if m:
      from SimpleSession import modelOffset
      model_id = (m.id + modelOffset, m.subid)
    else:
      model_id = None
    d.settings_changed_cb(model_id = model_id)

    if self.frozen_models:
      from SimpleSession import registerAfterModelsCB
      registerAfterModelsCB(self.restore_frozen_models, scale_bar_dialog)

    if m:
      m.restore_state(d.model)

    if m:
      from SimpleSession import registerAfterModelsCB
      registerAfterModelsCB(self.restore_screen_position, scale_bar_dialog)
      registerAfterModelsCB(self.fix_stick_scale, scale_bar_dialog)
      
  # ---------------------------------------------------------------------------
  #
  def restore_frozen_models(self, scale_bar_dialog):

    frozen_models = []
    if self.frozen_models:
      if isinstance(self.frozen_models[0], basestring):
        from SimpleSession import oslMap
        model_ids = []
        for id in self.frozen_models:
          try:
            new_id = oslMap(id)
          except:
            new_id = id
          model_ids.append(new_id)

        id_to_model = {}
        import chimera
        for m in chimera.openModels.list(all = 1):
          id_to_model[m.oslIdent()] = m

        for id in model_ids:
          if id_to_model.has_key(id):
            frozen_models.append(id_to_model[id])
      else:
        from SimpleSession import modelMap
        for id in self.frozen_models:
          frozen_models.extend(modelMap.get(id, []))
    scale_bar_dialog.frozen_model_list = frozen_models
      
  # ---------------------------------------------------------------------------
  # SimpleSession changes the scale bar xform when the camera has not yet
  # been reset causing the preserved scale bar screen position to change.
  # This restores the screen position after that happens.
  #
  def restore_screen_position(self, scale_bar_dialog):

    d = scale_bar_dialog
    if d.model:
      d.screen_x_position.set(self.screen_x_position, invoke_callbacks = 0)
      d.screen_y_position.set(self.screen_y_position, invoke_callbacks = 0)
      t = d.model.openState.xform.getTranslation()
      d.last_xyz_position = (t.x, t.y, t.z)
      d.settings_changed_cb()
      
  # ---------------------------------------------------------------------------
  # SimpleSession changes the stickScale setting when Chimera 1.1700
  # session files are opened in Chimera >1.18xx.  This resets it to 1.
  #
  def fix_stick_scale(self, scale_bar_dialog):

    d = scale_bar_dialog
    if d.model:
      d.model.stickScale = 1.0
