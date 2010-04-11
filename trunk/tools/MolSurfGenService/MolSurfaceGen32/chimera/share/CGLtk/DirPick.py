# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkinter, Tix, os

class DirPick:
	"""Pick directory"""

	def __init__(self, master=None, query="Pick Directory", startDir=None,
			showHidden=0):
		self.dialog = Tkinter.Frame(master)
		toplevel = self.dialog.winfo_toplevel()
		toplevel.title(query)
		toplevel.protocol('WM_DELETE_WINDOW', self.cancel)
		try:
			self.dialog.tk.call('load', '', 'Tix')
		except Tkinter.TclError:
			self.dialog.tk.call('package', 'require', 'Tix')

		self.dir = Tkinter.StringVar(self.dialog)
		# initialize dir with legal directory
		self.dir.set(os.path.abspath(os.curdir))
		self.dir.trace_variable('w', self.updateDirList)

		keywds = { "value":self.dir.get(), "browsecmd":self.dirBrowse }
		if showHidden:
			keywds["showhidden"] = 1
		self.dirlist = apply(Tix.DirList, (self.dialog,), keywds)
		self.dirlist.pack(side=Tkinter.TOP, fill=Tkinter.BOTH,
								expand=1)
		# now set dir to what we want it to start out as
		if startDir:
			self.dir.set(startDir)

		installdir = Tix.LabelEntry(self.dialog, label=query,
			labelside=Tkinter.TOP, pady=4,
			options="entry.width 30 label.anchor w")
		installdir.entry.config(textvariable=self.dir)
		#installdir.entry.bind('<Return>', ??)
		installdir.pack(side=Tkinter.TOP, expand=1, fill=Tkinter.X,
					anchor=Tkinter.S, padx=4, pady=4)

		box = Tix.ButtonBox(self.dialog,
						orientation=Tkinter.HORIZONTAL)
		box.add('ok', text='OK', width=6, command=self.ok)
		box.add('cancel', text='Cancel', width=6, command=self.cancel)
		box.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
		self.dialog.pack(fill=Tkinter.BOTH, expand=1)

	def cancel(self, *args):
		self.dialog.quit()

	def ok(self, *args):
		self.returnValue = 1
		self.dialog.quit()

	def dirBrowse(self, value):
		self.dir.set(value)

	def updateDirList(self, *args):
		dir = self.dir.get()
		if dir[-1] != os.sep:
			return
		try:
			self.dirlist.chdir(dir)
		except Tkinter.TclError:
			end = dir.rfind(os.sep)
			if end == -1:
				return
			dir = dir[:end]
			try:
				self.dirlist.chdir(dir)
			except Tkinter.TclError:
				pass

	def run(self):
		self.returnValue = 0
		toplevel = self.dialog.winfo_toplevel()
		toplevel.deiconify()
		toplevel.lift()
		self.dialog.mainloop()
		toplevel.withdraw()
		if self.returnValue:
			return self.dir.get()
		else:
			return None

if __name__ == '__main__':
	print DirPick(query="Choose Chimera Installation directory").run()
