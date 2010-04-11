# -----------------------------------------------------------------------------
#
from __future__ import with_statement
from contextlib import contextmanager
import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
@contextmanager
def benchmarking(viewer):

  # Use glFinish instead of swapping buffers to avoid maxing out
  # at the screen's refresh rate
  viewer.benchmarking = 2		# use glFinish
  yield
  viewer.benchmarking = 0		# reset to swapping 

# -----------------------------------------------------------------------------
#
class Benchmark_Dialog(ModelessDialog):

  title = 'Benchmark'
  name = 'benchmark'
  buttons = ('Run Benchmarks', 'Halt', 'Report Scores', 'Close',)
  help = 'ContributedSoftware/benchmark/benchmark.html'
  
  # ---------------------------------------------------------------------------
  #
  def fillInUI(self, parent):

    self.averaging_interval = 1                 # seconds
    self.target_fps = 10.0                      # frames per second
    self.standard_window_size = (512, 512)
    self.initial_size = 32

    self.frame_rate_timer = Frame_Rate_Timer(self.report_actual_frame_rate,
                                             self.averaging_interval)

    hb = self.buttonWidgets['Halt']
    self.halt_button = hb
    hb['state'] = 'disabled'

    rs = self.buttonWidgets['Report Scores']
    self.report_button = rs
    rs['state'] = 'disabled'

    import Tkinter
    from CGLtk import Hybrid

    row = 0
    parent.columnconfigure(0, weight = 1)

    rt = Hybrid.Scrollable_Text(parent, None, 15, horizontal_scroll = False)
    rt.text['width'] = 50
    rt.text['wrap'] = 'word'
    self.results_box = rt.text
    rt.frame.grid(row = row, column = 0, sticky = 'news')
    parent.rowconfigure(row, weight = 1)
    row = row + 1

    descrip = ('Running benchmarks takes 5-10 minutes to complete.\n\n' +

               'Measure graphics card and CPU performance ' +
               'for volume data rendering.  The scores ' +
               'give the edge size of a cubic volume data ' +
               'array such that rendering or contouring or recoloring ' +
               'can be performed %.0f ' % self.target_fps +
               'times per second.\n\n' +

               'The surface and mesh benchmarks measure the ' +
               'rendering rates for triangles and lines respectively.  ' +
               'The contour benchmark measures ' +
               'CPU and memory performance.  ' +
               'The solid benchmark measures 2 dimensional texture ' +
               'mapping performance.  The recolor benchmark measures ' +
               'bandwidth to the graphics card.\n\n' +

               'The frame rate buttons give the redraw ' +
               'rate for your currently displayed view ' +
               'reported at one second intervals.\n\n' +

               'The molecule benchmark measures and reports frames per '
               'second when displaying different representations of molecules, '
	       'and operations per second for the Ops call.\n\n'

               'For an accurate benchmark, please do not use the CPU for other '
               'tasks while benchmarks are running, and leave the entire Chimera '
               'graphics window visible.\n\n'
	      )
    self.show_result(descrip)
    self.results_box.see('1.0')

    frf = Tkinter.Frame(parent)
    frf.grid(row = row, column = 0, sticky = 'w')
    row = row +1

    mr = Hybrid.Checkbutton(frf, 'Measure frame rate continuously or ', False)
    mr.button.grid(row = 0, column = 0, sticky = 'w')
    self.monitor_frame_rate = mr.variable
    self.monitor_frame_rate.add_callback(self.monitor_cb)
    
    frb = Tkinter.Button(frf, text = 'one time',
                         command = self.actual_frame_rate)
    frb.grid(row = 0, column = 1, sticky = 'w')
    
    it = Hybrid.Checkbutton(parent, 'Show individual test controls', False)
    it.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    itf = Tkinter.Frame(parent)
    itf.grid(row = row, column = 0, sticky = 'w')
    row = row +1
    trow = 0

    it.popup_frame(itf)
    it.popup_frame_cb()         # Hide panel

    bmb = Hybrid.Button_Row(itf, 'Run',
			    (('molecule', self.molSphere_benchmark),
                             ('surface', self.surface_benchmark),
			     ('mesh', self.mesh_benchmark),
			     ('contour', self.contour_benchmark),
			     ('solid', self.solid_benchmark),
			     ('recolor', self.recolor_benchmark)))
    bmb.frame.grid(row = trow, column = 0, sticky = 'w')
    trow += 1
    
    smf = Tkinter.Frame(itf)
    smf.grid(row = trow, column = 0, sticky = 'w')
    trow += 1

    sml = Hybrid.Entry(smf, 'Show standard model, size ', 4,
                       repr(self.initial_size))
    sml.frame.grid(row = 0, column = 0, sticky = 'w')
    self.standard_model_size_var = sml.variable

    smb = Hybrid.Button_Row(smf, ', ',
			    (('surface', self.standard_surface),
			     ('mesh', self.standard_mesh),
			     ('solid', self.standard_solid),
			     ))
    smb.frame.grid(row = 0, column = 1, sticky = 'w')
    
    sv = Hybrid.Button_Row(itf, 'Set standard view',
                           (('camera', self.set_standard_camera_parameters),
                            ('window size', self.set_standard_window_size),
                            ))
    sv.frame.grid(row = trow, column = 0, sticky = 'w')
    trow += 1

    sf = Tkinter.Frame(parent)
    sf.grid(row = row, column = 0, sticky = 'w')
    row += 1
    
    sb = Tkinter.Button(sf, text = 'Show', command = self.show_scores_web_page)
    sb.grid(row = 0, column = 0, sticky = 'w')

    sl = Tkinter.Label(sf, text = ' scores reported by others')
    sl.grid(row = 0, column = 1, sticky = 'w')
    
  # ---------------------------------------------------------------------------
  #
  def RunBenchmarks(self):

    self.run_all_benchmarks()
    
  # ---------------------------------------------------------------------------
  #
  def Halt(self):

    self.halt_benchmark_cb()
    
  # ---------------------------------------------------------------------------
  #
  def ReportScores(self):

    from chimera.version import release
    from chimera import opengl_platform, operating_system
    text = self.results_box.get('0.0', 'end')
    from BugReport import systemInfo
    sinfo = systemInfo()
    for rf,rt in (('<i>',''), ('</i>',''),  ('<br>','\n'), ('\n\n', '\n')):
      sinfo = sinfo.replace(rf, rt)
    descrip = 'Benchmark scores\n\n%s\n%s' % (sinfo, text)

    t = {'description': descrip,
         'platform': '(%s) %s' % (opengl_platform(), operating_system()),
         'version': release,
         'name': '',
         'email': '',
         }

    from BugReport.pyWidgetInterface import hidden_attrs
    attrs = hidden_attrs.copy()
    for hk, hv in attrs.items():
      for k, v in t.items():
        if k.upper() + '_VAL' == hv:
          attrs[hk] = v
    
    from BugReport import post_url
    errcode, errmsg, headers, body = post_url(attrs, file_list = [])
    if errcode == 200:
      self.show_result('\n\nThanks for reporting your benchmark scores!  ' +
                       'It may take a few days before they are listed ' +
                       'on the Chimera web site.', color = 'blue')
    else:
      self.show_result('\n\nWas not able to send results.\n', color = 'red')
      self.show_result(errmsg, color = 'red')
    
  # ---------------------------------------------------------------------------
  #
  def show_scores_web_page(self):

    url = 'http://www.cgl.ucsf.edu/chimera/benchmarks.html'
    from chimera.help import display
    display(url)
    
  # ---------------------------------------------------------------------------
  #
  def show_result(self, text, color = None):

    rb = self.results_box
    if color is None:
      rb.insert('end', text + '\n')
    else:
      tag_name = 't%d' % len(rb.get('0.0','end'))
      rb.tag_configure(tag_name, foreground = color)
      rb.insert('end', text + '\n', tag_name)
    rb.see('end')
    rb.update_idletasks()
    
  # ---------------------------------------------------------------------------
  #
  def monitor_cb(self):

    if self.monitor_frame_rate.get():
      self.frame_rate_timer.report_continuously()
    else:
      self.frame_rate_timer.stop_reporting()

  # ---------------------------------------------------------------------------
  #
  def actual_frame_rate(self, event = None):

    show_main_chimera_window()
    t = Frame_Rate_Timer(self.report_actual_frame_rate,
                         self.averaging_interval)
    t.report_once()

  # ---------------------------------------------------------------------------
  #
  def report_actual_frame_rate(self, r):
    
    self.show_result('Frame rate: %.1f' % r)

  # ---------------------------------------------------------------------------
  #
  def set_window_size(self, width_and_height):

    v = chimera.viewer
    v.windowSize = width_and_height

    #
    # If user resizes by hand the above size will not take effect.
    # Reset top level geometry to get requested size.
    #
    from chimera import tkgui
    app = tkgui.app
    top = app.winfo_toplevel()
    top.wm_geometry('')

  # ---------------------------------------------------------------------------
  #
  def set_standard_window_size(self):

    self.set_window_size(self.standard_window_size)

  # ---------------------------------------------------------------------------
  #
  def set_standard_camera_parameters(self):

    v = chimera.viewer
    v.viewSize = 1
    v.scaleFactor = 1
    v.clipping = True

    c = v.camera
    c.nearFar = (2, -2)
    c.center = (0, 0, 0)
    c.viewDistance = 30

  # ---------------------------------------------------------------------------
  #
  def standard_model_size(self):

    try:
      size = int(self.standard_model_size_var.get())
    except ValueError:
      size = self.initial_size
    if size < 2:
      size = 2

    return size

  # ---------------------------------------------------------------------------
  #
  def standard_surface(self):

    size = self.standard_model_size()
    surf = cube_surface_model(size)
    chimera.openModels.add([surf])

  # ---------------------------------------------------------------------------
  #
  def standard_mesh(self):

    size = self.standard_model_size()
    mesh = cube_surface_model(size, mesh = 1)
    chimera.openModels.add([mesh])

  # ---------------------------------------------------------------------------
  #
  def standard_solid(self):

    size = self.standard_model_size()
    solid = solid_cube_model(size)
    chimera.openModels.add([solid])

  # ---------------------------------------------------------------------------
  #
  def find_size_by_bisection(self, name, f):

    self.allow_halt(True)

    self.show_result('\n' + name)
    self.show_result(' size      rate')

    size_low = None
    size_high = None

    while size_low == None or size_high == None or size_high - size_low > 1:

      if size_low != None and size_high != None:
        size = (size_low + size_high) / 2
      elif size_low != None:
        if size < 128:
          size = size * 2
        else:
          size = int(size * 1.4)
      elif size_high != None:
        size = size / 2
      else:
        size = self.initial_size

      if size <= 1:
        self.allow_halt(False)
        return size

      if self.halt_requested():
        self.show_result('%s benchmark halted' % name)
        self.allow_halt(False)
        return None
      
      fps = f(size)
      self.show_result('%5d %10.1f' % (size, fps))
      
      if fps < self.target_fps:
        if size_high == None or size < size_high:
          size_high = size
      else:
        if size_low == None or size > size_low:
          size_low = size

    self.show_result('%s benchmark: %.0f' % (name, size_low))
    self.allow_halt(False)
    return size_low

  # --- Sam's Molecule Benchmarks --
  # ---------------------------------------------------------------------------
  def set_molecule_style(self, mol, style):

        from chimera import runCommand
	if style == 'wireframe':
          runCommand('show # ; ~ribbon # ; repr wire #')
	elif style == 'stick':
          runCommand('show # ; ~ribbon # ; repr stick #')
	elif style == 'ball-stick':
          runCommand('show # ; ~ribbon # ; repr bs #')
	elif style == 'ribbon':
          runCommand('~show # ; ribbon # ; ribrepr flat #')
	elif style == 'sphere':
          runCommand('show # ; ~ribbon # ; repr sphere #')
	elif style == 'null':
          runCommand('~show # ; ~ribbon #')

  def do_molBenchmark(self, style):

	self.set_standard_window_size()

	import Midas
	Midas.window('#')
	show_main_chimera_window()
	draw_scene()

	# Use glFinish instead of swapping buffers to avoid maxing out
	# at the screen's refresh rate
	times = []
	for i in range(5):
		with benchmarking(chimera.viewer):
			t = calls_per_second(draw_scene, self.averaging_interval)
		times.append(t)
		if self.halt_requested():
			raise HaltRequest(style)
	mean = sum(times) / 5.0

	return mean

  def do_opFlip(self, mol):
	for at in mol.atoms:
		at.display = not at.display

  def do_opsBenchmark(self, mol):
        self.set_molecule_style(mol, 'wireframe')
	do_opFlip_mol = lambda : self.do_opFlip(mol)

	times = []
	for i in range(5):
		t = calls_per_second(do_opFlip_mol, self.averaging_interval)
		times.append(t)
		if self.halt_requested():
			raise HaltRequest('ops')
	mean = sum(times) / 5.0

	return mean

  def molSphere_benchmark(self):

        self.warn_if_models_open()
        self.show_result('\nRunning molecule benchmark using PDB 1f4h\n')
        
	self.allow_halt(True)
	i = 0
	styles = ('null', 'wireframe', 'stick', 'ball-stick',
		  'ribbon', 'sphere')
	from os.path import join, dirname
	for molName in ['1f4h']:
		try:
			molFile = join(dirname(__file__), molName + '.pdb')
			mlist = chimera.openModels.open(molFile, noprefs=True)
			m = mlist[0]
			scores = []
			for style in styles:
				self.set_molecule_style(m, style)
				score = self.do_molBenchmark(style)
				scores.append(score)
				self.show_result('%s %.1f' % (style, score))
				if self.halt_requested():
					raise HaltRequest(molName)
			score = self.do_opsBenchmark(m)
			scores.append(score)
			self.show_result('%s %.1f\n' % ('ops', score))
			s = '\t'.join(['%.1f' % s for s in scores])
		except MemoryError:
			# Note that catching this exception only helps
			# if we run out of memory during a Python procedure
			# call.  Frequently, the error occurs during Tcl/Tk
			# processing, and then Chimera just dies, and there's
			# not a whole lot we can do about that.
			self.show_result('Not enough memory to test %s' % molName)
		except HaltRequest:
			self.show_result('molecule benchmark halted')
			break
		else:
                  self.show_result('\nMolecule %s (%d atoms):'
                                   % (molName, len(m.atoms)))
                  self.show_result('Null\tWire\tStick\tBStick\tRibbon\tSphere\tOps')
                  self.show_result(s)
		chimera.openModels.close(mlist)

	self.allow_halt(False)
	return 1

  # --- End Sam's Code ---
  # ---------------------------------------------------------------------------
  #
  def solid_benchmark(self):

    self.warn_if_models_open()
    self.set_standard_window_size()
    return self.find_size_by_bisection('Solid rendering', self.solid_rate)

  # ---------------------------------------------------------------------------
  #
  def solid_rate(self, size):

    try:
      vol = solid_cube_model(size)
    except MemoryError:
      self.show_result('Not enough memory to test solid of size %d' % size)
      return 0
    
    chimera.openModels.add([vol])
    self.set_standard_camera_parameters()
    show_main_chimera_window()
    draw_scene()                # first draw may take longer
    gr = calls_per_second(draw_scene, self.averaging_interval)
    chimera.openModels.close([vol])

    return gr

  # ---------------------------------------------------------------------------
  #
  def recolor_benchmark(self):

    self.warn_if_models_open()
    self.set_standard_window_size()
    return self.find_size_by_bisection('Recoloring', self.recolor_rate)
  
  # ---------------------------------------------------------------------------
  #
  def recolor_rate(self, size):

    try:
      vol = solid_cube_model(size)
    except MemoryError:
      self.show_result('Not enough memory to test recoloring solid of size %d' % size)
      return 0

    chimera.openModels.add([vol])
    
    from numpy import empty, uint8
    p = empty((size, size, 2), uint8)
    p.fill(128)
    def get_color_plane(axis, plane, p=p):
      return p

    def recolor(vol = vol, size = size, gcp = get_color_plane):
      vol.set_color_plane_callback((size,size,size), gcp)
      draw_scene()

    show_main_chimera_window()
    draw_scene()                # first draw may take longer
    cr = calls_per_second(recolor, self.averaging_interval)

    chimera.openModels.close([vol])

    return cr

  # ---------------------------------------------------------------------------
  #
  def mesh_benchmark(self):

    self.warn_if_models_open()
    return self.surface_benchmark(mesh = 1)

  # ---------------------------------------------------------------------------
  #
  def surface_benchmark(self, mesh = 0):

    self.warn_if_models_open()
    self.set_standard_window_size()

    if mesh:
      name = 'Mesh rendering'
    else:
      name = 'Surface rendering'
    rate_func = lambda size, s=self, m=mesh: s.surface_rate(size, mesh=m)
    return self.find_size_by_bisection(name, rate_func)

  # ---------------------------------------------------------------------------
  #
  def surface_rate(self, size, mesh):

    try:
      surf = cube_surface_model(size, mesh)
    except MemoryError:
      self.show_result('Not enough memory to test surface of size %d' % size)
      return 0

    chimera.openModels.add([surf])
    self.set_standard_camera_parameters()
    v = chimera.viewer
    show_main_chimera_window()
    draw_scene()   # first drawing is direct rendered
    draw_scene()   # second draw takes longer - builds display list
    draw_scene()   # speed improves after third drawing.
    gr = calls_per_second(draw_scene, self.averaging_interval)
    chimera.openModels.close([surf])

    return gr

  # ---------------------------------------------------------------------------
  #
  def contour_benchmark(self):

    return self.find_size_by_bisection('Contouring', self.contour_rate)

  # ---------------------------------------------------------------------------
  #
  def contour_rate(self, size):

    data = gaussian_volume_data(size)
    threshold = .4
    def contour(data = data, threshold = threshold):
      from _contour import surface
      vertices, vertex_indices = surface(data, threshold)

    cr = calls_per_second(contour, self.averaging_interval)

    return cr
  
  # ---------------------------------------------------------------------------
  #
  def run_all_benchmarks(self):
    
    benchmarks = (('surface', self.surface_benchmark),
                  ('mesh', self.mesh_benchmark),
                  ('contour', self.contour_benchmark),
                  ('solid', self.solid_benchmark),
                  ('recolor', self.recolor_benchmark),
                  )

    scores = []
    for name, function in benchmarks:
      score = function()
      if score is None:
        break                   # halt requested
      scores.append(score)

    if scores:
      result_text = ''.join(['%8.0f' % score for score in scores])
      self.show_result('\nVolume benchmark scores')
      self.show_result(' surface    mesh  contour  solid  recolor')
      self.show_result(result_text)

    if not self.halt_requested():
      self.molSphere_benchmark()

    if not self.halt_requested():
      self.report_button['state'] = 'normal'
      self.show_result('\nTo report your scores for inclusion on the ' +
                       'Chimera web page press the Report Scores button.  ' +
                       'Only scores and machine specs will be sent using ' +
                       'an http post (not email).\n')
      
  # ---------------------------------------------------------------------------
  #
  def allow_halt(self, allow):

    if allow:
      self.request_halt = False
      self.halt_button['state'] = 'normal'
    else:
      self.halt_button['state'] = 'disabled'
      
  # ---------------------------------------------------------------------------
  #
  def halt_benchmark_cb(self):

    self.request_halt = True

  # ---------------------------------------------------------------------------
  #
  def halt_requested(self):

    from chimera import update
    update.processWidgetEvents(self.halt_button)
    return self.request_halt

  # ---------------------------------------------------------------------------
  #
  def warn_if_models_open(self):

    n = len(chimera.openModels.list())
    if n > 0:
      msg = '%d models are open. Running benchmarks with models opened will produce inaccurate lower scores.' % n
      from chimera.replyobj import warning
      warning(msg)
      self.show_result('\n\n' + msg + '\n\n', color = 'red')

# -----------------------------------------------------------------------------
# Monitor the Chimera frame rate using the "check for changes" trigger.
#
class Frame_Rate_Timer:

  def __init__(self, report_frame_rate_cb, averaging_interval):
    
    self.report_frame_rate_cb = report_frame_rate_cb
    self.averaging_interval = averaging_interval

    self.continue_reporting = 0
    self.start_time = None
    self.cfc_count = 0
    self.cfc_handler = None

  # ---------------------------------------------------------------------------
  #
  def report_once(self):

    self.add_handler()
    self.continue_reporting = 0

  # ---------------------------------------------------------------------------
  #
  def report_continuously(self):

    self.add_handler()
    self.continue_reporting = 1

  # ---------------------------------------------------------------------------
  #
  def stop_reporting(self):

    self.remove_handler()

  # ---------------------------------------------------------------------------
  #
  def add_handler(self):

    if self.cfc_handler == None:
      self.start_time = None
      h = chimera.triggers.addHandler('check for changes',
                                      self.check_for_changes_cb, None)
      self.cfc_handler = h

  # ---------------------------------------------------------------------------
  #
  def remove_handler(self):

    if self.cfc_handler:
      chimera.triggers.deleteHandler('check for changes', self.cfc_handler)
      self.cfc_handler = None

  # ---------------------------------------------------------------------------
  #
  def check_for_changes_cb(self, trigger, callData, triggerData):

    self.force_redisplay()

    import time
    t = time.time()		# use wall clock time
    if self.start_time == None:
      self.start_time = t
      self.cfc_count = 0
      return

    self.cfc_count = self.cfc_count + 1
    elapsed_time = float(t - self.start_time)
    if elapsed_time >= self.averaging_interval:
      r = self.cfc_count / elapsed_time
      self.report_rate(r)
      self.start_time = t
      self.cfc_count = 0

  # ---------------------------------------------------------------------------
  #
  def force_redisplay(self):

    v = chimera.viewer
    v.touch()

  # ---------------------------------------------------------------------------
  #
  def report_rate(self, rate):

    try:
      self.report_frame_rate_cb(rate)
    except:
      self.remove_handler()
      
    if not self.continue_reporting:
      self.remove_handler()

# ---------------------------------------------------------------------------
#
class HaltRequest(RuntimeError):
	pass

# ---------------------------------------------------------------------------
#
def cube_surface_model(size, mesh = 0):

  import _surface
  s = _surface.SurfaceModel()

  (vertices, vertex_indices) = cube_triangles(size)
  rgba = (.5,.5,.5,1)
  p = s.addPiece(vertices, vertex_indices, rgba)
  if mesh:
    style = p.Mesh
  else:
    style = p.Solid
  p.displayStyle = style
  p.useLighting = True
  p.twoSidedLighting = True
  p.smoothLines = False

  return s
    
# -----------------------------------------------------------------------------
#
def cube_triangles(size):

  from numpy import zeros, single as floatc, intc, array, multiply, add
  vertices = zeros((6*size*size, 3), floatc)
  vertex_indices = zeros((12*(size-1)*(size-1), 3), intc)

  faces = ((1, 0, 2, 0), (0, 1, 2, size-1),
	   (0, 2, 1, 0), (2, 0, 1, size-1),
	   (2, 1, 0, 0), (1, 2, 0, size-1))
  for k in range(6):
    a0, a1, a2, d = faces[k]
    cube_face(size, vertices[k*size*size:,:], k*size*size,
	      vertex_indices[k*2*(size-1)*(size-1):,:],
	      a0, a1, a2, d)

  multiply(vertices.flat, 2.0/(size-1), vertices.flat)
  add(vertices.flat, -1.0, vertices.flat)

  return vertices, vertex_indices
    
# -----------------------------------------------------------------------------
#
def cube_face(size, vertices, ioffset, vertex_indices, axis0, axis1, axis2, d):

  vertices[:,axis2] = d
  s2 = size * size
  from numpy import indices, ravel, array, arange, resize, add
  i = indices((size,size), vertices.dtype)
  vertices[:s2,axis0] = ravel(i[1,:,:])
  vertices[:s2,axis1] = ravel(i[0,:,:])

  vitype = vertex_indices.dtype
  sm2 = 2 * (size-1) * (size-1)
  j = resize(arange(s2, dtype=vitype), (size,size))
  j = ravel(j[:size-1,:size-1])

  one = array(1, vitype)
  s = array(size, vitype)
  sp1 = array(size+1, vitype)
  ioff = array(ioffset, vitype)

  vertex_indices[0:sm2:2,0] = j
  vertex_indices[0:sm2:2,1] = j
  add(vertex_indices[0:sm2:2,1], one, vertex_indices[0:sm2:2,1])
  vertex_indices[0:sm2:2,2] = j
  add(vertex_indices[0:sm2:2,2], s, vertex_indices[0:sm2:2,2])

  vertex_indices[1:sm2:2,0] = j
  add(vertex_indices[1:sm2:2,0], one, vertex_indices[1:sm2:2,0])
  vertex_indices[1:sm2:2,1] = j
  add(vertex_indices[1:sm2:2,1], sp1, vertex_indices[1:sm2:2,1])
  vertex_indices[1:sm2:2,2] = j
  add(vertex_indices[1:sm2:2,2], s, vertex_indices[1:sm2:2,2])

  add(vertex_indices[0:sm2,:], ioff, vertex_indices[0:sm2,:])

# -----------------------------------------------------------------------------
#
def solid_cube_model(size):

  import _volume
  v = _volume.Volume_Model()
  from numpy import empty, uint8
  p = empty((size,size,2), uint8)
  p.fill(128)
  def get_color_plane(axis, plane, p=p):
    return p
  v.set_color_plane_callback((size,size,size), get_color_plane)
  step = 2.0/size
  origin = -1.0 + 1.0/size
  tf = ((step, 0, 0, origin),
        (0, step, 0, origin),
        (0, 0, step, origin))
  v.set_array_coordinates(tf)
  v.projection_mode = '2d-xyz'
  v.color_mode = 'la8'
  v.maximum_intensity_projection = False
  v.linear_interpolation = True
  v.brightness_and_transparency_correction = False
  v.minimal_texture_memory = False
  v.show_outline_box = True

  return v

# -----------------------------------------------------------------------------
#
def gaussian_volume_data(size):

  from numpy import arange, add, multiply, exp, outer, resize, single as floatc
  i = arange(size)
  x = add(i, -.5 * size)
  x2 = multiply(x, x)
  mx2 = multiply(x2, -4.0/(size * size))
  h = exp(mx2)
  h2 = outer(h, h)
  h3 = outer(h2, h)
  d3 = resize(h3, (size, size, size))
  data = d3.astype(floatc)
  return data

# -----------------------------------------------------------------------------
# The Chimera frameUpdate() loop is bypassed.  The Chimera frameUpdate()
# loop introduces a delay of chimera.update.UPDATE_INTERVAL msec.
#
def draw_scene():

  from chimera import tkgui, viewer
  viewer.displayCB(tkgui.app.graphics)	# Redisplay graphics window

# -----------------------------------------------------------------------------
#
def show_main_chimera_window():

  chimera.tkgui.app.bringToFront()

# -----------------------------------------------------------------------------
# Uses wall clock time time.time() instead of CPU time time.clock() since
# the latter does not catch time spent waiting for graphics card.
#
def calls_per_second(function, averaging_interval):

  import time
  t = time.time()		# use wall clock time
  count = 0
  start_time = t
  elapsed_time = 0

  while elapsed_time < averaging_interval:
    function()
    count = count + 1
    t = time.time()		# use wall clock time
    elapsed_time = t - start_time

  if elapsed_time == 0:
    rate = 0
  else:
    rate = count / float(elapsed_time)

  return rate

# -----------------------------------------------------------------------------
#
def show_benchmark_dialog():

  from chimera import dialogs
  return dialogs.display(Benchmark_Dialog.name)
    
# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Benchmark_Dialog.name, Benchmark_Dialog, replace = 1)
#dialogs.register(Benchmark_Dialog.name, Benchmark_Dialog)
