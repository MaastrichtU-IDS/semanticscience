# -----------------------------------------------------------------------------
#
def show_saxs_profile(molecules, selected_only, epath, expath, dialog = None):

  if len(molecules) <= 2:
    name = ', '.join([m.name for m in molecules])
  else:
    name = '%d models' % len(molecules)

  import tempfile, os
  fd, pdbpath = tempfile.mkstemp(suffix = '.pdb')
  os.close(fd)
  import Midas
  Midas.write(molecules, molecules[0], pdbpath, selOnly = selected_only)

  if not epath:
    # Use web services if no executable is given
    if dialog is None:
      dialog = PlotDialog()
    ProfileOpalService(pdbpath, expath, name, dialog.figure) 
  else:
    cmd = '%s %s %s' % (epath, pdbpath, expath)
    from chimera.replyobj import info, warning
    info('Executing command: %s\n' % cmd)
    status = os.system(cmd)
    if status != 0:
      warning('Error %d executing command "%s"' % (status, cmd))
      return dialog
    if expath:
      from os.path import basename
      ppath = pdbpath[:-4] + '_' + basename(expath)
      p = read_profile(ppath, 3)
    else:
      ppath = pdbpath + '.dat'
      p = read_profile(ppath, 2)
    plot_profile(p, name, dialog.figure)
  return dialog

# -----------------------------------------------------------------------------
#
class ProfileOpalService:

  def __init__(self, pdbpath, expath, name, fig):
    from WebServices.AppService_types import ns0
    from WebServices.opal_client import OpalService
    self.pdbpath = pdbpath
    self.expath = expath
    self.name = name
    self.figure = fig

    pdbFile = ns0.InputFileType_Def("inputFile")
    pdbFile._name = "pdbfile"
    f = open(pdbpath)
    pdbFile._contents = f.read()
    f.close()
    files = [ pdbFile ]
    argList = "pdbfile"
    if expath:
      exFile = ns0.InputFileType_Def("inputFile")
      exFile._name = "exfile"
      f = open(expath)
      exFile._contents = f.read()
      f.close()
      files.append(exFile)
      argList += " exfile"
    
    try:
      self.opal = OpalService("SAXSService")
    except:
      import traceback, sys
      print "Traceback from SAXS request:"
      traceback.print_exc(file=sys.stdout)
      print """
Typically, if you get a TypeError, it's a problem on the remote server
and it should be fixed shortly.  If you get a different error or
get TypeError consistently for more than a day, please report the
problem using the Report a Bug... entry in the Help menu.  Please
include the traceback printed above as part of the problem description."""
      from chimera import NonChimeraError
      raise NonChimeraError("SAXS web service appears "
            "to be down.  See Reply Log "
            "for more details.")

    self.opal.launchJob(argList, _inputFile=files)
    from chimera.tasks import Task
    self.task = Task("SAXS " + self.name, self.cancelCB, self.statusCB)
    
  def cancelCB(self):
    self.task = None

  def statusCB(self):
    self.task.updateStatus(self.opal.currentStatus())
    if not self.opal.isFinished():
      self.opal.queryStatus()
      return
    self.task = None
    self.filemap = self.opal.getOutputs()
    if self.opal.isFinished() > 0:
      # Successful completion
      self.finished()
    else:
      # Failed
      from chimera import replyobj
      replyobj.error("SAXS %s failed; see Reply Log for more information"
		      % self.name)
      self.showFileContent("stdout.txt")
      self.showFileContent("stderr.txt")

  def finished(self):
    if self.expath:
      data = self.getFileContent("pdbfile_exfile.dat")
      p = read_profile_data(data, 3)
    else:
      data = self.getFileContent("pdbfile.dat")
      p = read_profile_data(data, 2)
    self.figure = plot_profile(p, self.name, self.figure)

  def getURLContent(self, url):
    import urllib2
    f = urllib2.urlopen(url)
    data = f.read()
    f.close()
    return data

  def getFileContent(self, filename):
    return self.getURLContent(self.filemap[filename])

  def showURLContent(self, title, url):
    from chimera import replyobj
    data = self.getURLContent(url)
    replyobj.message("%s\n-----\n%s-----\n" % (title, data))

  def showFileContent(self, filename):
    try:
      url = self.filemap[filename]
    except KeyError:
      from chimera import replyobj
      replyobj.message("SAXS profile: there is no file named \"%s\"" % filename)
    else:
      self.showURLContent("SAXS profile %s" % filename, url)


# -----------------------------------------------------------------------------
#
def read_profile(path, columns):

  p = open(path, 'r')
  data = p.read()
  p.close()
  return read_profile_data(data, columns)

# -----------------------------------------------------------------------------
#
def read_profile_data(data, columns):

  lines = data.splitlines()
  values = [tuple([float(x) for x in line.split()[:columns]])
      for line in lines if line and line[0] != '#']
  return values

# -----------------------------------------------------------------------------
#
def plot_profile(p, name, fig = None):

  if fig is None:
    d = PlotDialog()
    fig = d.figure
  ax = fig.add_subplot(1,1,1)
  
  q = [qi[0] for qi in p]
  i = [qi[1] for qi in p]
  if len(p[0]) == 3:
    e = i
    i = [qi[2] for qi in p]
    ax.semilogy(q, e, '+')
  ax.semilogy(q, i, linewidth=1.0)
  ax.set_xlim(xmin = 0.0)
  ax.set_xlabel('q')
  ax.set_ylabel('log(intensity)')
  ax.set_title('Small-angle x-ray scattering profile %s' % name)
  ax.grid(True)
  fig.canvas.draw()
  return fig

# -----------------------------------------------------------------------------
#
from chimera.baseDialog import ModelessDialog
class PlotDialog(ModelessDialog):

  title = "SAXS Profile"

  def fillInUI(self, parent):
    from matplotlib.figure import Figure
    self.figure = Figure()
    from matplotlib.backends.backend_tkagg \
      import FigureCanvasTkAgg, NavigationToolbar2TkAgg
    fc = FigureCanvasTkAgg(self.figure, master=parent)
    fc.get_tk_widget().pack(side="top", fill="both", expand=True)
    nt = NavigationToolbar2TkAgg(fc, parent)
    nt.update()

# -----------------------------------------------------------------------------

