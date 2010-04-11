# -----------------------------------------------------------------------------
# Histogram widget and interactive canvas ramp display.
#
import Tkinter

# -----------------------------------------------------------------------------
#
class Histogram:

  def __init__(self, canvas):

    self.canvas = canvas

  # ---------------------------------------------------------------------------
  #
  def show_data(self, heights):

    c = self.canvas
    c.delete('bar')
    c.update_idletasks()                          # determine canvas size
    cheight = c.winfo_fpixels(c['height'])
    cborder = c.winfo_fpixels(c['borderwidth'])
    
    bins = len(heights)
    max_height = max(heights)
    hscale = float(cheight) / max_height
    bottom = cheight + cborder - 1
    for b in range(bins):
      x = cborder + b
      h = int(hscale * heights[b])
      id = c.create_line(x, bottom, x, bottom-h, tags = ('bar',))
      c.tag_lower(id)                           # keep bars below marker lines

# -----------------------------------------------------------------------------
# Draw a set of movable markers on a canvas.  The markers can be moved with
# the mouse.  They can be drawn as vertical lines ('line' type) or as small
# boxes ('box' type).  Each marker has a color.  Markers can be added or
# deleted with ctrl-button-1.  A callback is invoked with no arguments when
# user mouse interaction selects, moves, adds or removes a marker.
#
# This was designed for display and control of theshold levels shown on a
# histogram.
#
class Markers:

  def __init__(self, canvas, canvas_box, marker_type, new_marker_color,
	       connect_markers, callback):

    self.canvas = canvas
    self.canvas_box = canvas_box
    self.marker_type = marker_type	# 'line' or 'box'
    self.box_size = 2
    self.new_marker_color = new_marker_color

    self.connect_markers = connect_markers
    self.connect_color = 'yellow'
    self.connect_ids = []

    self.callback = callback

    self.markers = []

    self.user_x_range = (0, 1)
    self.user_y_range = (0, 1)

    self.drag_marker_index = None
    self.last_mouse_xy = None

    self.shown = 0
    self.show(1)

    canvas.bind("<Control-ButtonPress-1>", self.add_or_delete_marker_cb,
		add = 1)
    canvas.bind("<ButtonPress-1>", self.select_marker_cb, add = 1)
    canvas.bind("<Button1-Motion>", self.move_marker_cb, add = 1)

  # ---------------------------------------------------------------------------
  #
  def show(self, show):

    if show and not self.shown:
      self.shown = show
      self.update_plot()
    elif not show and self.shown:
      self.unplot_markers()
      self.shown = show
    
  # ---------------------------------------------------------------------------
  #
  def plot_markers(self):

    c = self.canvas
    bs = self.box_size
    x0, y1, x1, y0 = self.canvas_box
    
    for m in self.markers:
      if m.id == None:
	x, y = self.user_xy_to_canvas_xy(m.xy)
	color = tk_color_name(m.rgba[:3])
	if self.marker_type == 'line':
	  m.id = c.create_rectangle(x-bs, y0, x+bs, y1, fill = color)
	elif self.marker_type == 'box':
	  m.id = c.create_rectangle(x-bs, y-bs, x+bs, y+bs, fill = color)

  # ---------------------------------------------------------------------------
  #
  def unplot_markers(self):

    c = self.canvas
    for m in self.markers:
      m.unplot(c)

    for i in self.connect_ids:
      c.delete(i)
    self.connect_ids = []
    
  # ---------------------------------------------------------------------------
  # canvas_box = (xmin, ymin, xmax, ymax)
  # The xmin and xmax values should give the positions corresponding to the
  # values passed to set_user_x_range().
  #
  def set_canvas_box(self, canvas_box):

    if canvas_box != self.canvas_box:
      self.canvas_box = canvas_box
      self.update_plot()
    
  # ---------------------------------------------------------------------------
  #
  def set_user_x_range(self, xmin, xmax):

    self.user_x_range = (xmin, xmax)
    self.update_plot()
    
  # ---------------------------------------------------------------------------
  #
  def canvas_xy_to_user_xy(self, cxy):

    xmin, ymin, xmax, ymax = self.canvas_box
    fx = float(cxy[0] - xmin) / (xmax - xmin)
    uxmin, uxmax = self.user_x_range
    ux = (1-fx) * uxmin + fx * uxmax
    fy = float(cxy[1] - ymin) / (ymax - ymin)
    uymin, uymax = self.user_y_range
    uy = (1-fy) * uymax + fy * uymin
    return ux, uy

  # ---------------------------------------------------------------------------
  #
  def user_xy_to_canvas_xy(self, uxy):

    xmin, ymin, xmax, ymax = self.canvas_box

    uxmin, uxmax = self.user_x_range
    fx = (uxy[0] - uxmin) / (uxmax - uxmin)
    cx = (1-fx) * xmin + fx * xmax

    uymin, uymax = self.user_y_range
    fy = (uxy[1] - uymin) / (uymax - uymin)
    cy = (1-fy) * ymax + fy * ymin

    return cx, cy
  
  # ---------------------------------------------------------------------------
  #
  def set_markers(self, markers):

    for m in self.markers:
      m.unplot(self.canvas)

    self.markers = markers
    self.update_plot()
  
  # ---------------------------------------------------------------------------
  #
  def clamp_canvas_xy(self, xy):
    
    x, y = xy
    xmin, ymin, xmax, ymax = self.canvas_box

    if x < xmin:      x = xmin
    elif x > xmax:    x = xmax
    
    if y < ymin:      y = ymin
    elif y > ymax:    y = ymax

    return [x, y]
  
  # ---------------------------------------------------------------------------
  #
  def update_plot(self):

    if not self.shown:
      return

    self.plot_markers()

    self.update_marker_coordinates()

    if self.connect_markers:
      self.update_connections()
  
  # ---------------------------------------------------------------------------
  #
  def update_marker_coordinates(self):

    c = self.canvas
    x0, y0, x1, y1 = self.canvas_box
    bs = self.box_size

    for m in self.markers:
      cxy = self.user_xy_to_canvas_xy(m.xy)
      x, y = self.clamp_canvas_xy(cxy)
      if self.marker_type == 'line':
	c.coords(m.id, x-bs, y0, x+bs, y1)
      elif self.marker_type == 'box':
	c.coords(m.id, x-bs, y-bs, x+bs, y+bs)
  
  # ---------------------------------------------------------------------------
  #
  def update_connections(self):

    xy_list = map(lambda m: m.xy, self.markers)
    cxy_list = map(self.user_xy_to_canvas_xy, xy_list)
    cxy_list.sort()
    cxy_list = map(self.clamp_canvas_xy, cxy_list)

    c = self.canvas
    color = self.connect_color
    ids = []
    for k in range(len(cxy_list) - 1):
      x0, y0 = cxy_list[k]
      x1, y1 = cxy_list[k+1]
      id = c.create_line(x0, y0, x1, y1, fill = color)
      ids.append(id)

    for id in self.connect_ids:
      c.delete(id)

    self.connect_ids = ids

    for m in self.markers:
      c.tag_raise(m.id)

  # ---------------------------------------------------------------------------
  #
  def add_or_delete_marker_cb(self, event):

    if not self.shown:
      return

    range = 3
    i = self.closest_marker_index(event.x, event.y, range)

    if i == None:
      cxy = self.clamp_canvas_xy((event.x, event.y))
      xy = self.canvas_xy_to_user_xy(cxy)
      sm = self.selected_marker()
      if sm:
	color = sm.rgba
      else:
	color = self.new_marker_color
      m = Marker(xy, color)
      self.markers.append(m)
      self.last_mouse_xy = xy
      self.drag_marker_index = len(self.markers) - 1
    else:
      self.drag_marker_index = None
      self.markers[i].unplot(self.canvas)
      del self.markers[i]

    self.update_plot()

    if self.callback:
      self.callback()

  # ---------------------------------------------------------------------------
  #
  def select_marker_cb(self, event):

    if not self.shown:
      return

    range = 3
    i = self.closest_marker_index(event.x, event.y, range)
    self.drag_marker_index = i

    if i == None:
      return

    self.last_mouse_xy = self.canvas_xy_to_user_xy((event.x, event.y))

    if self.callback:
      self.callback()

  # ---------------------------------------------------------------------------
  #
  def closest_marker_index(self, x, y, range):

    marker_ids = map(lambda m: m.id, self.markers)
    c = self.canvas
    close = c.find('closest', x, y, range)
    for c in close:
      if c in marker_ids:
        return marker_ids.index(c)

    return None

  # ---------------------------------------------------------------------------
  #
  def move_marker_cb(self, event):

    if (not self.shown or
	self.last_mouse_xy == None or
	self.drag_marker_index == None or
	self.drag_marker_index >= len(self.markers)):
      return

    mouse_xy = self.canvas_xy_to_user_xy((event.x, event.y))
    dx = mouse_xy[0] - self.last_mouse_xy[0]
    dy = mouse_xy[1] - self.last_mouse_xy[1]
    self.last_mouse_xy = mouse_xy

    shift_mask = 1
    if event.state & shift_mask:
      dx = .1 * dx
      dy = .1 * dy

    #
    # Don't allow dragging out of the canvas box.
    #
    m = self.markers[self.drag_marker_index]
    xy = (m.xy[0] + dx, m.xy[1] + dy)
    cxy = self.user_xy_to_canvas_xy(xy)
    cxy = self.clamp_canvas_xy(cxy)
    xy = self.canvas_xy_to_user_xy(cxy)
    m.xy = xy

    self.update_plot()

    if self.callback:
      self.callback()
    
  # ---------------------------------------------------------------------------
  #
  def selected_marker(self):

    if (self.drag_marker_index == None or
	self.drag_marker_index >= len(self.markers)):
      if len(self.markers) > 0:
	return self.markers[0]
      else:
	return None
    return self.markers[self.drag_marker_index]
    
# -----------------------------------------------------------------------------
#
class Marker:

  def __init__(self, xy, color):

    self.xy = xy
    self.rgba = color
    self.id = None
  
  # ---------------------------------------------------------------------------
  #
  def set_color(self, rgba, canvas):

    if rgba == self.rgba:
      return

    self.rgba = rgba
    if self.id != None:
      color = tk_color_name(rgba[:3])
      canvas.itemconfigure(self.id, fill = color)
  
  # ---------------------------------------------------------------------------
  #
  def unplot(self, canvas):

    if self.id != None:
      canvas.delete(self.id)
      self.id = None
    
# -----------------------------------------------------------------------------
#
def tk_color_name(rgb):

  rgb8 = map(lambda c: int(256 * c), rgb)
  rgb8 = map(lambda c: max(c, 0), rgb8)
  rgb8 = map(lambda c: min(c, 255), rgb8)
  rgb8 = tuple(rgb8)
  return '#%02x%02x%02x' % rgb8
