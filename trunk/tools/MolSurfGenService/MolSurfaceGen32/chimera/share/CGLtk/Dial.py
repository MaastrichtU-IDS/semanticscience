# -----------------------------------------------------------------------------
# Dial widget that shows a turnable knob for setting an angle.
#
import math
import Tkinter

# -----------------------------------------------------------------------------
# Radius is in any Tk-acceptable format.
# Command callback takes an angle argument (degrees).
#
class Dial:

  def __init__(self, parent, radius='.5i', command=None, initAngle=0.0,
				zeroAxis='x', rotDir='counterclockwise',
				fill=None, outline='black', line='black'):

    self.command = command
    self.radius = parent.winfo_pixels(radius)
    self.bump_size = .2 * self.radius
    rpb = self.radius + self.bump_size
    self.center_xy = (rpb, rpb)
    self.drag_from_angle = None

    s = int(2 * (self.radius + self.bump_size))
    c = Tkinter.Canvas(parent, width = s, height = s)
    c.bind('<ButtonPress-1>', self.button_press_cb)
    c.bind('<Button1-Motion>', self.pointer_drag_cb)
    c.bind('<ButtonRelease-1>', self.button_release_cb)
    cx, cy = self.center_xy
    r = self.radius
    kw = {}
    if fill is not None:
    	kw['fill'] = fill
    if outline is not None:
    	kw['outline'] = outline
    apply(c.create_oval, (cx - r, cy - r, cx + r, cy + r), kw)
    bs = self.bump_size
    kw = {'width': bs}
    if line is not None:
    	kw['fill'] = line
    id = apply(c.create_line, (cx, cy, cx + r + bs, cy), kw)
    self.line_id = id
    self.canvas = c
    self.widget = c
    self.rotDir = rotDir
    self.zeroAxis = zeroAxis
    self.setAngle(initAngle, doCallback=0)
  
  # ---------------------------------------------------------------------------
  #
  def button_press_cb(self, event):

    try:
      self.drag_from_angle = self.event_angle(event)
    except ValueError:
      pass
    
  # ---------------------------------------------------------------------------
  #
  def pointer_drag_cb(self, event):

    if self.drag_from_angle == None:
      return

    try:
      a = self.event_angle(event)
    except ValueError:
      pass
    else:
      self.drag_from_angle = a
      self.set_angle(a)

  # ---------------------------------------------------------------------------
  #
  def button_release_cb(self, event):

    if self.drag_from_angle == None:
      return

    try:
      a = self.event_angle(event)
    except ValueError:
      pass
    else:
      delta = a - self.drag_from_angle
      self.drag_from_angle = None
      self.set_angle(a)

  # ---------------------------------------------------------------------------
  #
  def event_angle(self, event):
    # math.atan2 may raise ValueError if dx and dy are zero.
    (x, y) = canvas_coordinates(self.canvas, event)
    (dx, dy) = (x - self.center_xy[0], self.center_xy[1] - y)
    rad = math.atan2(dy, dx)
    deg = 180 * rad / math.pi
    if self.zeroAxis == 'y':
    	deg = deg + 270
    elif self.zeroAxis == '-x':
    	deg = deg + 180
    elif self.zeroAxis == '-y':
    	deg = deg + 90

    if self.rotDir == 'clockwise':
    	deg = 360 - deg

    while deg > 180.0:
    	deg = deg - 360
    while deg <= -180.0:
    	deg = deg + 360
    return deg
  
  # ---------------------------------------------------------------------------
  #
  def set_angle(self, a, doCallback=1):

    #
    # Move dial pointer
    #
    cx, cy = self.center_xy
    d = self.radius + self.bump_size
    cartesian = a
    if self.rotDir == 'clockwise':
    	cartesian = 360 - cartesian
    if self.zeroAxis == 'y':
    	cartesian = cartesian + 90
    elif self.zeroAxis == '-x':
    	cartesian = cartesian + 180
    elif self.zeroAxis == '-y':
    	cartesian = cartesian + 270
    while cartesian > 180.0:
    	cartesian = cartesian - 360
    while cartesian <= -180.0:
    	cartesian = cartesian + 360
    rad = math.pi * cartesian / 180.0
    ox = d * math.cos(rad)
    oy = d * math.sin(rad)
    self.canvas.coords(self.line_id, cx, cy, cx + ox, cy - oy)

    #
    # Call callback
    #
    if doCallback:
	    self.command(a)

  setAngle = set_angle

# -----------------------------------------------------------------------------
#
def canvas_coordinates(canvas, event):

  return (canvas.canvasx(event.x), canvas.canvasy(event.y))
