# -----------------------------------------------------------------------------
# Dialog for coloring surfaces by volume data value.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Surface_Color_Dialog(ModelessDialog):

  title = 'Surface Color'
  name = 'surface color'
  buttons = ('Color', 'Uncolor', 'Options', 'Close',)
  help = 'ContributedSoftware/surfcolor/surfcolor.html'
  
  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight=1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid
    from chimera import widgets
    
    from SurfaceColor import colorable_surface_models
    sm = widgets.ModelOptionMenu(parent, labelpos = 'w',
                                 label_text = 'Color surface ',
                                 listFunc = colorable_surface_models,
                                 command = self.surface_menu_cb)
    sm.grid(row = row, column = 0, sticky = 'w')
    self.surface_menu = sm
    row = row + 1

    from SurfaceColor import coloring_methods
    methods = [cm.menu_name for cm in coloring_methods]
    csm = Hybrid.Option_Menu(parent, 'by ', *methods)
    csm.frame.grid(row = row, column = 0, sticky = 'w')
    self.color_source_menu = csm.variable
    csm.add_callback(self.color_source_changed_cb)
    row = row + 1
 
    from VolumeViewer import Volume_Menu
    vm = Volume_Menu(parent, 'file', open_button = 'browse...')
    vm.frame.grid(row = row, column = 0, sticky = 'w')
    self.volume_menu = vm
    row += 1
    
    oaf = Tkinter.Frame(parent)
    oaf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.origin_axis_frame = oaf

    oe = Hybrid.Entry(oaf, 'origin ', 8, '0 0 0')
    oe.frame.grid(row = 0, column = 0, sticky = 'w')
    self.origin_variable = oe.variable
    oe.entry.bind('<KeyPress-Return>', self.settings_changed_cb)

    cb = Tkinter.Button(oaf, text = 'center', command = self.set_center_cb)
    cb.grid(row = 0, column = 1, sticky = 'w')
    
    ae = Hybrid.Entry(oaf, 'axis ', 8, '0 0 1')
    ae.frame.grid(row = 0, column = 2, sticky = 'w')
    self.axis_frame = ae.frame
    self.axis_variable = ae.variable
    ae.entry.bind('<KeyPress-Return>', self.settings_changed_cb)

    cg = Colorwell_GUI(parent, 5, self.settings_changed_cb)
    cg.set_color_palette('rainbow')
    self.colormap_gui = cg
    self.colormap_gui.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    op = Hybrid.Popup_Panel(parent)
    opf = op.frame
    opf.grid(row = row, column = 0, sticky = 'news')
    opf.grid_remove()
    opf.columnconfigure(0, weight=1)
    self.options_panel = op.panel_shown_variable
    row += 1
    orow = 0

    cb = op.make_close_button(opf)
    cb.grid(row = orow, column = 1, sticky = 'ne')

    cf = Tkinter.Frame(opf)
    cf.grid(row = orow, column = 0, sticky = 'w')
    orow += 1

    color_counts = ('2', '3', '5', '10', '15', '20')
    cc = Hybrid.Option_Menu(cf, 'Colors ', *color_counts)
    cc.frame.grid(row = 0, column = 0, sticky = 'w')
    self.color_count = cc.variable
    self.color_count.set('5')
    cc.add_callback(self.change_color_count_cb)

    cpat = ('Rainbow', 'Gray', 'Red-Blue', 'Cyan-Maroon')
    cp = Hybrid.Option_Menu(cf, 'Palette', *cpat)
    cp.frame.grid(row = 0, column = 1, sticky = 'w')
    self.palette = cp.variable
    cp.add_callback(self.change_color_palette_cb)

    rc = Tkinter.Button(cf, text = 'Reverse', command = self.reverse_colors_cb)
    rc.grid(row = 0, column = 2, sticky = 'w')

    ckb = Tkinter.Button(opf, text="Create color key",
                         command = self.colormap_gui.color_key_cb)
    ckb.grid(row = orow, column = 0, sticky ='w')
    orow += 1

    dcf = Tkinter.Frame(opf)
    dcf.grid(row = orow, column = 0, sticky = 'w')
    orow += 1

    db = Tkinter.Button(dcf, text = 'Set',
                        command = self.show_default_colormap_values)
    db.grid(row = 0, column = 0, sticky = 'w')

    dt = Tkinter.Label(dcf, text = ' full range of surface values')
    dt.grid(row = 0, column = 1, sticky = 'w')

    so = Hybrid.Entry(opf, 'Surface offset ', 5, '1.4')
    so.frame.grid(row = orow, column = 0, sticky = 'w')
    self.surface_offset = so.variable
    self.surface_offset_frame = so.frame
    orow += 1
    so.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    
    ocf = Tkinter.Frame(opf)
    ocf.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.outside_color_frame = ocf

    ocl = Tkinter.Label(ocf, text = 'Color outside volume')
    ocl.grid(row = 0, column = 0, sticky = 'w')

    outside_color = (.5,.5,.5,1)
    from CGLtk.color import ColorWell
    cw = ColorWell.ColorWell(ocf)
    cw.showColor(outside_color)
    cw.grid(row = 0, column = 1, sticky = 'w')
    self.outside_color = cw

    co = Hybrid.Checkbutton(opf, 'Only color sliced surface face', 0)
    co.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.color_caps_only = co.variable

    ppc = Hybrid.Checkbutton(opf, 'Per-pixel coloring', False)
    ppc.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.per_pixel_color = ppc.variable
    
    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

    # Show current coloring if one already exists from session restore.
    self.surface_menu_cb()

    # Show axix, origin, volume widgets if appropriate.
    self.color_source_changed_cb()
    
  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()

  # ---------------------------------------------------------------------------
  #
  def Color(self):

    self.settings_changed_cb()

  # ---------------------------------------------------------------------------
  #
  def Uncolor(self):

    self.stop_recoloring_cb()
    
  # ---------------------------------------------------------------------------
  #
  def Options(self):

    self.options_panel.set(not self.options_panel.get())

  # ---------------------------------------------------------------------------
  # Update gui to show coloring parameters being used for selected surface.
  #
  def surface_menu_cb(self, text = None):

    surface = self.chosen_surface()
    if surface == None:
      return

    import SurfaceColor
    color_source, caps_only = SurfaceColor.surface_coloring(surface)
    if color_source == None:
      return

    cmap = color_source.colormap

    self.color_source_menu.set(color_source.menu_name)

    if color_source.uses_volume_data:
      self.volume_menu.set_volume(color_source.volume)
    if color_source.uses_origin:
      self.origin_variable.set('%g %g %g' % color_source.origin)
    if color_source.uses_axis:
      self.axis_variable.set('%g %g %g' % color_source.axis)

    self.color_count.set(len(cmap.colors))
    self.colormap_gui.set_colormap(cmap.data_values, cmap.colors)

    if cmap.color_no_value:
      self.outside_color.showColor(cmap.color_no_value)

    self.color_caps_only.set(caps_only)

    if hasattr(color_source, 'per_pixel_coloring'):
      self.per_pixel_color.set(color_source.per_pixel_coloring)

  # ---------------------------------------------------------------------------
  #
  def set_center_cb(self):

    surface = self.chosen_surface()
    if surface == None:
      self.message('Select a surface')
      return

    have_bbox, box = surface.bbox()
    if not have_bbox:
      self.message('Surface has no bounding box')
      return
    
    origin = box.center().data()
    self.origin_variable.set('%.4f %.4f %.4f' % origin)

  # ---------------------------------------------------------------------------
  #
  def change_color_count_cb(self):

    cc = self.color_count.get()
    n = int(cc)
    self.colormap_gui.set_color_count(n)
    
  # ---------------------------------------------------------------------------
  #
  def change_color_palette_cb(self):

    p = self.palette.get()
    pname = {'Rainbow': 'rainbow',
             'Gray': 'grayscale',
             'Red-Blue': 'red-white-blue',
             'Cyan-Maroon': 'cyan-white-maroon',
             }
    self.colormap_gui.set_color_palette(pname[p])

  # ---------------------------------------------------------------------------
  #
  def reverse_colors_cb(self):

    self.colormap_gui.reverse_colors()

  # ---------------------------------------------------------------------------
  #
  def settings_changed_cb(self, event = None):

    self.message('')
    
    surface = self.chosen_surface()
    if surface == None:
        self.message('Select a surface')
        return

    color_source = self.color_source()
    if color_source.uses_volume_data and color_source.volume is None:
        self.message('No %s data specified' % color_source.volume_name)
        return

    if color_source.colormap is None:
      if self.colormap_gui.no_colormap_values():
        self.show_default_colormap_values()
        color_source.set_colormap(self.colormap())
      if color_source.colormap is None:
        self.message('No colormap specified')
        return

    caps_only = self.color_caps_only.get()

    import SurfaceColor
    SurfaceColor.color_surface(surface, color_source, caps_only,
                               auto_update = True)
      
  # ---------------------------------------------------------------------------
  #
  def stop_recoloring_cb(self, event = None):

    surface = self.chosen_surface()
    if surface == None:
        self.message('Select a surface')
        return

    import SurfaceColor
    SurfaceColor.stop_coloring_surface(surface)
      
  # ---------------------------------------------------------------------------
  #
  def chosen_surface(self):

    sm = self.surface_menu
    surface = sm.getvalue()
    return surface
      
  # ---------------------------------------------------------------------------
  #
  def color_source_changed_cb(self):

    color_source = self.color_source()
    self.set_origin_axis_visibility(color_source.uses_origin,
                                    color_source.uses_axis)
    self.set_volume_visibility(color_source)
      
  # ---------------------------------------------------------------------------
  #
  def set_volume_visibility(self, color_source):

    show_volume = color_source.uses_volume_data
    if show_volume:
      fname = color_source.volume_name + ' file '
      self.volume_menu.menu.configure(label_text = fname)

    show_frame(self.volume_menu.frame, show_volume)
    show_frame(self.outside_color_frame, show_volume)
    from SurfaceColor import Electrostatic_Color
    show_frame(self.surface_offset_frame,
               isinstance(color_source, Electrostatic_Color))
      
  # ---------------------------------------------------------------------------
  #
  def set_origin_axis_visibility(self, show_origin, show_axis):

    show_frame(self.origin_axis_frame, show_origin)
    show_frame(self.axis_frame, show_axis)
      
  # ---------------------------------------------------------------------------
  #
  def show_default_colormap_values(self):

    color_source = self.color_source()

    surface = self.chosen_surface()
    if surface == None:
      self.message('No surface selected')
      return

    caps_only = self.color_caps_only.get()
    import SurfaceColor
    value_range = SurfaceColor.surface_value_range(surface,
                                                   color_source.value_range,
                                                   caps_only)
    if value_range[0] == None:
      self.message('No data values for surface')
    else:
      self.colormap_gui.show_default_colormap(value_range)
      
  # ---------------------------------------------------------------------------
  #
  def color_source(self):

    csname = self.color_source_menu.get()
    from SurfaceColor import coloring_methods
    csclass = [cm for cm in coloring_methods if cm.menu_name == csname][0]
    cs = csclass()

    cmap = self.colormap()
    if cmap:
      cs.set_colormap(cmap)

    if cs.uses_volume_data:
      cs.set_volume(self.volume_menu.volume())

    if cs.uses_origin:
      o = parse_vector(self.origin_variable.get(), default = (0,0,0))
      cs.set_origin(o)

    if cs.uses_axis:
      a = parse_vector(self.axis_variable.get(), default = (0,0,1))
      cs.set_axis(a)

    cs.per_pixel_coloring = self.per_pixel_color.get()

    from SurfaceColor import Electrostatic_Color
    if isinstance(cs, Electrostatic_Color):
      from CGLtk import Hybrid
      cs.offset = Hybrid.float_variable_value(self.surface_offset, 0)

    return cs
      
  # ---------------------------------------------------------------------------
  #
  def colormap(self):

    cmap = self.colormap_gui.colormap(self.message)     # List of (value,color)
    if len(cmap) < 2:
        return None
      
    data_values = [vc[0] for vc in cmap]
    rgba_colors = [vc[1] for vc in cmap]

    import SurfaceColor
    cmap = SurfaceColor.Color_Map(data_values, rgba_colors,
                                  color_no_value = self.outside_color.rgba)
    return cmap
      
  # ---------------------------------------------------------------------------
  #
  def use_electrostatics_colormap(self):

    from SurfaceColor import Electrostatic_Color
    self.color_source_menu.set(Electrostatic_Color.menu_name)

    self.color_count.set('3')
    values = (-10, 0, 10)
    colors = ((1,0,0,1), (1,1,1,1), (0,0,1,1))
    self.colormap_gui.set_colormap(values, colors)

# -----------------------------------------------------------------------------
#
class Colorwell_GUI:

  def __init__(self, parent, n, colormap_changed_cb):

    import Tkinter
    f = Tkinter.Frame(parent)
    self.frame = f

    self.n = 0
    self.colorwells = []
    self.entry_fields = []

    self.colormap_changed_cb = colormap_changed_cb

    self.set_color_count(n)
    
  # ---------------------------------------------------------------------------
  #
  def show(self):
    self.frame.grid()
  def hide(self):
    self.frame.grid_remove()

  # ---------------------------------------------------------------------------
  #
  def set_color_count(self, n):

    if n == self.n:
      return

    if n > len(self.colorwells):
      # Add more color buttons
      for c in range(len(self.colorwells), n):
        from CGLtk.color import ColorWell
        cw = ColorWell.ColorWell(self.frame)
        cw.grid(row = 2*(c/5), column = c%5)
        self.colorwells.append(cw)
        from CGLtk import Hybrid
        e = Hybrid.Entry(self.frame, '', 5, '')
        e.frame.grid(row = 2*(c/5)+1, column = c%5)
        e.entry.bind('<KeyPress-Return>', self.colormap_changed_cb)
        self.entry_fields.append(e)

    # Map additional colorwells
    for c in range(self.n, n):
      self.colorwells[c].grid()
      self.entry_fields[c].frame.grid()

    # Unmap extra colorwells
    for c in range(n, self.n):
      self.colorwells[c].grid_remove()
      self.entry_fields[c].frame.grid_remove()

    self.n = n
    
  # ---------------------------------------------------------------------------
  #
  def set_color_palette(self, name):

    from SurfaceColor import standard_color_palettes as scp
    rgba = scp.get(name, None)
    if not rgba is None:
      self.set_color_ramp(rgba)
    
  # ---------------------------------------------------------------------------
  #
  def reverse_colors(self):

    rgba = [self.colorwells[c].rgba for c in range(self.n)]
    rgba.reverse()
    self.set_color_ramp(rgba)
    
  # ---------------------------------------------------------------------------
  #
  def set_color_ramp(self, rgba_ramp):

    rn = len(rgba_ramp)
    rvalues = values = map(lambda c: float(c)/(rn-1), range(rn))
    n = self.n
    values = map(lambda c: float(c)/(n-1), range(n))
    from SurfaceColor import interpolate_colormap
    rgba = interpolate_colormap(values, rvalues, rgba_ramp,
                                rgba_ramp[-1], rgba_ramp[0])
    for c in range(n):
      self.colorwells[c].showColor(tuple(rgba[c]))
    
  # ---------------------------------------------------------------------------
  #
  def set_colors(self, rgba_list):

    for c in range(len(rgba_list)):
      self.colorwells[c].showColor(tuple(rgba[c]))

  # ---------------------------------------------------------------------------
  #
  def no_colormap_values(self):

    for c in range(self.n):
      v = self.entry_fields[c].variable
      if v.get().strip():
        return False
    return True

  # ---------------------------------------------------------------------------
  #
  def colormap(self, message_cb):

    cmap = []
    for c in range(self.n):
      v = self.entry_fields[c].variable
      if v.get().strip() == '':
        continue                    # unused color
      from CGLtk import Hybrid
      dv = Hybrid.float_variable_value(v)
      if dv == None:
        message_cb('Data value "%s" is not a number' % v.get())
        continue
      cw = self.colorwells[c]
      cmap.append((dv, cw.rgba))
    cmap.sort()
    return cmap
      
  # ---------------------------------------------------------------------------
  #
  def set_colormap(self, values, colors):

    n = min(len(values), self.n)
    for k in range(n):
      v = self.entry_fields[k].variable
      v.set(str(values[k]))
      cw = self.colorwells[k]
      cw.showColor(colors[k])

    for k in range(n, self.n):
      v = self.entry_fields[k].variable
      v.set('')
      
  # ---------------------------------------------------------------------------
  #
  def show_default_colormap(self, value_range):

    dmin, dmax = value_range
    for k in range(self.n):
      f = float(k) / (self.n-1)
      val = dmin + f * (dmax - dmin)
      v = self.entry_fields[k].variable
      v.set('%.4g' % val)
      
  # ---------------------------------------------------------------------------
  #
  def color_key_cb(self, *args):
    if self.n < 2:
      raise chimera.UserError("At least two colors needed to create key")
    from Ilabel.gui import IlabelDialog
    from chimera import dialogs
    d = dialogs.display(IlabelDialog.name)
    d.keyConfigure([(w.rgba, h.variable.get()) for w, h in zip(self.colorwells,
                      self.entry_fields)[:self.n]])
                 
# -----------------------------------------------------------------------------
#
def show_frame(frame, show):

  if show:
    frame.grid()
  else:
    frame.grid_remove()
                 
# -----------------------------------------------------------------------------
#
def parse_vector(string, default = None):

  fields = string.split()
  if len(fields) != 3:
    return default

  try:
    v = map(float, fields)
  except ValueError:
    return default

  return v

# -----------------------------------------------------------------------------
#
def surface_color_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Surface_Color_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_surface_color_dialog():

  from chimera import dialogs
  return dialogs.display(Surface_Color_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Surface_Color_Dialog.name, Surface_Color_Dialog, replace = 1)
