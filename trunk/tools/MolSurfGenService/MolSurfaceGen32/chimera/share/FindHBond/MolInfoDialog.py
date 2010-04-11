import chimera
from OpenSave import SaveModeless
class SaveMolInfoDialog(SaveModeless):
	oneshot = True

	def __init__(self, info, callback, **kw):
		self.info = info
		self.callback = callback
		SaveModeless.__init__(self, clientPos='s', **kw)

	def fillInUI(self, parent):
		SaveModeless.fillInUI(self, parent)

		from chimera.tkoptions import NamingStyleOption
		self.namingStyle = NamingStyleOption(self.clientArea, 0, None,
								None, None)

	def Apply(self):
		paths = self.getPaths()
		if not paths:
			return
		self.callback(paths[0], self.info, self.namingStyle.get())
