# -----------------------------------------------------------------------------
# Save and restore multiscale state.
#

# -----------------------------------------------------------------------------
#
def save_multiscale_state(multiscale_dialog, file):

  s = Multiscale_Dialog_State()
  s.state_from_dialog(multiscale_dialog)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_multiscale():\n')
  file.write(' multiscale_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '  ')
  file.write('\n')
  file.write(' import MultiScale.session\n')
  file.write(' MultiScale.session.restore_multiscale_state(multiscale_state)\n')
  file.write('\n')
  file.write('try:\n')
  file.write('  restore_multiscale()\n')
  file.write('except:\n')
  file.write("  reportRestoreError('Error restoring multiscale')\n")
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_multiscale_state(multiscale_dialog_state):

  from SessionUtil.stateclasses import Model_State, Xform_State

  classes = (
    Multiscale_Dialog_State,
    Group_Piece_State,
    Chain_Piece_State,
    LAN_Molecule_State,
    LAN_Chain_State,
    Model_State,
    Xform_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(multiscale_dialog_state,
                                             name_to_class)

  import MultiScale
  d = MultiScale.multiscale_model_dialog(create = True)

  set_dialog_state(s, d)

# -----------------------------------------------------------------------------
#
def set_dialog_state(multiscale_dialog_state, multiscale_dialog):

  multiscale_dialog_state.restore_state(multiscale_dialog)

# -----------------------------------------------------------------------------
#
class Multiscale_Dialog_State:

  version = 3
  
  state_attributes = ('is_visible',
                      'geometry',
                      'rgba',
                      'transparency',
                      'surface_resolution',
                      'density_threshold',
                      'density_threshold_ca_only',
                      'smoothing_factor',
		      'smoothing_iterations',
                      'multimer_type',
                      'model_states',
                      'lan_molecule_states',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_dialog(self, multiscale_dialog):

    d = multiscale_dialog
    self.is_visible = d.isVisible()
    self.geometry = d.toplevel_widget.wm_geometry()
    self.rgba = d.color.rgba
    self.transparency = d.transparency.get()
    self.surface_resolution = d.surface_resolution.get()
    self.density_threshold = d.density_threshold.get()
    self.density_threshold_ca_only = d.density_threshold_ca_only.get()
    self.smoothing_factor = d.smoothing_factor.get()
    self.smoothing_iterations = d.smoothing_iterations.get()
    self.multimer_type = d.multimer_type.get()
    lmlist = self.lan_molecule_list(d)
    self.lan_molecule_states = self.lan_molecule_states(lmlist)
    self.model_states = model_piece_states(d.models)

  # ---------------------------------------------------------------------------
  #
  def lan_molecule_list(self, multiscale_dialog):

    # Get list of all LAN_Molecule objects.
    lmtable = {}
    for cp in multiscale_dialog.chain_pieces():
        lmtable[cp.lan_chain.lan_molecule] = 1
    lmlist = lmtable.keys()
    return lmlist

  # ---------------------------------------------------------------------------
  #
  def lan_molecule_states(self, lmlist):

    # Assign id numbers to LAN_Chains used for referencing from Chain_Piece.
    sid = 1
    for lm in lmlist:
        for lc in lm.chains():
            lc.session_id = sid
            sid += 1

    # Create LAN_Molecule_State objects.
    lmstates = []
    for lm in lmlist:
        s = LAN_Molecule_State()
        s.state_from_lan_molecule(lm)
        lmstates.append(s)

    return lmstates
  
  # ---------------------------------------------------------------------------
  #
  def restore_state(self, multiscale_dialog):

    d = multiscale_dialog
    if self.is_visible:
      d.enter()
    d.toplevel_widget.wm_geometry(self.geometry)
    d.color.showColor(self.rgba, doCallback = 0)
    d.transparency.set(self.transparency)
    d.surface_resolution.set(self.surface_resolution)
    d.density_threshold.set(self.density_threshold)
    if self.version >= 2:
      d.density_threshold_ca_only.set(self.density_threshold_ca_only)
    d.smoothing_factor.set(self.smoothing_factor)
    d.smoothing_iterations.set(self.smoothing_iterations)
    d.multimer_type.set(self.multimer_type)
    lmlist = [lms.create_object() for lms in self.lan_molecule_states]
    self.restore_multiscale_models(d, lmlist)
  
  # ---------------------------------------------------------------------------
  #
  def restore_multiscale_models(self, multiscale_dialog, lmlist):
    
    lan_chain_table = {}
    for lm in lmlist:
      if lm:
        for lc in lm.chains():
          lan_chain_table[lc.session_id] = lc

    d = multiscale_dialog
    mlist = [ms.create_object(lan_chain_table, d.surfacer)
             for ms in self.model_states]
    d.add_models(mlist, show = False)

    #
    # Surfaces are recreated after model tree is created because the one
    # SurfaceModel belongs to the root of the tree.
    #
    self.restore_chain_surfaces(d.chain_pieces())

    if self.version <= 2:
      from SimpleSession import registerAfterModelsCB
      registerAfterModelsCB(self.fix_molecule_transforms, mlist)
  
  # ---------------------------------------------------------------------------
  #
  def restore_chain_surfaces(self, chain_pieces):
    
    for cp in chain_pieces:
      if hasattr(cp, 'session_restore_surface_parameters'):
        show = cp.session_restore_surface_parameters[0]
        # Put in None for density threshold for c-alpha only chains
        surf_params = (cp.session_restore_surface_parameters[1:3] + (None,) +
                       cp.session_restore_surface_parameters[3:])
        delattr(cp, 'session_restore_surface_parameters')
        # Have to always show surface so surface_piece is made.
        cp.show_surface(True, surf_params)
        if not show:
          cp.show_surface(False)
  
  # ---------------------------------------------------------------------------
  # At version 3 switched to having molecule transforms be the same
  # as surface model transform and modifying molecule coordinates instead
  # of using different molecule transforms.  This allows moving chains.
  #
  # Correct molecule transforms after session restore finishes restoring
  # transforms.
  #
  def fix_molecule_transforms(self, mlist):

    mtable = {}
    import MultiScale
    cplist = MultiScale.find_pieces(mlist, MultiScale.Chain_Piece)
    for cp in cplist:
      m = cp.molecule(load = False)
      if m and not m in mtable:
        mtable[m] = cp.surface_model()

    for m, sm in mtable.items():
      m.openState.xform = sm.openState.xform

# -----------------------------------------------------------------------------
#
def model_piece_states(model_pieces):

    from MultiScale import Group_Piece, Chain_Piece
    ms = []
    for mp in model_pieces:
        if isinstance(mp, Group_Piece):
            s = Group_Piece_State()
            s.state_from_group_piece(mp)
        elif isinstance(mp, Chain_Piece):
            s = Chain_Piece_State()
            s.state_from_chain_piece(mp)
        ms.append(s)
    return ms

# -----------------------------------------------------------------------------
#
class Group_Piece_State:

  version = 1

  state_attributes = ('name',
                      'children_states',
                      'surface_model_state',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_group_piece(self, group_piece):
    
      gp = group_piece
  
      self.name = gp.name
      self.children_states = model_piece_states(gp.children)

      if gp.surf_model:
          from SessionUtil.stateclasses import Model_State
          sms = Model_State()
          sms.state_from_model(gp.surf_model)
          self.surface_model_state = sms
      else:
          self.surface_model_state = None

  # ---------------------------------------------------------------------------
  #
  def create_object(self, lan_chain_table, surfacer):

      children = [cs.create_object(lan_chain_table, surfacer)
                  for cs in self.children_states]
      children = [c for c in children if not c is None]

      from MultiScale import Group_Piece
      gp = Group_Piece(self.name, children)

      sms = self.surface_model_state
      if sms:
          from SimpleSession import modelOffset
          sm = gp.surface_model(model_id = (sms.id + modelOffset, sms.subid))
          sms.restore_state(sm)
          
      return gp

# -----------------------------------------------------------------------------
#
class Chain_Piece_State:

  version = 1

  state_attributes = ('lan_chain_session_id',
                      'xform_state',
                      'xform_id_number',
                      'surface_shown',
                      'rgba',
                      'surface_resolution',
                      'density_threshold',
                      'smoothing_factor',
                      'smoothing_iterations',
                      'surface_model_state',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_chain_piece(self, chain_piece):

      cp = chain_piece
      self.lan_chain_session_id = cp.lan_chain.session_id
      from SessionUtil.stateclasses import Xform_State
      xfs = Xform_State()
      xfs.state_from_xform(cp.xform)
      self.xform_state = xfs
      if hasattr(cp.xform, 'id_number'):
        self.xform_id_number = cp.xform.id_number
      self.surface_shown = cp.surface_shown()
      self.rgba = cp.color()
      g = cp.surface_piece
      if g:
          (self.surface_resolution,
           self.density_threshold,
           self.smoothing_factor,
           self.smoothing_iterations) = g.surfacing_parameters
      else:
          self.surface_resolution = None
          self.density_threshold = None
          self.smoothing_factor = None
          self.smoothing_iterations = None

      if cp.surf_model:
          from SessionUtil.stateclasses import Model_State
          sms = Model_State()
          sms.state_from_model(cp.surf_model)
          self.surface_model_state = sms
      else:
          self.surface_model_state = None
      
  # ---------------------------------------------------------------------------
  #
  def create_object(self, lan_chain_table, surfacer):

      if not self.lan_chain_session_id in lan_chain_table:
        return None     # Source molecule was not restored by session.

      lan_chain = lan_chain_table[self.lan_chain_session_id]
      xform = self.xform_state.create_object()
      if hasattr(self, 'xform_id_number'):
        xform.id_number = self.xform_id_number
      import MultiScale
      cp = MultiScale.Chain_Piece(lan_chain, xform, surfacer)
      cp.set_color(self.rgba)

      # Surface is restored after tree is created
      cp.session_restore_surface_parameters = \
          (self.surface_shown,
           self.surface_resolution, self.density_threshold,
           self.smoothing_factor, self.smoothing_iterations)
          
      sms = self.surface_model_state
      if sms:
          sm = cp.surface_model()
          sms.restore_state(sm)

      return cp

# -----------------------------------------------------------------------------
#
class LAN_Molecule_State:

  version = 4

  state_attributes = ('name',
                      'source_molecule_id',
                      'molecule_id',
                      'dont_unload',
                      'chain_states',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_lan_molecule(self, lan_molecule):

      lm = lan_molecule
      self.name = lm.name

      sm = lm.source_molecule
      self.source_molecule_id = (sm.id, sm.subid)
      
      m = lm.molecule(load = 0)
      if m:
          self.molecule_id = (m.id, m.subid)
      else:
          self.molecule_id = None

      self.dont_unload = lm.dont_unload
      
      if lm.chain_list == None:
          self.chain_states = None
      else:
          cslist = []
          for lc in lm.chain_list:
              lcs = LAN_Chain_State()
              lcs.state_from_lan_chain(lc)
              cslist.append(lcs)
          self.chain_states = cslist
        
  # ---------------------------------------------------------------------------
  # TODO: Maybe need SimpleSession.registerAfterModelsCB() to assure
  #   that molecules are already restored.  In Chimera 1.2203 and earlier
  #   versions molecules are restored first, but not clear it that is
  #   guaranteed.
  #
  def create_object(self):

    if self.version >= 3:
      source_molecule = find_molecule_by_id(self.source_molecule_id)
    else:
      source_molecule = find_molecule_by_name(self.name)

    if source_molecule is None:
      from chimera.replyobj import info
      info('Multiscale session restore error, molecule "%s" missing.\n'
           % self.name)
      return None

    import MultiScale
    lm = MultiScale.LAN_Molecule(source_molecule)
    lm.dont_unload = self.dont_unload
    if self.molecule_id:
      m = find_molecule_by_id(self.molecule_id)
      if m:
        lm.associate_molecule(m, allow_close = not self.dont_unload)

    if self.chain_states != None:
      clist = map(lambda cs: cs.create_object(lm), self.chain_states)
      lm.chain_list = clist

    return lm
    
# -----------------------------------------------------------------------------
#
def find_molecule_by_id(id):

  from SimpleSession import modelMap
  if not id in modelMap:
    return None
  mlist = modelMap[id]
  from chimera import Molecule
  mlist = [m for m in mlist if isinstance(m, Molecule)]
  if len(mlist) == 0:
    return None
  m = mlist[0]
  return m
          
# -----------------------------------------------------------------------------
#
def find_molecule_by_name(name):

  from chimera import openModels, Molecule
  mlist = openModels.list(modelTypes = [Molecule])
  for m in mlist:
    if m.name == name:
      return m
  return None
      
# -----------------------------------------------------------------------------
#
class LAN_Chain_State:

  version = 1

  state_attributes = ('chain_id',
                      'session_id',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_lan_chain(self, lan_chain):

      lc = lan_chain
      self.chain_id = lc.chain_id
      self.session_id = lc.session_id

  # ---------------------------------------------------------------------------
  #
  def create_object(self, lan_molecule):

      import MultiScale
      lc = MultiScale.LAN_Chain(lan_molecule, self.chain_id)
      lc.session_id = self.session_id
      return lc
