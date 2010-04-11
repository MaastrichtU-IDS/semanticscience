# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera
from chimera.baseDialog import ModelessDialog

MatchErrorText = 'You must select one reference and one alternative ensemble'
TileErrorText = 'You must select one ensemble to tile'
ScaleErrorText = 'Scale must be between -1 and 1'
PenaltyErrorText = 'Penalty ratio must be between 0 and 1'

def getEnsembles():
	modelList = chimera.openModels.list(modelTypes=[chimera.Molecule])
	modelDict = {}
	for m in modelList:
		try:
			modelDict[m.id].append(m)
		except KeyError:
			modelDict[m.id] = [m]
	ensembleList = []
	for i, ml in modelDict.items():
		ensembleList.append((i, ml[0].name))
	ensembleList.sort()
	return modelDict, ensembleList

class EnsembleMatchCB(ModelessDialog):
	title = "Ensemble Match"
	help = "ContributedSoftware/ensemblematch/ensemblematch.html"
	oneshot = True

	def __init__(self, *args, **kw):
		self.modelDict, self.ensembleList = getEnsembles()
		self.itemList = [ '%d: %s' % t for t in  self.ensembleList ]
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Tkinter
		import Pmw
		self.selectionField = Pmw.EntryField(parent,
					labelpos='w',
					label_text='Parts to Match:')
		self.selectionField.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)

		self.refListbox = Pmw.ScrolledListBox(parent,
					items=self.itemList,
					listbox_exportselection=Tkinter.FALSE,
					labelpos='n',
					label_text='Reference')
		self.refListbox.pack(side=Tkinter.LEFT, expand=Tkinter.TRUE,
					fill=Tkinter.BOTH)
		self.altListbox = Pmw.ScrolledListBox(parent,
					items=self.itemList,
					listbox_exportselection=Tkinter.FALSE,
					labelpos='n',
					label_text='Alternative')
		self.altListbox.pack(side=Tkinter.LEFT, expand=Tkinter.TRUE,
					fill=Tkinter.BOTH)

	def Apply(self):
		ref = self.refListbox.getcurselection()
		alt = self.altListbox.getcurselection()
		if len(ref) != 1 or len(alt) != 1:
			import chimera
			raise chimera.UserError(MatchErrorText)
		n = self.itemList.index(ref[0])
		refId = self.ensembleList[n][0]
		n = self.itemList.index(alt[0])
		altId = self.ensembleList[n][0]
		subSelection = self.selectionField.get().strip()
		import base
		base.EnsembleMatch(self.modelDict[refId],
						self.modelDict[altId],
						subSelection)

class EnsembleClusterCB(ModelessDialog):
	title = "Ensemble Cluster"
	help = "ContributedSoftware/ensemblecluster/ensemblecluster.html"
	oneshot = True

	def __init__(self, *args, **kw):
		self.modelDict, self.ensembleList = getEnsembles()
		self.itemList = [ '%d: %s' % t for t in self.ensembleList ]
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Tkinter
		import Pmw
		self.selectionField = Pmw.EntryField(parent,
					labelpos='w',
					label_text='Parts to Match:')
		self.selectionField.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
		self.listbox = Pmw.ScrolledListBox(parent,
					items=self.itemList,
					listbox_exportselection=Tkinter.FALSE,
					labelpos='n',
					label_text='Ensemble to Cluster')
		self.listbox.pack(side=Tkinter.LEFT, expand=Tkinter.TRUE,
					fill=Tkinter.BOTH)
		if len(self.itemList) == 1:
			self.listbox.setvalue(self.itemList)

	def Apply(self):
		sel = self.listbox.getcurselection()
		if len(sel) != 1:
			import chimera
			raise chimera.UserError(TileErrorText)
		n = self.itemList.index(sel[0])
		id = self.ensembleList[n][0]
		subSelection = self.selectionField.get().strip()
		import base
		base.cluster(self.modelDict[id], subSelection)

class TileStructuresCB(ModelessDialog):
	title = "Tile Structures"
	help = "ContributedSoftware/ensembletile/ensembletile.html"
	oneshot = True

	def configure(self, models=[]):
		self.modListBox.setvalue(models)

	def fillInUI(self, parent):
		import Tkinter
		import Pmw
		self.scale = Pmw.Counter(parent, 
					labelpos="w",
					label_text="Border scale:",
					entryfield_value=1.0,
					datatype={ "counter":"real" },
					entryfield_validate={
						"validator":"real",
						"min":0.0,
						"max":2.0,
					},
					increment=0.1)
		self.scale.pack(side=Tkinter.BOTTOM, expand=Tkinter.FALSE,
					fill=Tkinter.X)
		from chimera.widgets import ModelScrolledListBox
		self.modListBox = ModelScrolledListBox(parent,
					listbox_selectmode="extended",
					labelpos="n",
					label_text="Models")
		self.modListBox.pack(side=Tkinter.LEFT, expand=Tkinter.TRUE,
					fill=Tkinter.BOTH)

	def Apply(self):
		modList = self.modListBox.getvalue()
		if len(modList) == 0:
			import chimera
			raise chimera.UserError("No models selected")
		ef = self.scale.component("entryfield")
		if not ef.valid():
			import chimera
			raise chimera.UserError(ScaleErrorText)
		s = float(ef.getvalue())
		import base
		base.tile(modList, s)

from chimera import dialogs
dialogs.register(TileStructuresCB.name, TileStructuresCB)
