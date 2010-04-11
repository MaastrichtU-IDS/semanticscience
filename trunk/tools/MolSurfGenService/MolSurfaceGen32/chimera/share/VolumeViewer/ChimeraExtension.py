import chimera.extension

# -----------------------------------------------------------------------------
#
class Volume_Viewer_EMO(chimera.extension.EMO):

  def name(self):
    return 'Volume Viewer'
  def description(self):
    return self.categoryDescriptions()['Volume Data']
  def categories(self):
    return self.categoryDescriptions().keys()
  def categoryDescriptions(self):
    # since we want to use specialized descriptions for certain categories...
    return {
      'Volume Data': 'Display volume data as surfaces, meshes or solids',
      # since showing DOCK scoring grids is only really useful for people
      # debugging DOCK... (grid values are before multiplying for ligands)
      #'Surface/Binding Analysis': 'Show DOCK scoring grids'
    }
  def icon(self):
    return self.path('volumeviewer.gif')
  def activate(self):
    self.module('volumedialog').show_volume_dialog()
    return None

# -----------------------------------------------------------------------------
# Register volume dialog and menu entry.
#
emo = Volume_Viewer_EMO(__file__)
chimera.extension.manager.registerExtension(emo)

# -----------------------------------------------------------------------------
#
def register_file_types():

  from VolumeData import file_types, electrostatics_types
  ftypes = filter(lambda ft: ft[1] not in electrostatics_types, file_types)
  for descrip, name, prefix_list, suffix_list, batch in ftypes:

    def open_cb(path, ftype=name):
      from VolumeViewer import open_volume_file
      drlist = open_volume_file(path, ftype, open_models = False)
      models = [dr.surface_model() for dr in drlist]
      drlist = None # Work around numpy bug #454
      return models

    suffixes = map(lambda s: '.' + s, suffix_list)      # fileInfo wants '.'
    import chimera
    fi = chimera.fileInfo
    fi.register(descrip, open_cb, suffixes, prefix_list,
                canDecompress = False, category = fi.VOLUME,
                batch = batch)

# -----------------------------------------------------------------------------
#
register_file_types()

# -----------------------------------------------------------------------------
# Register volume command.
#
def volume_cmd(cmdname, args):
    from VolumeViewer.volumecommand import volume_command
    volume_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('volume', volume_cmd, help = True)

# -----------------------------------------------------------------------------
# Delay importing module until function is actually called.
#
def function(name):
  def f(*args, **kw):
    from VolumeViewer import shortcuts
    getattr(shortcuts, name)(*args, **kw)
  return f

# -----------------------------------------------------------------------------
# Register keyboard shortcuts.
#
ks = (('bv', 'Make volume bounding selected atoms from periodic volume',
       'bounding_map'),
      ('cv', 'Clip volume', 'clip_volume'),
      ('ez', 'Copy map with erased zone', 'erase_zone'),
      ('fv', 'Change volume subregion to full data', 'full_volume'),
      ('Im', 'Invert map shown in volume viewer', 'invert_map'),
      ('ob', 'Toggle volume outline box', 'outline_box'),
      ('u8', 'Make MRC signed 8-bit volume unsigned',
       'mrc_signed8_to_unsigned8'),
      ('vh', 'Hide volume', 'hide_volume'),
      ('vR', 'Remove volume', 'remove_volume'),
      ('vs', 'Show volume', 'show_volume'),
      ('vv', 'Show volume viewer dialog', 'show_volume_dialog'),
      ('wv', 'Make writable copy of volume data', 'writable_volume'),
      ('zv', 'Copy map including only zone', 'zone_volume'),
      )
from Accelerators import add_accelerator
for keys, descrip, fname in ks:
  add_accelerator(keys, descrip, function(fname))
