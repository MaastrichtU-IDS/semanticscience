from OpenSave import SaveModeless

name = "Export Scene"

class ExportDialog(SaveModeless):
	title = name
	help = "UsersGuide/export.html"

	def __init__(self, **kw):
		import exports
		self.notes = None
		filterInfo = exports.getFilterInfo()
		self.addedSceneTypes = set([i[0] for i in filterInfo])
		SaveModeless.__init__(self, clientPos='s', clientSticky='ew',
				filters=filterInfo, defaultFilter='X3D',
				command=self._command,
				setFilterCommand=self._setFilterCB, **kw)

	def fillInUI(self, parent):
		import Tkinter as Tk
		import Pmw
		from HtmlText import HtmlText
		SaveModeless.fillInUI(self, parent)
		parent = self.clientArea
		self.notes = Pmw.ScrolledText(parent, text_pyclass=HtmlText,
				text_relief=Tk.FLAT, text_wrap=Tk.WORD,
				text_height=4, text_width=10,
				text_highlightthickness=0)
		self.notes.pack(side=Tk.TOP, anchor=Tk.NW, fill=Tk.BOTH,
						expand=True, pady=5, padx=10)
		self.notes.configure(text_state=Tk.DISABLED,
			hscrollmode='dynamic', vscrollmode='dynamic',
			text_background=parent.cget('background'))
		import exports
		self.notes.settext(exports.getNotes(self.getFilter()))

	def enter(self):
		# if any new export types have been added,
		# then add them to the dialog
		import exports
		filterInfo = exports.getFilterInfo()
		for pos, fi in enumerate(filterInfo):
			if fi[0] in self.addedSceneTypes:
				continue
			self.addedSceneTypes.add(fi[0])
			self.addFilter(fi, pos)
		# next do the normal enter stuff
		SaveModeless.enter(self)

	def _setFilterCB(self, descript):
		if not self.notes:
			return
		import exports
		self.notes.settext(exports.getNotes(descript))

	def _command(self, okayed, dialog):
		if not okayed:
			return
		paths = dialog.getPaths()
		if len(paths) == 1:
			import exports
			exports.doExportCommand(self.getFilter(), paths[0])
