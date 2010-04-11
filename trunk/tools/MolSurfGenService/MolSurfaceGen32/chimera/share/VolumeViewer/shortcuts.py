# -----------------------------------------------------------------------------
#
def show_volume():
  'Show active volume viewer volume'
  from volumedialog import active_volume
  v = active_volume()
  if v:
    if v.representation is None:
      v.set_representation('surface')
    v.initialize_thresholds()
    v.show()

# -----------------------------------------------------------------------------
#
def hide_volume():
  'Hide active volume viewer volume'
  from volumedialog import active_volume
  v = active_volume()
  if v:
    v.unshow()

# -----------------------------------------------------------------------------
#
def full_volume():
  'Change volume subregion to show full data'
  from volumedialog import active_volume
  v = active_volume()
  if v:
    ijk_min = (0,0,0)
    ijk_max = [n-1 for n in v.data.size]
    v.new_region(ijk_min, ijk_max, show = v.shown())

# -----------------------------------------------------------------------------
#
def writable_volume():

  from volumedialog import active_volume
  v = active_volume()
  if v:
    v.writable_copy(require_copy = True)

# -----------------------------------------------------------------------------
#
def remove_volume():
  'Remove active volume viewer volume'
  from volumedialog import active_volume
  v = active_volume()
  if v:
    v.close()

# -----------------------------------------------------------------------------
#
from volumedialog import show_volume_dialog

# -----------------------------------------------------------------------------
#
def mrc_signed8_to_unsigned8():

  from volumedialog import active_volume
  v = active_volume()
  if v == None:
    from chimera.replyobj import status
    status('No volume shown in volume viewer dialog.')
    return

  data = v.data
  if not hasattr(data, 'signed8_to_unsigned8'):
    from chimera.replyobj import status
    status('Volume is not MRC format.')
    return

  from numpy import int8
  if data.value_type != int8:
    from chimera.replyobj import status
    status('MRC volume is not 8-bit integers.')
    return

  data.signed8_to_unsigned8()

  v.show()

# -----------------------------------------------------------------------------
#
def invert_map():

  from volumedialog import active_volume
  v = active_volume()
  if v is None:
    return
  wv = v.writable_copy()

  m = wv.data.full_matrix()
  from VolumeData import invert_matrix
  invert_matrix(m)
  wv.data.values_changed()
  wv.show()

# ----------------------------------------------------------------------------
# Create and show bounding map for selected atoms using active volume.
#
def bounding_map(pad = 5.0):

    from chimera.selection import currentAtoms
    atoms = currentAtoms()
    if len(atoms) == 0:
        from chimera.replyobj import status
        status('No atoms selected')
        return

    from volumedialog import active_volume
    v = active_volume()
    if v is None:
        from chimera.replyobj import status
        status('No volume shown in volume dialog')
        return

    from volume import map_covering_atoms
    bv = map_covering_atoms(atoms, pad, v)
    bv.show()
    v.show(show = False)

# -----------------------------------------------------------------------------
#
def erase_zone():

  zone_volume(outside = True)

# -----------------------------------------------------------------------------
#
def zone_volume(outside = False):

  from volumedialog import active_volume
  v = active_volume()
  if v is None:
    from chimera.replyobj import status
    status('No volume shown in volume dialog')
    return

  mv = v.copy_zone(outside)
  if mv is None:
    from chimera.replyobj import status
    status('No zone for volume %s' % v.name)

# -----------------------------------------------------------------------------
# Turn on per-model clipping for active volume.
#
def clip_volume():

  from volumedialog import active_volume
  v = active_volume()
  if v:
    if v.useClipPlane:
      v.useClipPlane = False
    else:
      from chimera import tkgui
      tkgui.setClipModel(v)

# -----------------------------------------------------------------------------
#
def outline_box():
  'Toggle outline boxes for selected volumes'
  from VolumeViewer import volume_list, Volume
  from chimera import selection
  if selection.currentEmpty():
    vlist = volume_list()
  else:
    vlist = [v for v in selection.currentGraphs() if isinstance(v, Volume)]
  for v in vlist:
    if v.display:
      shown = v.rendering_options.show_outline_box
      v.set_parameters(show_outline_box = not shown)
      v.show()
