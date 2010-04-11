from chimera.extension import EMO, manager

# -----------------------------------------------------------------------------
#
class Surface_Color_EMO(EMO):

	def name(self):
		return 'Surface Color'
	def description(self):
		return 'Color surface using volume data'
	def categories(self):
		return ['Volume Data']
	def icon(self):
		return self.path('gumball.png')
	def activate(self):
		self.module('gui').show_surface_color_dialog()
		return None

# -----------------------------------------------------------------------------
#
class Electrostatic_Surface_Color_EMO(EMO):

	def name(self):
		return 'Electrostatic Surface Coloring'
	def description(self):
		return 'Color surface using an electrostatic potential data file'
	def categories(self):
		return ['Surface/Binding Analysis']
	def icon(self):
		return self.path('gumball.png')
	def activate(self):
		m = self.module('gui')
		d = m.show_surface_color_dialog()
		d.use_electrostatics_colormap()
		return None

# -----------------------------------------------------------------------------
#
manager.registerExtension(Surface_Color_EMO(__file__))
manager.registerExtension(Electrostatic_Surface_Color_EMO(__file__))

# -----------------------------------------------------------------------------
#
def register_file_types():

  from VolumeData import file_types, electrostatics_types
  ftypes = filter(lambda ft: ft[1] in electrostatics_types, file_types)
  for descrip, name, prefix_list, suffix_list, batch in ftypes:
    def open_cb(path, ftype=name):
      from VolumeViewer import open_volume_file
      vlist = open_volume_file(path, ftype, open_models = False,
			       show_data = False, show_dialog = False)
      import chimera
      if len(vlist) > 0 and not chimera.nogui:
        from SurfaceColor.gui import show_surface_color_dialog
	d = show_surface_color_dialog()
	d.use_electrostatics_colormap()
	# TODO: Should set volume menu entry, but volumes are not yet opened.
      return vlist
    suffixes = map(lambda s: '.' + s, suffix_list)      # fileInfo wants '.'
    import chimera
    fi = chimera.fileInfo
    fi.register(descrip, open_cb, suffixes, prefix_list,
                canDecompress = False, category = fi.VOLUME, batch = batch)

# -----------------------------------------------------------------------------
#
register_file_types()

# -----------------------------------------------------------------------------
# Register scolor command.
#
def scolor_cmd(cmdname, args):
    from SurfaceColor import scolor
    scolor.scolor_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('scolor', scolor_cmd, scolor_cmd, help = True)
addCommand('scolour', scolor_cmd, scolor_cmd, help = True)
