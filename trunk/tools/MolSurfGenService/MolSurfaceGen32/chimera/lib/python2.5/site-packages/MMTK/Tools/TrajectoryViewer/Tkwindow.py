import Tkinter

_root = Tkinter.Tk()
_mainloop_started = 0
_open_windows = []

class Tkwindow(Tkinter.Toplevel):

    def __init__(self, master):
	if master is None:
	    master = _root
	else:
	    master.addDependent(self)
	Tkinter.Toplevel.__init__(self, master)
	self.protocol("WM_DELETE_WINDOW", self.close)
	self._dependents = []

    def open(self):
	global _mainloop_started
	_open_windows.append(self)
	if not _mainloop_started:
	    _root.withdraw()
	    _root.mainloop()
	    _mainloop_started = 1

    def close(self):
	for window in self._dependents:
	    window.close()
	self.destroy()
	if self.master is not _root:
	    self.master.removeDependent(self)
	_open_windows.remove(self)
	if not _open_windows:
	    _root.destroy()

    def addDependent(self, window):
	self._dependents.append(window)

    def removeDependent(self, window):
	self._dependents.remove(window)


if __name__ == '__main__':

    class Test(Tkwindow):

	def __init__(self, master = None):
	    Tkwindow.__init__(self, master)
	    Tkinter.Button(self, text='Clone', command=self.clone).pack()
	    self.open()

	def clone(self):
	    Test()

    Test()
