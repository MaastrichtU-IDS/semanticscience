# -----------------------------------------------------------------------------
# Dialog for coloring connected pieces of a surface chosen with mouse.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Blob_Picker_Dialog(ModelessDialog):

  title = 'Measure and Color Blobs'
  name = 'measure and color blobs'
  buttons = ('Close',)
  help = 'ContributedSoftware/pickblobs/pickblobs.html'
  
  def fillInUI(self, parent):

    self.default_color = (0,0,0.8,1)
    
    t = parent.winfo_toplevel()
    self.toplevel_widget = t
    t.withdraw()

    parent.columnconfigure(0, weight = 1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    mmf = Tkinter.Frame(parent)
    mmf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    mb = Hybrid.Option_Menu(mmf, 'Use mouse ',
                            'button 1', 'button 2', 'button 3',
                            'ctrl button 1', 'ctrl button 2', 'ctrl button 3')
    mb.variable.set('ctrl button 3')
    mb.frame.grid(row = 0, column = 0, sticky = 'w')
    mb.add_callback(self.bind_mouse_button_cb)
    self.mouse_button = mb
    
    mbl = Tkinter.Label(mmf, text = ' to choose blobs')
    mbl.grid(row = 0, column = 1, sticky = 'w')

    crf = Tkinter.Frame(parent)
    crf.grid(row = row, column = 0, sticky = 'ew')
    crf.columnconfigure(1, weight = 1)
    row = row + 1

    cl = Tkinter.Label(crf, text = 'Color blob ')
    cl.grid(row = 0, column = 0, sticky = 'w')
    
    from CGLtk.color import ColorWell
    sc = ColorWell.ColorWell(crf, color = self.default_color)
    sc.grid(row = 0, column = 1, sticky = 'w')
    self.blob_color = sc
    
    msg = Tkinter.Label(parent, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg
    
    callbacks = (self.mouse_down_cb, self.mouse_drag_cb, self.mouse_up_cb)
    icon = self.mouse_mode_icon('pickblob.gif')
    from chimera import mousemodes
    mousemodes.addFunction('pick blobs', callbacks, icon)

    self.bind_mouse_button_cb()
      
  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()

  # -------------------------------------------------------------------------
  #
  def mouse_mode_icon(self, filename):

    import os.path
    icon_path = os.path.join(os.path.dirname(__file__), filename)
    from PIL import Image
    image = Image.open(icon_path)
    from chimera import chimage, tkgui
    icon = chimage.get(image, tkgui.app)
    return icon

  # -------------------------------------------------------------------------
  #
  def mouse_down_cb(self, viewer, event):

    self.color_and_measure(event.x, event.y)

  # -------------------------------------------------------------------------
  #
  def color_and_measure(self, window_x, window_y):
    
    from VolumeViewer import slice
    xyz_in, xyz_out = slice.clip_plane_points(window_x, window_y)

    import PickBlobs
    smlist = PickBlobs.surface_models()
    p, vlist, tlist = PickBlobs.picked_surface_component(smlist, xyz_in, xyz_out)
    if p is None:
      self.message('No intercept with surface.')
      return
    
    PickBlobs.color_blob(p, vlist, self.blob_color.rgba)

    # Report enclosed volume and area
    from MeasureVolume import enclosed_volume, surface_area
    varray, tarray = PickBlobs.blob_geometry(p, vlist, tlist)
    v, h = enclosed_volume(varray, tarray)
    if v == None:
      vstr = 'undefined (non-oriented surface)'
    else:
      vstr = '%.5g' % v
      if h > 0:
        vstr += ' (%d holes)' % h
    area = surface_area(varray, tarray)

    s = p.model
    msg = ('Surface %s (%s) piece: volume = %s, area = %.5g'
           % (s.name, s.oslIdent(), vstr, area))
    self.message(msg)
    from chimera.replyobj import info, status
    info(msg + '\n')
    status(msg)
      
  # -------------------------------------------------------------------------
  #
  def mouse_drag_cb(self, viewer, event):
    pass
  def mouse_up_cb(self, viewer, event):
    pass
    
  # ---------------------------------------------------------------------------
  #
  def bind_mouse_button_cb(self):

    bname = self.mouse_button.variable.get()
    button, modifiers = self.button_spec(bname)
    from chimera import mousemodes
    mousemodes.setButtonFunction(button, modifiers, 'pick blobs')

  # ---------------------------------------------------------------------------
  #
  def button_spec(self, bname):

    name_to_bspec = {'button 1':('1', []), 'ctrl button 1':('1', ['Ctrl']),
                     'button 2':('2', []), 'ctrl button 2':('2', ['Ctrl']),
                     'button 3':('3', []), 'ctrl button 3':('3', ['Ctrl'])}
    bspec = name_to_bspec[bname]
    return bspec

# -----------------------------------------------------------------------------
#
def blob_picker_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Blob_Picker_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_blob_picker_dialog():

  from chimera import dialogs
  return dialogs.display(Blob_Picker_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Blob_Picker_Dialog.name, Blob_Picker_Dialog, replace = 1)
