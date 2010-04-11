import chimera.extension

class BildEMO(chimera.extension.EMO):
	fileType = 'Bild'
	exts = [ '.bild', '.bld' ]

	def name(self):
		return 'Bild'
	def description(self):
		return 'open Bild graphics file'
	def categories(self):
		return ['Utilities']
	def activate(self):
		self.gui()
		return None

	def gui(self):
		from OpenSave import OpenModeless
		globs = []
		for ext in self.exts:
			globs.append('*' + ext)
		OpenModeless(title='Open Bild File', command=self._openCB,
			filters=[(self.fileType, globs)],
			defaultFilter=self.fileType,
			historyID='bild open file', dialogKw={'oneshot':1})

	def open(self, filename, identifyAs=None):
		return self.module().openBild(filename, identifyAs=identifyAs)

	def _openCB(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			self.open(path)

emo = BildEMO(__file__)
#chimera.extension.manager.registerExtension(emo)
chimera.fileInfo.register(emo.fileType, emo.open,
			  emo.exts, [ emo.fileType.lower() ],
			  category=chimera.FileInfo.GENERIC3D)
