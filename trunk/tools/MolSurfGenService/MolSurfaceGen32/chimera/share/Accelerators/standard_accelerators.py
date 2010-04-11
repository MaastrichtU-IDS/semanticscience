import chimera

# -----------------------------------------------------------------------------
# Standard accelerators.
#
def register_accelerators():

  accelerators = [
    ('a0', 'Activate model 0 (toggle)', activate_model_0),
    ('a1', 'Activate model 1 (toggle)', activate_model_1),
    ('a2', 'Activate model 2 (toggle)', activate_model_2),
    ('a3', 'Activate model 3 (toggle)', activate_model_3),
    ('aa', 'Activate all models', activate_all),
    ('ad', 'Accelerator dialog', show_accelerator_dialog),
    ('af', 'Accelerators off', turn_off_accelerators),
    ('ao', 'Activate only selected models', activate_only),
    ('ar', 'Activate reverse', activate_reverse),
    ('at', 'Activate toggle', activate_toggle_and_remember),
    ('bb', 'Backbone only', backbone_only),
    ('bk', 'Set background to black', set_black_background),
    ('bs', 'Ball & stick representation', ball_and_stick_representation),
    ('c2', 'Color secondary structure', color_secondary_structure),
    ('Ca', 'Close all models', close_all_models),
    ('ca', 'Adjust clip planes with mouse', clip_adjust),
    ('cc', 'Clip selected models', clip_selected_models),
    ('ce', 'Color by element', color_by_element),
    ('cl', 'Show command line', show_command_line),
    ('cm', 'Show surface color dialog', show_surface_color_dialog),
    ('cp', 'Show surface capper dialog', show_surface_capper_dialog),
    ('cr', 'Set center of rotation', set_center_of_rotation),
    ('cs', 'Clear selection', clear_selection),
    ('Cs', 'Close session', close_session),
    ('ct', 'Show chain trace only', show_chain_trace_only),
    ('da', 'Display atoms', display_atoms),
    ('Da', 'Delete atoms and bonds', delete_atoms),
    ('dc', 'Toggle depth cueing', toggle_depth_cueing),
    ('dp', 'Display path tracer markers', show_all_markers),
    ('ds', 'Display surface', show_surface),
    ('ff', 'Fetch file from web', fetch_file),
    ('fo', 'Focus', focus),
    ('gb', 'Set gray background', set_gray_background),
    ('gl', 'Toggle glossy lighting', glossy_lighting),
    ('ha', 'Hide atoms', hide_atoms),
    ('hc', 'Hide command line', hide_command_line),
    ('hp', 'Hide path tracer markers', hide_all_markers),
    ('hr', 'Hide ribbon', hide_ribbon),
    ('hs', 'Hide surface', hide_surface),
    ('ir', 'Independent center of rotation', independent_cofr),
    ('is', 'Invert selection (selected models)', invert_selection),
    ('iS', 'Invert selection (all models)', invert_selection_all_models),
    ('kl', 'Show per-model clipping dialog', show_per_model_clipping_dialog),
    ('lo', 'Show names of last opened files', names_of_last_opened),
    ('ls', 'Open last session file', open_last_session),
    ('mm', 'Mouse modes', show_mouse_modes),
    ('mp', 'Show model panel dialog', show_model_panel),
    ('mw', 'Molecular weight', molecular_weight),
    ('o2', 'Open last 2 files', open_last_2_files),
    ('o3', 'Open last 3 files', open_last_3_files),
    ('oc', 'Type one command', one_command),
    ('oj', 'Open 3nd to last file', open_3rd_to_last_file),
    ('ok', 'Open 2nd to last file', open_2nd_to_last_file),
    ('ol', 'Open last file', open_last_file),
    ('Op', 'Original model positions', original_positions),
    ('op', 'Open file', open_file),
    ('or', 'Orthographic projection', toggle_ortho_projection),
    ('os', 'Open session', open_session),
    ('ov', 'Open volume', open_file),
    ('Qt', 'Quit Chimera', quit),
    ('pf', 'Preferences dialog', show_preferences_dialog),
    ('ps', 'Python shell', show_python_shell),
    ('ra', 'Render by attribute', show_render_by_attribute_dialog),
    ('rc', 'Rainbow chain', rainbow_chain),
    ('re', 'Edged ribbon', edged_ribbon),
    ('rf', 'Flat ribbon', flat_ribbon),
    ('rh', 'Hide ribbon', hide_ribbon),
    ('rl', 'Reply log', show_reply_log),
    ('rr', 'Round ribbon', round_ribbon),
    ('sa', 'Select all', select_all),
    ('sc', 'Select connected atoms/bonds', select_connected),
    ('se', 'Toggle silhouette edges', toggle_silhouette_edges),
    ('sf', 'Show surface', show_surface),
    ('sF', 'Surface selected atoms', surface_selected_atoms),
    ('si', 'Save image...', save_image),
    ('sl', 'Show/Hide status line', toggle_status_line),
    ('so', 'Standard orientation', standard_orientation),
    ('sp', 'Sphere representation', sphere_representation),
    ('ss', 'Save session as...', save_session_as),
    ('Ss', 'Save session', save_session),
    ('st', 'Stick representation', stick_representation),
    ('sv', 'Show side view dialog', show_side_view),
    ('sx', 'Show side chains only', show_side_chains_only),
    ('t0', 'Transparent surface 0%', transparent_surface_0),
    ('t5', 'Transparent surface 50%', transparent_surface_50),
    ('ug', "User's guide", show_users_guide),
    ('va', 'View all models', view_all),
    ('vp', 'Show volume path tracer dialog', show_volume_path_tracer_dialog),
    ('wb', 'Set background to white', set_white_background),
    ('wr', 'Wire representation', wire_representation),
    ('xs', 'Export scene', export_scene),
    ('x9', 'Turn 90 degrees about x axis', turn_x_90),
    ('y9', 'Turn 90 degrees about y axis', turn_y_90),
    ('z9', 'Turn 90 degrees about z axis', turn_z_90),
    ('zn', 'Select zone using zone dialog settings', select_zone),
    ('zd', 'Show zone dialog', show_zone_dialog),
    ]

  from Accelerators import add_accelerator
  for (keys, descrip, func) in accelerators:
    add_accelerator(keys, descrip, func)
    
# -----------------------------------------------------------------------------
#
def activate_model_0():
  'Toggle whether model 0 can be moved with mouse'
  activate_model(0)
    
# -----------------------------------------------------------------------------
#
def activate_model_1():
  'Toggle whether model 1 can be moved with mouse'
  activate_model(1)
    
# -----------------------------------------------------------------------------
#
def activate_model_2():
  'Toggle whether model 2 can be moved with mouse'
  activate_model(2)
    
# -----------------------------------------------------------------------------
#
def activate_model_3():
  'Toggle whether model 3 can be moved with mouse'
  activate_model(3)
    
# -----------------------------------------------------------------------------
#
def activate_model(model_number):
  'Toggle whether model can be moved with mouse'
  mlist = chimera.openModels.list(id = model_number)
  activate_toggle(mlist)
  
# -----------------------------------------------------------------------------
#
def activate_toggle(models):
  'Toggle whether models can be moved with mouse'
  ostable = {}
  for m in models:
    ostable[m.openState] = 1
  oslist = ostable.keys()
  for os in oslist:
    os.active = not os.active
    
# -----------------------------------------------------------------------------
#
def activate_all():
  'Make all models movable with mouse'
  mlist = chimera.openModels.list()
  for m in mlist:
    m.openState.active = True
    
# -----------------------------------------------------------------------------
#
def activate_only():
  'Activate only selected models'
  from chimera import selection, Model
  osactive = set([m.openState for m in selection.currentGraphs()
                  if isinstance(m, Model)])
  osall = set([m.openState for m in chimera.openModels.list()])
  for os in osall:
    os.active = (os in osactive)
    
# -----------------------------------------------------------------------------
#
def activate_reverse():
  'Make movable models unmovable and unmovable models movable'
  mlist = chimera.openModels.list()
  activate_toggle(mlist)
    
# -----------------------------------------------------------------------------
#
last_active = None
def activate_toggle_and_remember():
  'Toggle and remember active models'
  global last_active
  mlist = chimera.openModels.list()
  iamlist = filter(lambda m: not m.openState.active, mlist) # Inactive models
  if iamlist:
    last_active = iamlist
    activate_toggle(last_active)
  elif last_active:
    last_active = filter(lambda m: not is_model_deleted(m), last_active)
    activate_toggle(last_active)
    
# -----------------------------------------------------------------------------
#
def is_model_deleted(m):
  'Test if model has been deleted'
  try:
    m.display
  except:
    return True
  return False
  
# -----------------------------------------------------------------------------
#
def show_accelerator_dialog():
  'Show accelerator browser dialog'
  import Accelerators
  Accelerators.show_accelerator_dialog()

# -----------------------------------------------------------------------------
#
def turn_off_accelerators():
  'Turn off accelerators'
  import Accelerators
  Accelerators.activate_accelerators(0)

# -----------------------------------------------------------------------------
#
def backbone_only():
  'Display backbone only'
  from chimera import actions
  actions.displayResPart(backbone = 1)

# -----------------------------------------------------------------------------
#
def ball_and_stick_representation():
  'Show molecules with ball and stick representation'
  from chimera import actions
  actions.setAtomBondDraw(chimera.Atom.Ball, chimera.Bond.Stick)

# -----------------------------------------------------------------------------
#
def clip_selected_models():
  'Toggle per-model clipping for selected models'
  from chimera import selection, openModels
  mlist = [m for m in selection.currentGraphs() if m.display]
  if len(mlist) == 0:
    mlist = [m for m in openModels.list() if m.display and m.useClipPlane]
    if len(mlist) == 0:
      mlist = [m for m in openModels.list() if m.display]
      if len(mlist) == 0:
        return

  from chimera import tkgui
  for m in mlist:
    if m.useClipPlane:
      m.useClipPlane = False
    elif m.bbox()[0]:
      tkgui.setClipModel(m)      # Set initial clip plane placement.

  # Turn off clip adjust mouse mode.
  cm = tkgui.getClipModel()
  if cm is None or not cm.useClipPlane:
    from chimera import dialogs
    import ModelClip
    cd = dialogs.find(ModelClip.ClipDialog.name)
    if cd:
      cd.stopMouseClip()

# -----------------------------------------------------------------------------
#
def clip_adjust():
  'Toggle mouse modes to move per-model clip plane of selected model'
  from chimera import selection, openModels, tkgui
  mlist = [m for m in selection.currentGraphs() if m.useClipPlane and m.display]
  if len(mlist) == 0:
    mlist = [m for m in openModels.list() if m.useClipPlane and m.display]
  if clip_adjust_enabled():
    if len(mlist) == 0 or tkgui.getClipModel() in mlist:
      enable_clip_adjust(False)
    else:
      tkgui.setClipModel(mlist[0])
  elif mlist:
    enable_clip_adjust(mlist[0])

# -----------------------------------------------------------------------------
#
def enable_clip_adjust(m):

  cd = clip_dialog()
  if m:
    cd.startMouseClip(m)
  else:
    cd.stopMouseClip()

# -----------------------------------------------------------------------------
#
def clip_adjust_enabled():

  if clip_dialog().normMouse:
    from chimera import tkgui
    return tkgui.getClipModel()
  return None

# -----------------------------------------------------------------------------
# Get clip dialog but do not show it.
#
def clip_dialog():

  from chimera import dialogs
  import ModelClip
  cd = dialogs.find(ModelClip.ClipDialog.name)
  if cd is None:
    cd = dialogs.find(ModelClip.ClipDialog.name, create = True)
    cd.Close()
  return cd

# -----------------------------------------------------------------------------
#
def color_by_element():
  'Color atoms by element'
  class all_objects:
    def get(self): return 'all'
  from chimera import actions
  actions.colorByElement(appliesToVar = all_objects())

# -----------------------------------------------------------------------------
#
def color_secondary_structure():
  'Color secondary structure using ColorSS extension'
  import ColorSS
  from chimera import dialogs
  d = dialogs.find(ColorSS.ColorSSDialog.name, create=False)
  if d == None:
    d = dialogs.display(ColorSS.ColorSSDialog.name)
    d.Close()
  d.Apply()

# -----------------------------------------------------------------------------
#
def close_all_models():
  'Close all models'
  om = chimera.openModels
  om.close(om.list())

# -----------------------------------------------------------------------------
#
def clear_selection():
  'Clear selection'
  from chimera import selection
  selection.setCurrent([])

# -----------------------------------------------------------------------------
#
def close_session():
  'Close the current session'
  chimera.closeSession()

# -----------------------------------------------------------------------------
#
def show_chain_trace_only():
  'Show molecule chain trace only'
  from chimera import actions
  actions.displayResPart(trace = 1)

# -----------------------------------------------------------------------------
#
def display_atoms():
  'Display atoms'
  from chimera import actions
  actions.setDisplay(1)

# -----------------------------------------------------------------------------
#
def delete_atoms():
  'Delete atoms and bonds'
  from chimera import actions
  actions.delAtomsBonds()

# -----------------------------------------------------------------------------
#
def toggle_depth_cueing():
  'Toggle depth cueing (ie dimming with depth)'
  import chimera
  v = chimera.viewer
  v.depthCue = not v.depthCue
  
# -----------------------------------------------------------------------------
#
def export_scene():
  'Export 3D scene for external rendering programs'
  from chimera import dialogs, exportDialog
  dialogs.display(exportDialog.name)
  
# -----------------------------------------------------------------------------
#
def focus():
  'Set camera to show selected objects'
  from chimera import actions
  actions.focus()

# -----------------------------------------------------------------------------
#
def hide_atoms():
  'Hide atoms'
  from chimera import actions
  actions.setDisplay(0)

# -----------------------------------------------------------------------------
#
def hide_command_line():
  'Undisplay the command line'
  from Midas import midas_ui
  midas_ui.hideUI()

# -----------------------------------------------------------------------------
#
def hide_surface():
  'Hide MSMS molecular surface'
  from chimera.selection import currentAtoms
  from Surface import selected_surface_pieces, hide_surfaces
  if len(currentAtoms()) > 0 or len(selected_surface_pieces()) == 0:
    # If actions.hideSurface() with no atoms selected and a SurfacePiece is
    # selected then it shows a warning dialog.  Suppress that.
    from chimera import actions
    actions.hideSurface()     # MSMSModel surfaces
  hide_surfaces(selected_surface_pieces())    # SurfaceModel surfaces

# -----------------------------------------------------------------------------
#
def independent_cofr():
  'Toggle center of rotation between independent and default center'
  from chimera import openModels as om
  if om.cofrMethod == om.Independent:
    from chimera import viewing
    m = viewing.defaultCofrMethod
  else:
    m = om.Independent
  om.cofrMethod = m
    
# -----------------------------------------------------------------------------
#
def invert_selection():
  'Invert selection within selected models'
  from chimera import selection
  selection.invertCurrent(allModels = False)

# -----------------------------------------------------------------------------
#
def invert_selection_all_models():
  'Invert selection within space of all models'
  from chimera import selection
  selection.invertCurrent(allModels = True)
      
# -----------------------------------------------------------------------------
#
def show_surface_color_dialog():
  'Show dialog for surface coloring using volume data'
  import SurfaceColor.gui
  SurfaceColor.gui.show_surface_color_dialog()

# -----------------------------------------------------------------------------
#
def set_center_of_rotation():
  'Set center of rotation to center of selected atoms or use center of models mode if no atoms are selected'
  from chimera import selection
  if selection.currentEmpty():
    chimera.runCommand('~cofr')
  else:
    chimera.runCommand('cofr sel')

# -----------------------------------------------------------------------------
#
def show_surface_capper_dialog():
  'Show surface capping dialog'
  import SurfaceCap.gui
  SurfaceCap.gui.show_capper_dialog()

# -----------------------------------------------------------------------------
#
def show_per_model_clipping_dialog():
  'Show per-model clipping dialog'
  from chimera import dialogs
  import ModelClip
  dialogs.display(ModelClip.ClipDialog.name)

# -----------------------------------------------------------------------------
#
def transparent_surface_50():
  'Make selected surfaces 50% transparent'
  from chimera.actions import transpSurf
  transpSurf(0.50)

# -----------------------------------------------------------------------------
#
def transparent_surface_0():
  'Make selected surfaces opaque (0% transparent)'
  from chimera.actions import transpSurf
  transpSurf(0.0)

# -----------------------------------------------------------------------------
#
def show_command_line():
  'Show command line and turn off accelerators'
  from Midas import midas_ui
  midas_ui.createUI()
  turn_off_accelerators()

# -----------------------------------------------------------------------------
#
def one_command():
  'Show command-line and return to shortcuts after entering one command'
  show_command_line()
  from chimera import triggers as t
  from Midas.midas_ui import triggerName as command_entered_trigger
  def enable_shortcuts(trigger_name, handler, command_text):
    t.deleteHandler(command_entered_trigger, handler[0])
    import Accelerators
    Accelerators.activate_accelerators(True)
  h = []
  h.append(t.addHandler(command_entered_trigger, enable_shortcuts, h))

# -----------------------------------------------------------------------------
#
def show_mouse_modes():
  'Show mouse modes pane of preferences dialog'
  from chimera import dialogs
  d = dialogs.display('preferences')
  from chimera import tkgui
  d.setCategoryMenu(tkgui.MOUSE)

# -----------------------------------------------------------------------------
#
def show_model_panel():
  'Show the model panel dialog'
  from chimera import dialogs
  import ModelPanel
  dialogs.display(ModelPanel.ModelPanel.name)

# -----------------------------------------------------------------------------
#
def molecular_weight():
  'Report molecular weight of selected atoms'
  from chimera import selection, replyobj
  w = sum([a.element.mass for a in selection.currentAtoms()])
  if w >= 1.0e6:
    s = '%.4g MDa' % (w * 1.0e-6)
  elif w >= 1.0e3:
    s = '%.4g KDa' % (w * 1.0e-3)
  else:
    s = '%.4g Daltons' % (w * 1.0e-3)
  replyobj.status('Molecular weight ' + s)

# -----------------------------------------------------------------------------
#
def names_of_last_opened():
  'Show the names of the last 3 opened files on the status line'
  paths = recent_opened_files()
  import os.path
  last3 = ', '.join(map(os.path.basename, paths[:3]))
  from chimera.replyobj import status
  status(last3)

# -----------------------------------------------------------------------------
#
def open_last_file():
  'Open the top file in the file history list'
  open_previous_file(0)
  
# -----------------------------------------------------------------------------
#
def open_2nd_to_last_file():
  'Open the second file in the file history list'
  open_previous_file(1)
  
# -----------------------------------------------------------------------------
#
def open_3rd_to_last_file():
  'Open the second file in the file history list'
  open_previous_file(2)
  
# -----------------------------------------------------------------------------
#
def open_previous_file(*nth):
  'Open a previous file in the file history list'
  paths = recent_opened_files()
  for k in nth:
    if len(paths) > k:
      ftype = None              # must recognize suffix to get file type
      from chimera.tkgui import openPath
      openPath(paths[k], ftype)
      remember_file(paths[k])
      main_window_focus()
    
# -----------------------------------------------------------------------------
# Put file at top of main open dialog file history.
#
def remember_file(path):

  d = chimera.tkgui.importDialog()
  d.rememberFile(path)
    
# -----------------------------------------------------------------------------
#
def open_last_2_files():
  'Open the top 2 files in the file history list'
  open_previous_file(1,0)
    
# -----------------------------------------------------------------------------
#
def open_last_3_files():
  'Open the top 3 files in the file history list'
  open_previous_file(2,1,0)

# -----------------------------------------------------------------------------
#
def recent_opened_files(session_files = False):
  #
  # The OpenSave preferences implementation doesn't provide a way to
  # get the file history list without using private variables.
  #
  from OpenSave import miller
  h = miller._prefs['fileHistory']
  if session_files:
    historyID = 'SimpleSession'
  else:
    historyID = 'main chimera import dialog'
  if not h.has_key(historyID):
    return []
  flist = h[historyID]
  return tuple(flist)

# -----------------------------------------------------------------------------
#
def open_last_session():
  'Open the top file in the session file history list'
  paths = recent_opened_files(session_files = True)
  if paths:
    from chimera import openModels
    openModels.open(paths[0], type="Python")

# -----------------------------------------------------------------------------
#
def open_file():
  'Show the main Chimera open file dialog'
  import chimera.tkgui
  chimera.tkgui._importModel()

# -----------------------------------------------------------------------------
#
def fetch_file():
  'Show dialog for fetching PDB file by id'
  import chimera.fetch
  chimera.fetch.showFetchDialog()

# -----------------------------------------------------------------------------
#
def open_session():
  'Show the open session dialog'
  from chimera import dialogs
  from SimpleSession.gui import OpenSessionDialog
  dialogs.display(OpenSessionDialog.name)

# -----------------------------------------------------------------------------
#
def quit():
  'Quit Chimera'
  from chimera import dialogs
  dialogs.display('Confirm Exit')

# -----------------------------------------------------------------------------
#
def show_preferences_dialog():
  'Show Preferences dialog'
  from chimera import dialogs
  dialogs.display('preferences')

# -----------------------------------------------------------------------------
#
def show_python_shell():
  'Show Python shell (IDLE)'
  import Idle
  Idle.start_shell()

# -----------------------------------------------------------------------------
#
def show_render_by_attribute_dialog():
  'Show Render by Attribute dialog'
  from ShowAttr import ShowAttrDialog
  from chimera import dialogs
  dialogs.display(ShowAttrDialog.name).configure(mode="Render")

# -----------------------------------------------------------------------------
#
def rainbow_chain():
  'Color each chain with a different color'
  chimera.runCommand('rainbow chain')

# -----------------------------------------------------------------------------
#
def edged_ribbon():
  'Show molecules with edged ribbon representation'
  from chimera import actions
  actions.setRibbonDraw(chimera.Residue.Ribbon_Edged)
  actions.setResidueDisplay(1)
  
# -----------------------------------------------------------------------------
#
def flat_ribbon():
  'Show molecules with flat ribbon representation'
  from chimera import actions
  actions.setRibbonDraw(chimera.Residue.Ribbon_2D)
  actions.setResidueDisplay(1)
  
# -----------------------------------------------------------------------------
#
def hide_ribbon():
  'Hide molecule ribbons by undisplaying residues'
  from chimera import actions
  actions.setResidueDisplay(0)

# -----------------------------------------------------------------------------
#
def show_reply_log():
  'Show Reply log'
  from chimera import dialogs
  from chimera import tkgui
  dialogs.display(tkgui._ReplyDialog.name)

# -----------------------------------------------------------------------------
#
def round_ribbon():
  'Show molecules with round ribbon representation'
  from chimera import actions
  actions.setRibbonDraw(chimera.Residue.Ribbon_Round)
  actions.setResidueDisplay(1)

# -----------------------------------------------------------------------------
#
def select_all():
  'Select all models'
  from chimera import selection, openModels
  selection.setCurrent(openModels.list())

# -----------------------------------------------------------------------------
#
def toggle_silhouette_edges():
  'Toggle display of silhouette edges'
  from chimera import viewer as v
  v.showSilhouette = not v.showSilhouette

# -----------------------------------------------------------------------------
#
def show_surface():
  'Show MSMS molecular surface'
  from chimera.selection import currentAtoms
  from Surface import selected_surface_pieces, show_surfaces
  if len(currentAtoms()) > 0 or len(selected_surface_pieces()) == 0:
    # If actions.showSurface() with no atoms selected and a SurfacePiece is
    # selected then it shows a warning dialog.  Suppress that.
    from chimera import actions
    actions.showSurface()     # MSMSModel surfaces
  show_surfaces(selected_surface_pieces())    # SurfaceModel surfaces

# -----------------------------------------------------------------------------
#
surface_category_number = 1
def surface_selected_atoms():
  'Show MSMS molecular surface enclosing just the selected atoms'
  global surface_category_number
  category_name = 'c%d' % surface_category_number
  chimera.runCommand('surfcat %s sel' % category_name)
  surface_category_number += 1
  chimera.runCommand('surface %s' % category_name)

# -----------------------------------------------------------------------------
#
def save_image():
  'Save image in a file'
  from chimera import dialogs, printer
  dialogs.display(printer.ImageSaveDialog.name)

# -----------------------------------------------------------------------------
#
def show_side_chains_only():
  'Show molecule side chains/bases only'
  from chimera import actions
  actions.displayResPart(side = 1)

# -----------------------------------------------------------------------------
#
def select_connected():
  'Select atoms and bonds connected to currently selected atoms and bnods'
  from chimera import selection, Atom
  atoms_and_bonds = selection.currentAtoms() + selection.currentBonds()
  reached = set(atoms_and_bonds)
  i = 0
  while i < len(atoms_and_bonds):
    ab = atoms_and_bonds[i]
    if isinstance(ab, Atom):
      n = ([b for b in ab.bonds if not b in reached] +
           [a for a in ab.neighbors if not a in reached])
    else:
      n = [a for a in ab.atoms if not a in reached]
    atoms_and_bonds.extend(n)
    reached.update(set(n))
    i += 1
  selection.setCurrent(atoms_and_bonds)

# -----------------------------------------------------------------------------
#
def toggle_status_line():
  'Show or unshow main window status line'
  from chimera import statusline
  shown = statusline.status_line_shown()
  statusline.show_status_line(not shown)

# -----------------------------------------------------------------------------
#
def sphere_representation():
  'Show molecules with sphere representation'
  from chimera import actions
  actions.setAtomBondDraw(chimera.Atom.Sphere, chimera.Bond.Wire)

# -----------------------------------------------------------------------------
#
def save_session_as():
  'Show the save session dialog'
  from chimera import dialogs
  from SimpleSession.gui import SaveSessionDialog
  dialogs.display(SaveSessionDialog.name)

# -----------------------------------------------------------------------------
#
def save_session():
  'Save the session to the most recent session file'
  from chimera import tkgui
  tkgui.saveSession()

# -----------------------------------------------------------------------------
#
def stick_representation():
  'Show molecules with stick representation'
  from chimera import actions
  actions.setAtomBondDraw(chimera.Atom.EndCap, chimera.Bond.Stick)
  
# -----------------------------------------------------------------------------
#
def standard_orientation():
  'Rotate active models to standard orientation.\nx horizontal, y vertical, z out of screen'

  mlist = chimera.openModels.list()
  if len(mlist) == 0:
    return

  xform = mlist[0].openState.xform
  axis, angle = xform.getRotation()
  rot = chimera.Xform.rotation(axis, -angle)
  chimera.openModels.applyXform(rot)
  
# -----------------------------------------------------------------------------
#
def original_positions():
  'Move all models to original positions on open.  Like reset command.'
  identity = chimera.Xform()
  for m in chimera.openModels.list():
    m.openState.xform = identity

# -----------------------------------------------------------------------------
#
def toggle_ortho_projection():
  'Toggle between orthographic and persepective projection'
  c = chimera.viewer.camera
  c.ortho = not c.ortho

# -----------------------------------------------------------------------------
#
def show_side_view():
  'Show side view dialog'
  from chimera import dialogs
  from chimera import viewing
  dialogs.display(viewing.ViewerDialog.name)
  d = dialogs.find(viewing.ViewerDialog.name, create = 1)
  d.nb.raise_page('pSideView')

# -----------------------------------------------------------------------------
#
def show_users_guide():
  'Show users guide in web browser'
  from chimera import help
  help.display('UsersGuide/index.html')

# -----------------------------------------------------------------------------
#
def view_all():
  'Adjust camera center and scale so all displayed models are in view.'
  chimera.viewer.viewAll()

# -----------------------------------------------------------------------------
#
def show_volume_path_tracer_dialog():
  'Show volume path tracer viewer dialog'
  import VolumePath
  VolumePath.show_volume_path_dialog()

# -----------------------------------------------------------------------------
#
def wire_representation():
  'Show molecules with wire representation'
  from chimera import actions
  actions.setAtomBondDraw(chimera.Atom.Dot, chimera.Bond.Wire)

# -----------------------------------------------------------------------------
#
def show_all_markers():
  'Show all volume markers from the active marker set'

  ams = active_marker_set()
  if ams == None:
    return

  ams.show_markers(1)

# -----------------------------------------------------------------------------
#
def hide_all_markers():
  'Hide all volume markers from the active marker set'

  ams = active_marker_set()
  if ams == None:
    return

  ams.show_markers(0)

# -----------------------------------------------------------------------------
#
def active_marker_set():

  import VolumePath
  d = VolumePath.volume_path_dialog()
  if d:
    return d.active_marker_set
  return None

# -----------------------------------------------------------------------------
#
def set_white_background():
  set_background((1,1,1))
def set_gray_background():
  set_background((0.5,0.5,0.5))
def set_black_background():
  set_background((0,0,0))
def set_background(rgb):  
  from chimera import preferences, bgprefs
  preferences.set(bgprefs.BACKGROUND, bgprefs.BG_COLOR, rgb)

# -----------------------------------------------------------------------------
#
def glossy_lighting():
  'Toggle glossy lighting'
  import Lighting
  l = Lighting.get()
  from chimera import viewer
  q = {True:'normal', False:'glossy'}[viewer.haveShader()]
  l._setQualityFromParams(q)

# -----------------------------------------------------------------------------
#
def turn_x_90():
  chimera.runCommand('turn x 90')
def turn_y_90():
  chimera.runCommand('turn y 90')
def turn_z_90():
  chimera.runCommand('turn z 90')
  
# -----------------------------------------------------------------------------
#
def select_zone():
  from chimera import dialogs, ZoneDialog, tkgui
  d = dialogs.find(ZoneDialog.ZoneDialog.name)
  if d == None:
      d = dialogs.find(ZoneDialog.ZoneDialog.name, create = True)
      d.Close()
  tkgui.finishZone(d)
def show_zone_dialog():
  import chimera
  chimera.tkgui.startZone()

# -----------------------------------------------------------------------------
#
def main_window_focus():
  from chimera.tkgui import app
  # Make sure new dialogs are shown before returning focus to main window.
  app.update_idletasks()
  app.graphics.focus()
