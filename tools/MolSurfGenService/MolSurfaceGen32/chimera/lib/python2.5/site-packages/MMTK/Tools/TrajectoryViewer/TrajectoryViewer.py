# Trajectory viewer for MMTK trajectory files
#
# Written by Konrad Hinsen
# last revision: 2007-7-3
#

from Tkinter import *
from Tkwindow import Tkwindow
from Scientific.TkWidgets import FloatEntry, IntEntry, StatusBar, ModalDialog
from Scientific.TkWidgets.TkPlotCanvas import PlotCanvas,PolyLine,PlotGraphics
from Scientific.TkWidgets.TkVisualizationCanvas import VisualizationCanvas, \
     VisualizationGraphics, PolyLine3D
from MMTK.Tk.ProteinVisualization import ProteinBackboneGraphics
import Dialog, FileDialog
from Scientific.DictWithDefault import DictWithDefault
from Scientific.IO import ArrayIO
from Scientific import N as Numeric
import os, string, tempfile, time
import MMTK, MMTK.Trajectory
from TrajectoryInspector import TrajectoryInspector


try:
    import Pyro.core, Pyro.naming, Pyro.errors
    use_pyro = 1
except ImportError:
    use_pyro = 0
if use_pyro:
    from TrajectoryManager import TrajectoryManager
    try:
        tmanager = TrajectoryManager()
    except Pyro.errors.PyroError:
        tmanager = None
else:
    tmanager = None

#
# Utility functions
#

#
# Plotting via external program
#
plot_program = None
try:
    plot_program = os.environ['PLOTPROGRAM']
except KeyError: pass

def externalPlot(data):
    if plot_program is not None:
        filename = tempfile.mktemp()
        ArrayIO.writeArray(data, filename)
        if os.fork() == 0:
            pipe = os.popen(plot_program + ' ' + filename + \
                            ' 1> /dev/null 2>&1', 'w')
            pipe.close()
            os.unlink(filename)
            os._exit(0)

#
# Sort variables into categories for display
#
_category = {
    'energy': 'energy',
    'temperature': 'thermodynamic',
    'pressure': 'thermodynamic',
    'volume': 'thermodynamic',
    'configuration': 'configuration',
    'coordinate': 'auxiliary',
    'masses': 'masses',
    'time': 'time',
    }

def categorizeVariables(variable_names):
    categories = DictWithDefault([])
    for name in variable_names:
        words = string.split(name, '_')
        try:
            c = _category[words[-1]]
        except KeyError:
            c = ''
        if c:
            categories[c].append(name)
    for list in categories.values():
        list.sort()
    if categories.has_key('energy'):
        list = categories['energy']
        for variable in ['kinetic_energy', 'potential_energy']:
            if variable in list:
                list.remove(variable)
                list = [variable] + list
        categories['energy'] = list
    return categories

#
# Determine 'nice' plot range for a given value interval
#
def plotRange(lower, upper):
    range = upper-lower
    if range == 0.:
        return lower-0.5, upper+0.5
    log = Numeric.log10(range)
    power = Numeric.floor(log)
    fraction = log-power
    if fraction <= 0.05:
        power = power-1
    grid = 10.**power
    lower = lower - lower % grid
    mod = upper % grid
    if mod != 0:
        upper = upper - mod + grid
    return lower, upper

#
# Simple text display window
#
class TextViewer(Toplevel):

    def __init__(self, master, text, title=''):
        Toplevel.__init__(self, master)
        self.title(title)
        Label(self, text=text,
                      justify=LEFT).pack(side=TOP)
        button_bar = Frame(self)
        button_bar.pack(side=BOTTOM)
        Button(button_bar, text='Close',
               command=self.destroy).pack(side=RIGHT)

#
# Multiple plot window
#
class PlotWindow(Toplevel):

    def __init__(self, master, title):
        Toplevel.__init__(self, master)
        self.title(title)
        self.plotlist = []
        self.protocol("WM_DELETE_WINDOW", self.close)

    def close(self):
        for plot in self.plotlist:
            self.master._unregisterPlot(plot)
        self.destroy()

    def registerPlot(self, plot):
        self.plotlist.append(plot)
        self.master._registerPlot(plot)
    
    def setSelection(self, plot):
        if self.master.selection is not None:
            i1, i2 = self.master.selection
            plot.select((self.master.time[i1], self.master.time[i2]))

#
# Standard plot window for independent quantities
#
class PlotViewer(PlotWindow):

    def __init__(self, master, title, time, inspector, names):
        PlotWindow.__init__(self, master, title)
        self.time = time
        self.step = max(1, len(time)/300)
        self.setup(time, inspector, names)

    def setup(self, time, inspector, names):
        time = time[::self.step]
        for n in names:
            data = Numeric.zeros((len(time), 2), Numeric.Float)
            data[:, 0] = time
            data[:, 1] = Numeric.array(inspector.readScalarVariable(n, 0, None,
                                                                    self.step))
            self.plotBox(n, data)

    def plotBox(self, name, data, data_range=None):
        box = Frame(self, border=2, relief=SUNKEN)
        box.pack(side=TOP, fill=BOTH, expand=YES)
        frame = Frame(box, background='grey')
        frame.pack(side=TOP, fill=X, expand=NO)
        Label(frame, text=string.capitalize(string.join(
                          string.split(name , '_'), ' ')),
              background='grey').pack(side=LEFT)
        if data_range is None:
            min = Numeric.minimum.reduce(data[:,1])
            max = Numeric.maximum.reduce(data[:,1])
            min, max = plotRange(min, max)
        else:
            min, max = data_range
        plot_objects = []
        plot_data = data
        time = plot_data[:,0]
        jumps = Numeric.repeat(Numeric.arange(len(time)-1),
                               Numeric.less(time[1:], time[:-1]))+1
        for i in self.master.restarts:
            plot_objects.append(PolyLine([(self.time[i], min),
                                          (self.time[i], max)],
                                         color='black',
                                         stipple='gray25'))
        plot_objects.insert(0, PolyLine(plot_data, color = 'red'))
        plot = PlotCanvas(box, 400, 100, zoom=1,
                          select=self.master._selectRange)
        plot.pack(side=LEFT, fill=BOTH, expand=YES)
        plot.draw(PlotGraphics(plot_objects),
                  'automatic', (min, max))
        plot.bind('<Double-Button-1>', lambda event, d=plot_data:
                                       externalPlot(d))
        self.registerPlot(plot)
        self.setSelection(plot)

#
# Special plot window for energy terms: uniform scale and
# display of sum.
#
class EnergyViewer(PlotViewer):

    def setup(self, time, inspector, names):
        time = time[::self.step]
        sum = 0.
        range = 0.
        for n in names:
            data = Numeric.array(inspector.readScalarVariable(n, 0, None,
                                                              self.step))
            sum = sum + data
            upper = Numeric.maximum.reduce(data)
            lower = Numeric.minimum.reduce(data)
            lower, upper = plotRange(lower, upper)
            range = max(range, upper-lower)
        upper = Numeric.maximum.reduce(sum)
        lower = Numeric.minimum.reduce(sum)
        lower, upper = plotRange(lower, upper)
        range = 0.5*max(range, upper-lower)
        for n in names:
            data = Numeric.array(inspector.readScalarVariable(n, 0, None,
                                                              self.step))
            data = Numeric.transpose(Numeric.array([time, data]))
            mean = Numeric.add.reduce(data[:, 1])/len(data)
            self.plotBox(n, data, (mean-range, mean+range))
        if len(names) > 1:
            data = Numeric.transpose(Numeric.array([time, sum]))
            mean = Numeric.add.reduce(data[:, 1])/len(data)
            self.plotBox('Sum', data, (mean-range, mean+range))

#
# Plot window for mode projections
#
class ModeProjectionViewer(PlotWindow):

    def __init__(self, master, mode_projector, indices):
        from Scientific.Statistics import mean, standardDeviation
        title = "Normal mode projections (Temperature: %5.1f K)" \
                % mode_projector.temperature
        PlotWindow.__init__(self, master, title)
        self.mode_projector = mode_projector

        plot_range = 0.
        for i in indices:
            series = mode_projector[i][:, 1]
            average = mean(series)
            deviation = standardDeviation(series)
            lower = Numeric.minimum.reduce(series)
            lower = min(lower, average-deviation)
            upper = Numeric.maximum.reduce(series)
            upper = max(upper, average+deviation)
            lower, upper = plotRange(lower, upper)
            plot_range = max(plot_range, upper-lower)

        nmodes = mode_projector.numberOfModes()
        for i in range(len(indices)):
            if indices[i] < 0:
                indices[i] = nmodes+indices[i]
        next_indices = []
        step = indices[1] - indices[0]
        i = indices[-1]
        while len(next_indices) < 4:
            i = i + step
            if i >= nmodes:
                break
            next_indices.append(i)
        previous_indices = []
        i = indices[0]
        while len(previous_indices) < 4:
            i = i - step
            if i < 6:
                break
            previous_indices.insert(0, i)
        if next_indices or previous_indices:
            frame = Frame(self)
            frame.pack(side=BOTTOM, fill=X, expand=YES)
            if previous_indices:
                Button(frame, text="Previous",
                       command=lambda s=self, pi=previous_indices:
                               s.modeProjection(pi)).pack(side=LEFT)
            if next_indices:
                Button(frame, text="Next",
                       command=lambda s=self, ni=next_indices:
                               s.modeProjection(ni)).pack(side=RIGHT)

        for i in range(len(indices)):
            number = indices[i]
            data = mode_projector[number]
            fluctuation = self.mode_projector.amplitude(number)
            average = mean(data[:, 1])
            deviation = standardDeviation(data[:, 1])
            box = Frame(self, border=2, relief=SUNKEN)
            box.pack(side=TOP, fill=BOTH, expand=YES)
            frame = Frame(box, background='grey')
            frame.pack(side=TOP, fill=X, expand=NO)
            Label(frame, text="Mode %d" % number,
                  background='grey').pack(side=LEFT)
            Button(frame, text="Animation", background='grey',
                   command=lambda s=self, n=number:
                                  s.animateMode(n, 1.)).pack(side=RIGHT)
            Button(frame, text="View", background='grey',
                   command=lambda s=self, n=number:
                                  s.viewMode(n)).pack(side=RIGHT)
            minv = Numeric.minimum.reduce(data[:,1])
            maxv = Numeric.maximum.reduce(data[:,1])
            minv, maxv = plotRange(minv, maxv)
            middle = 0.5*(maxv+minv)
            if maxv-minv < plot_range:
                minv = middle-0.5*plot_range
                maxv = middle+0.5*plot_range
            plot_objects = [PolyLine([(data[1, 0], average-fluctuation),
                                      (data[1, 0], average+fluctuation)],
                                     color='blue', width=3),
                            PolyLine([(data[-1, 0], average-deviation),
                                      (data[-1, 0], average+deviation)],
                                     color='green', width=3)]
            plot_objects.insert(0, PolyLine(data, color = 'red'))
            plot = PlotCanvas(box, 400, 100, zoom=1,
                              select=self.master._selectRange)
            plot.pack(side=LEFT, fill=BOTH, expand=YES)
            plot.draw(PlotGraphics(plot_objects), 'automatic', (minv, maxv))
            plot.bind('<Double-Button-1>', lambda event, d=data:
                                           externalPlot(d))
            self.registerPlot(plot)
            self.setSelection(plot)

    def viewMode(self, number):
        amplitude = self.mode_projector.amplitude(number)
        ModeViewer(self, amplitude*self.mode_projector.modes[number], number)

    def animateMode(self, number, scale):
        mode = self.mode_projector.modes[number]
        amplitude = self.mode_projector.amplitude(number)
        mode.view(scale*amplitude)

    def modeProjection(self, indices):
        self.master.modeProjection(indices)


class RBProjectionViewer(PlotWindow):

    def __init__(self, master, rb_projector):
        PlotWindow.__init__(self, master, "Rigid-body motion projections")
        plot_range = 0.
        for i in range(6):
            series = rb_projector[i][:, 1]
            lower = Numeric.minimum.reduce(series)
            upper = Numeric.maximum.reduce(series)
            lower, upper = plotRange(lower, upper)
            plot_range = max(plot_range, upper-lower)

        for column, offset, type in [(0, 0, "Translation "),
                                     (1, 3, "Rotation ")]:
            for i in range(3):
                data = rb_projector[i+offset]
                box = Frame(self, border=2, relief=SUNKEN)
                box.grid(row=i, column=column, sticky=N+W+E+S)
                frame = Frame(box, background='grey')
                frame.pack(side=TOP, fill=X, expand=NO)
                Label(frame, text=type + ["X", "Y", "Z"][i],
                      background='grey').pack(side=LEFT)
                minv = Numeric.minimum.reduce(data[:,1])
                maxv = Numeric.maximum.reduce(data[:,1])
                minv, maxv = plotRange(minv, maxv)
                middle = 0.5*(maxv+minv)
                if maxv-minv < plot_range:
                    minv = middle-0.5*plot_range
                    maxv = middle+0.5*plot_range
                plot_objects = [PolyLine(data, color = 'red')]
                plot = PlotCanvas(box, 400, 100, zoom=1,
                                  select=self.master._selectRange)
                plot.pack(side=LEFT, fill=BOTH, expand=YES)
                plot.draw(PlotGraphics(plot_objects), 'automatic',
                          (minv, maxv))
                plot.bind('<Double-Button-1>', lambda event, d=data:
                                                      externalPlot(d))
                self.registerPlot(plot)
                self.setSelection(plot)

#
# Entry dialog for temperature
#
class TemperatureDialog(ModalDialog):

    def body(self, master):
        self.entry = FloatEntry(master, "Enter temperature: ", 300., 0., None)
        self.entry.pack()
        return self.entry

    def apply(self):
        self.result = self.entry.get()

#
# Normal mode displacement viewer window
#
class ModeViewer(Toplevel):

    def __init__(self, master, mode, number):
        Toplevel.__init__(self, master)
        self.title("Mode %d" % number)
        self.mode = mode
        self.scale = 10.

        frame = Frame(self)
        frame.pack(side=TOP, fill=X, expand=YES)
        self.scale_entry = FloatEntry(frame, "Enhancement factor: ",
                                      10., 0., None)
        self.scale_entry.pack(side=LEFT)
        self.scale_entry.bind('<Return>', self.draw)
        Button(frame, text="Animation",
               command=self.animation).pack(side=RIGHT)
        self.canvas = VisualizationCanvas(self, width=400, height=400,
                                          background='#BBB', relief=SUNKEN,
                                          border=2)
        self.canvas.pack(side=BOTTOM, fill=BOTH, expand=Y)
        self.draw()

    def draw(self, event=None):
        self.canvas.clear()
        graphics = []
        conf = self.mode.universe.configuration()
        offset = self.scale_entry.get()*self.mode
        conf_plus = conf+offset
        conf_minus = conf-offset
        for protein in self.mode.universe:
            graphics.append(ProteinBackboneGraphics(protein, conf_plus,
                                                    color='green'))
            graphics.append(ProteinBackboneGraphics(protein, conf_minus,
                                                    color='red'))
            for a in protein.atomList():
                p1 = conf_plus[a]
                p2 = conf_minus[a]
                graphics.append(PolyLine3D([p1.array, p2.array],
                                           color = 'blue'))
        self.canvas.draw(VisualizationGraphics(graphics))

    def animation(self):
        from MMTK.Visualization import viewSequence
        scale = self.scale_entry.get()
        conf = self.mode.universe.configuration()
        offset = scale*self.mode
        viewSequence(self.mode.universe,
                     [conf, conf+offset, conf, conf-offset], 1)

#
# 2D mode viewer
#
class ModeViewer2D(Toplevel):

    def __init__(self, master, mode_projector):
        Toplevel.__init__(self, master)
        self.title("2D Mode Projection")
        self.mode_projector = mode_projector
        frame = Frame(self)
        frame.pack(side=TOP, fill=BOTH, expand=YES)
        self.xnum = IntEntry(frame, "X mode number: ", 6, 6,
                             mode_projector.numberOfModes()-1)
        self.xnum.pack(side=LEFT)
        self.xnum.bind('<Return>', self.draw)
        self.ynum = IntEntry(frame, "  Y mode number: ", 7, 6,
                             mode_projector.numberOfModes()-1)
        self.ynum.pack(side=LEFT)
        self.ynum.bind('<Return>', self.draw)
        self.plot = PlotCanvas(self, 400, 400)
        self.plot.pack(side=TOP, fill=BOTH, expand=YES)
        self.draw()

    def draw(self, event=None):
        xnum = self.xnum.get()
        ynum = self.ynum.get()
        self.mode_projector.calculateProjections([xnum, ynum])
        data = self.mode_projector[ynum]
        data[:, 0] = self.mode_projector[xnum][:, 1]
        self.plot.clear()
        self.plot.draw(PolyLine(data, color = 'red'))

#
# 3D mode viewer
#
class ModeViewer3D(Toplevel):

    def __init__(self, master, mode_projector):
        Toplevel.__init__(self, master)
        self.title("3D Mode Projection")
        self.mode_projector = mode_projector
        frame = Frame(self)
        frame.pack(side=TOP, fill=BOTH, expand=YES)
        self.xnum = IntEntry(frame, "X mode number: ", 6, 6,
                             mode_projector.numberOfModes()-1,
                             fg='red')
        self.xnum.pack(side=TOP)
        self.xnum.bind('<Return>', self.draw)
        self.ynum = IntEntry(frame, "Y mode number: ", 7, 6,
                             mode_projector.numberOfModes()-1,
                             fg='yellow')
        self.ynum.pack(side=TOP)
        self.ynum.bind('<Return>', self.draw)
        self.znum = IntEntry(frame, "Z mode number: ", 8, 6,
                             mode_projector.numberOfModes()-1,
                             fg='green')
        self.znum.pack(side=TOP)
        self.znum.bind('<Return>', self.draw)
        self.plot = VisualizationCanvas(self, 400, 400)
        self.plot.pack(side=TOP, fill=BOTH, expand=YES)
        self.draw()

    def draw(self, event=None):
        xnum = self.xnum.get()
        ynum = self.ynum.get()
        znum = self.znum.get()
        self.mode_projector.calculateProjections([xnum, ynum, znum])
        x = self.mode_projector[xnum]
        data = Numeric.zeros((len(x), 3), Numeric.Float)
        data[:, 0] = x[:, 1]
        data[:, 1] = self.mode_projector[ynum][:, 1]
        data[:, 2] = self.mode_projector[znum][:, 1]
        minv = Numeric.minimum.reduce(data)
        maxv = Numeric.maximum.reduce(data)
        scale = maxv-minv
        reference = minv-0.05*scale
        xaxis = PolyLine3D([reference,
                            reference+scale*Numeric.array([0.2, 0., 0.])],
                           color='red')
        yaxis = PolyLine3D([reference,
                            reference+scale*Numeric.array([0., 0.2, 0.])],
                           color='yellow')
        zaxis = PolyLine3D([reference,
                            reference+scale*Numeric.array([0., 0., 0.2])],
                           color='green')
        graphics = [PolyLine3D(data, color = 'blue'), xaxis, yaxis, zaxis]
        self.plot.clear()
        self.plot.draw(VisualizationGraphics(graphics))

#
# Trajectory viewer window
#
class TrajectoryViewer(Tkwindow):

    def __init__(self, master, trajectory):
        Tkwindow.__init__(self, master)
        self.filename = None
        if type(trajectory) == type(''):
            if string.find(trajectory, ':') >= 0 and tmanager is not None:
                self.filename = trajectory
                self.inspector = tmanager.trajectoryInspector(trajectory)
                self.inspector.reopen()
            else:
                self.filename = trajectory
                self.inspector = TrajectoryInspector(trajectory)
        else:
            self.inspector = TrajectoryInspector(trajectory)
        if self.filename is not None:
            self.title(self.filename)
        self.description = self.inspector.description()
        self.universe = None
        self.categories = categorizeVariables(self.inspector.variableNames())
        step_number = Numeric.array(self.inspector.readScalarVariable('step'))
        jumps = Numeric.less(step_number[1:]-step_number[:-1], 0)
        self.restarts = Numeric.repeat(Numeric.arange(len(jumps)), jumps)+1
        self.restarts = list(self.restarts)
        try:
            self.time = \
                      Numeric.array(self.inspector.readScalarVariable('time'))
            jumps = Numeric.repeat(Numeric.arange(len(self.time)-1),
                                   Numeric.less(self.time[1:],
                                                self.time[:-1]))+1
            if len(jumps) > 0:
                for jump in jumps[::-1]:
                    dt = self.time[jump-1] + self.time[jump+1] \
                         - 2*self.time[jump]
                    try:
                        # Numeric
                        typecode = self.time.typecode()
                    except AttributeError:
                        # numpy
                        typecode = self.time.dtype.char
                    self.time[jump:] = (self.time[jump:] + dt).astype(typecode)
        except KeyError:
            self.time = 1.*Numeric.arange(self.inspector.numberOfSteps())
        self.plotlist = []
        self.selection = None
        self._createMenu()
        self._createMainBox()
        self.open()

    def _createMainBox(self):
        self.status = StatusBar(self)
        self.status.pack(side=BOTTOM, anchor=W, fill=BOTH)
        if self.filename is None:
            text = []
        else:
            text = ['Trajectory file: ' + self.filename, '']
        comment = self.inspector.comment()
        if len(comment) > 0:
            text.append(comment)
            text.append('')
        natoms = self.inspector.numberOfAtoms()
        nsteps = self.inspector.numberOfSteps()
        text.append(`natoms` + ' atoms, ' + `nsteps` + ' steps')
        text.append('')
        Label(self, text=string.join(text, '\n'), justify=LEFT).pack(side=TOP)
        animation = Frame(self)
        animation.pack(side=LEFT)
        Label(animation, text = 'First: ').grid(row=0, column=0)
        self.first_step = Entry(animation)
        self.first_step.grid(row=0, column=1)
        Label(animation, text = 'Last:  ').grid(row=1, column=0)
        self.last_step = Entry(animation)
        self.last_step.grid(row=1, column=1)
        Label(animation, text = 'Skip:  ').grid(row=2, column=0)
        self.skip_step = Entry(animation)
        self.skip_step.grid(row=2, column=1)
        self.first_step.insert(0, '1')
        self.last_step.insert(0, `nsteps`)
        self.skip_step.insert(0, `max(1, nsteps/100)`)
        button_box = Frame(animation)
        button_box.grid(column=3, row=0, rowspan=3)
        Button(button_box, text = 'Start Animation',
               command=self._animation).pack(side=TOP, fill=X)
        Button(button_box, text = 'Export PDB',
               command=self._export).pack(side=TOP, fill=X)

    def _createMenu(self):
        #menu_bar = Menu(self)
        menu_bar = Frame(self, relief=RAISED, bd=2)
        menu_bar.pack(side=TOP, fill=X)
        self._createFileMenu(menu_bar)
        self._createViewMenu(menu_bar)
        if string.find(self.description, "l('Protein'") >= 0:
            self._createProteinMenu(menu_bar)

    def _createFileMenu(self, menu_bar):
        menu_button = Menubutton(menu_bar, text='File', underline=0)
        menu_button.pack(side=LEFT)
        menu = Menu(menu_button)
        #menu = Menu(menu_bar, tearoff=0)
        menu.add_command(label='Open...', command=self._open)
        if tmanager is not None:
            menu.add_command(label='Open remote...', command=self._openRemote)
        menu.add_separator()
        menu.add_command(label='Close', command=self.close)
        menu.add_command(label='Quit', command=self.quit)
        menu_button['menu'] = menu

    def _createViewMenu(self, menu_bar):
        menu_button = Menubutton(menu_bar, text='View', underline=0)
        menu_button.pack(side=LEFT)
        menu = Menu(menu_button)
        #menu = Menu(menu_bar, tearoff=0)
        categories = self.categories.keys()
        categories = filter(lambda c, cl=categories: c in cl,
                            ['energy', 'thermodynamic', 'auxiliary'])
        for category in categories:
            menu.add_command(label=string.capitalize(category),
                             command=lambda s=self, c=category: s._viewData(c))
        menu.add_separator()
        menu.add_command(label='History', command=self._showhistory)
        menu_button['menu'] = menu

    def _createProteinMenu(self, menu_bar):
        menu_button = Menubutton(menu_bar, text='Proteins', underline=0)
        menu_button.pack(side=LEFT)
        menu = Menu(menu_button)
        #menu = Menu(menu_bar, tearoff=0)
        menu.add_command(label='Rigid-body motion',
                         command=self._rbProjection)
        menu.add_separator()
        menu.add_command(label='Mode projection overview',
                         command=self._projectionOverview)
        menu.add_command(label='Low-frequency modes projection',
                         command=self._projectionLow)
        menu.add_command(label='High-frequency modes projection',
                         command=self._projectionHigh)
        menu.add_separator()
        menu.add_command(label='2D projection',
                         command=self._modeProjection2D)
        menu.add_command(label='3D projection',
                         command=self._modeProjection3D)
        menu_button['menu'] = menu

    def _missing(self):
        Dialog.Dialog(self, title='Undefined operation',
                      text='This operation is not yet implemented.',
                      bitmap='warning', default=0,
                      strings = ('Cancel',))

    def _open(self):
        fd = FileDialog.LoadFileDialog(self)
        file = fd.go(key='OpenTrajectory', pattern='*.nc')
        if file is not None:
            TrajectoryViewer(None, file)

    def _openRemote(self):
        window = Tkwindow(self)
        window.title("Remote trajectories")
        self.remote_window = window
        frame = Frame(window)
        frame.pack(side=TOP, expand=YES, fill=BOTH)
        scrollbar = Scrollbar(frame, orient=VERTICAL)
        self.remote = Listbox(frame, selectmode=EXTENDED, relief=SUNKEN,
                              width=60, height=10,
                              yscrollcommand=scrollbar.set)
        for name in tmanager.trajectoryList():
            self.remote.insert(END, name)
        scrollbar.config(command=self.remote.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.remote.pack(side=TOP, fill=BOTH, expand=YES)
        button_bar = Frame(window)
        button_bar.pack(side=BOTTOM, fill=X, expand=YES)
        Button(button_bar, text='Open',
               command=self._openRemoteFiles).pack(side=LEFT)
        Button(button_bar, text='Cancel',
               command=window.destroy).pack(side=RIGHT)
        window.open()

    def _openRemoteFiles(self):
        items = self.remote.curselection()
        try:
            items = map(string.atoi, items)
        except ValueError: pass
        files = []
        for item in items:
            files.append(self.remote.get(item))
        self.remote_window.destroy()
        for file in files:
            TrajectoryViewer(None, file)

    def _registerPlot(self, plot_canvas):
        self.plotlist.append(plot_canvas)

    def _unregisterPlot(self, plot_canvas):
        try:
            self.plotlist.remove(plot_canvas)
        except ValueError:
            pass

    def _selectRange(self, range):
        if range is None:
            first = 0
            last = self.inspector.numberOfSteps()
            self.selection = None
        else:
            first = Numeric.sum(Numeric.less(self.time, range[0]))
            last = Numeric.sum(Numeric.less(self.time, range[1]))
            self.selection = (first, last)
        skip = max(1, (last-first)/100)
        self.first_step.delete(0, END)
        self.first_step.insert(0, `first`)
        self.last_step.delete(0, END)
        self.last_step.insert(0, `last`)
        self.skip_step.delete(0, END)
        self.skip_step.insert(0, `skip`)
        for plot_canvas in self.plotlist:
            if range is None:
                plot_canvas.select(None)
            else:
                plot_canvas.select((self.time[first], self.time[last]))

    def _showhistory(self):
        TextViewer(self, self.inspector.history(), 'History')

    def _viewData(self, category):
        variable_names = self.categories[category][:]
        if category == 'configuration':
            self._missing()
        elif category == 'energy':
            EnergyViewer(self, string.capitalize(category),
                         self.time, self.inspector, variable_names)
        else:
            PlotViewer(self, string.capitalize(category),
                       self.time, self.inspector, variable_names)

    def _makeUniverse(self):
        import MMTK.Skeleton
        import MMTK.ForceFields
        if self.universe is None:
            self.status.set("Constructing model")
            local = {}
            skeleton = eval(self.description, vars(MMTK.Skeleton), local)
            self.universe = skeleton.make({})
            self.mode_projector = None
            self.rb_projector = None
            self.temperature = None
            self.status.clear()

    def _animation(self):
        first = string.atoi(self.first_step.get())-1
        last = string.atoi(self.last_step.get())
        skip = string.atoi(self.skip_step.get())
        self._makeUniverse()
        from MMTK.Visualization import viewSequence
        viewSequence(self.universe,
                     ConfigurationFactory(self.universe, self.inspector,
                                          range(first, last, skip)))

    def _export(self):
        first = string.atoi(self.first_step.get())-1
        last = string.atoi(self.last_step.get())
        skip = string.atoi(self.skip_step.get())
        self._makeUniverse()
        numbers = range(first, last, skip)
        conf = ConfigurationFactory(self.universe, self.inspector, numbers)
        for i in range(len(numbers)):
            n = numbers[i]
            self.universe.writeToFile("conf%d.pdb" % n, conf[i], 'pdb')

    def _rbProjection(self):
        self._makeUniverse()
        if self.rb_projector is None:
            last = self.inspector.numberOfSteps()
            skip = max(1, last/500)
            traj = ConfigurationFactory(self.universe, self.inspector,
                                        range(0, last, skip))
            time = self.time[0:last:skip]
            self.status.set("Calculating projections")
            self.rb_projector = RBProjector(traj, time)
            self.rb_projector.calculateProjections(range(6))
            self.status.clear()
        RBProjectionViewer(self, self.rb_projector)

    def _projectionOverview(self):
        self.modeProjection(None)

    def _projectionLow(self):
        self.modeProjection([6, 7, 8, 9])

    def _projectionHigh(self):
        self.modeProjection([-4, -3, -2, -1])

    def modeProjection(self, indices):
        self._makeModeProjector()
        if indices is None:
            nmodes = self.mode_projector.numberOfModes()-6
            skip = max(2, nmodes/3)-1
            indices = range(6, 6+min(nmodes, 4*skip), skip)

        self.status.set("Calculating projections")
        self.mode_projector.calculateProjections(indices)
        self.status.clear()
        ModeProjectionViewer(self, self.mode_projector, indices)

    def _makeModeProjector(self):
        self._makeUniverse()
        if self.mode_projector is None:
            self._getTemperature()
            if self.temperature is None:
                return
            self.status.set("Calculating normal modes")
            last = self.inspector.numberOfSteps()
            skip = max(1, last/500)
            traj = ConfigurationFactory(self.universe, self.inspector,
                                        range(0, last, skip))
            time = self.time[0:last:skip]
            self.mode_projector = ModeProjector(traj, time, self.temperature)
            self.status.clear()
    
    def _getTemperature(self):
        try:
            t = self.inspector.readScalarVariable('temperature', 0, None, 1)
            self.temperature = Numeric.add.reduce(t)/len(t)
        except KeyError:
            window = TemperatureDialog(self)
            self.temperature = window.result

    def _modeProjection2D(self):
        self._makeModeProjector()
        ModeViewer2D(self, self.mode_projector)

    def _modeProjection3D(self):
        self._makeModeProjector()
        ModeViewer3D(self, self.mode_projector)


class ConfigurationFactory:

    def __init__(self, universe, inspector, indices):
        self.universe = universe
        self.inspector = inspector
        self.indices = indices

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, item):
        index = self.indices[item]
        cell, conf = self.inspector.readConfiguration(index)
        if cell is not None:
            cell = cell.astype(Numeric.Float)
        conf = conf.astype(Numeric.Float)
        conf = MMTK.Configuration(self.universe, conf, cell)
        self.universe.setConfiguration(conf)
        return conf

    def __getslice__(self, first, last):
        return ConfigurationFactory(self.universe, self.inspector,
                                    self.indices[first:last])

class ModeProjector:

    def __init__(self, trajectory, time, temperature):
        from MMTK.NormalModes import EnergeticModes
        self.raw_trajectory = trajectory
        self.trajectory = None
        self.time = time
        self.temperature = temperature
        self.cache = {}

        self._makeUniverse()
        self.modes = EnergeticModes(self.universe_calpha, temperature=None)

    def numberOfModes(self):
        return len(self.modes)

    def _makeUniverse(self):
        from MMTK.Proteins import Protein, PeptideChain
        from MMTK.ForceFields import CalphaForceField
        self.universe = self.raw_trajectory.universe
        self.proteins = self.universe.objectList(Protein)
        universe_calpha = MMTK.InfiniteUniverse(CalphaForceField(2.5))
        calpha_map = {}
        for protein in self.proteins:
            chains_calpha = []
            for chain in protein:
                chains_calpha.append(PeptideChain(chain.sequence(),
                                                  model='calpha'))
            protein_calpha = Protein(chains_calpha)
            universe_calpha.addObject(protein_calpha)
            for i in range(len(protein)):
                chain = protein[i]
                chain_calpha = protein_calpha[i]
                for j in range(len(chain)):
                    calpha_map[chain[j].peptide.C_alpha] = \
                                        chain_calpha[j].peptide.C_alpha
                    chain_calpha[j].peptide.C_alpha.setMass(1.)
        conf = self.raw_trajectory[0]
        for atom, calpha in calpha_map.items():
            calpha.setPosition(conf[atom])
        self.universe_calpha = universe_calpha
        universe_calpha.configuration()
        self.map = universe_calpha.numberOfAtoms()*[None]
        for atom, calpha in calpha_map.items():
            self.map[calpha.index] = atom.index

    def _extractTrajectory(self):
        if self.trajectory is not None:
            return
        self.trajectory = []
        universe = self.universe
        universe_calpha = self.universe_calpha
        conf_calpha_0 = universe_calpha.configuration()
        for conf in self.raw_trajectory:
            conf = self.universe.contiguousObjectConfiguration(self.proteins,
                                                               conf)
            array = Numeric.take(conf.array, self.map)
            conf_calpha = MMTK.ParticleVector(universe_calpha, array)
            tr, rms = universe_calpha.findTransformation(conf_calpha)
            tr = tr.inverse()
            for a in universe_calpha.atomList():
                conf_calpha[a] = tr(conf_calpha[a])
            conf_calpha = conf_calpha-conf_calpha_0
            self.trajectory.append(conf_calpha)

    def calculateProjections(self, indices):
        calc = []
        for i in indices:
            if not self.cache.has_key(i):
                calc.append(i)
        if not calc:
            return
        self._extractTrajectory()
        proj = []
        for conf_calpha in self.trajectory:
            p = []
            for i in calc:
                p.append(conf_calpha.dotProduct(self.modes[i]))
            proj.append(p)
        proj = Numeric.transpose(Numeric.array(proj))
        for i in range(len(calc)):
            self.cache[calc[i]] = proj[i]

    def __getitem__(self, item):
        try:
            series = self.cache[item]
        except KeyError:
            self.calculateProjections([item])
            series = self.cache[item]
        return Numeric.transpose(Numeric.array([self.time, series]))

    def amplitude(self, number):
        force_constant = self.modes[number].force_constant
        return Numeric.sqrt(self.temperature*MMTK.Units.k_B/force_constant)


class RBProjector(ModeProjector):

    def __init__(self, trajectory, time):
        self.raw_trajectory = trajectory
        self.time = time
        self.cache = {}
        self.modes = []
        self._makeUniverse()
        for i in range(3):
            v = MMTK.ParticleVector(self.universe_calpha)
            v.array[:, i] = 1.
            self.modes.append(v.scaledToNorm(1.))
        for e in [MMTK.Vector(1., 0., 0.),
                  MMTK.Vector(0., 1., 0.),
                  MMTK.Vector(0., 0., 1.)]:
            v = MMTK.ParticleVector(self.universe_calpha)
            for a in self.universe_calpha.atomList():
                v[a] = e.cross(a.position())
            self.modes.append(v.scaledToNorm(1.))

    def calculateProjections(self, indices):
        calc = []
        for i in indices:
            if not self.cache.has_key(i):
                calc.append(i)
        if not calc:
            return
        universe = self.universe
        universe_calpha = self.universe_calpha
        conf_calpha_0 = universe_calpha.configuration()
        proj = []
        for conf in self.raw_trajectory:
            conf = self.universe.contiguousObjectConfiguration(self.proteins,
                                                               conf)
            array = Numeric.take(conf, self.map)
            conf_calpha = MMTK.ParticleVector(universe_calpha, array)
            conf_calpha = conf_calpha-conf_calpha_0
            p = []
            for i in calc:
                p.append(conf_calpha.dotProduct(self.modes[i]))
            proj.append(p)
        proj = Numeric.transpose(Numeric.array(proj))
        for i in range(len(calc)):
            self.cache[calc[i]] = proj[i]

    def amplitude(self, number):
        raise ValueError


if __name__ == '__main__':

    import sys
    if len(sys.argv) < 2:
        sys.stderr.write('No trajectory specified\n')
        sys.exit()
    for trajectory in sys.argv[1:]:
        TrajectoryViewer(None, trajectory)
