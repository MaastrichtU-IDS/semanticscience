# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AssociationsDialog.py 29598 2009-12-11 21:37:51Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from chimera.misc import oslModelCmp
import Pmw, Tkinter
from MAViewer import ADD_ASSOC, DEL_ASSOC, MOD_ALIGN

class AssociationsDialog(ModelessDialog):
	"""Allow the user to change structure/sequence associations"""

	buttons = ("OK", "Apply", "Close")
	help = "ContributedSoftware/multalignviewer/multalignviewer.html" \
							"#assocpanel"

	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Structure/Sequence Associations for %s" % (
								mav.title,)
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		self.parent = parent
		self.assocInfo = {}
		col1 = Tkinter.Label(parent, text="Model")
		col1.grid(row=0, column=0)
		col2 = Tkinter.Label(parent, text="Chain")
		col2.grid(row=0, column=1)
		col3 = Tkinter.Label(parent, text="Association")
		col3.grid(row=0, column=2)
		self._postDeletionID = None
		self._newModelsCB()
		for aseq in self.mav.seqs:
			try:
				mapDict = aseq.matchMaps
			except AttributeError:
				continue
			self._addAssocCB(newAssocs=mapDict.values())
		self.addAssocHandlerID = self.mav.triggers.addHandler(ADD_ASSOC,
							self._addAssocCB, None)
		self.delAssocHandlerID = self.mav.triggers.addHandler(DEL_ASSOC,
							self._delAssocCB, None)
		self.modAlignHandlerID = self.mav.triggers.addHandler(MOD_ALIGN,
							self._modAlignCB, None)
		self.addHandlerID = chimera.openModels.addAddHandler(
			self._newModelsCB, None)
		self.removeHandlerID = chimera.openModels.addRemoveHandler(
			self._closeModelsCB, None)

	def _addAssocCB(self, trigName=None, myData=None, newAssocs=[]):
		for matchMap in newAssocs:
			mseq = matchMap['mseq']
			mol = mseq.molecule
			try:
				assocInfo = self.assocInfo[mol]
			except KeyError:
				continue
			widgets = assocInfo['widgets']
			if widgets[1]:
				widgets[1].setvalue(mseq.name)
			widgets[2].setvalue(matchMap['aseq'].name)
			widgets[3].variable.set(False)
			widgets[3].button.grid_forget()

	def _assocMenuCB(self, val, widgets):
		if val ==  'none':
			widgets[3].button.grid()
		else:
			widgets[3].button.grid_forget()

	def _chainDeletionCB(self, *args):
		from chimera.triggerSet import ONESHOT
		if self._postDeletionID:
			return ONESHOT
		self._postDeletionID = self.uiMaster().after_idle(
							self._newModelsCB)
		return ONESHOT

	def _closeModelsCB(self, trigName=None, myData=None, models=[]):
		if not self.mav:
			# already destroyed
			return
		for mol in models:
			if mol not in self.assocInfo:
				continue
			for widget in self.assocInfo[mol]['widgets']:
				if not widget:
					continue
				widget.grid_forget()
				widget.destroy()
			del self.assocInfo[mol]
		if not chimera.openModels.list(modelTypes=[chimera.Molecule]):
			self.mav._disableAssociationsDialog()

	def _delAssocCB(self, trigName=None, myData=None, delAssocs=[]):
		for matchMap in delAssocs:
			mseq = matchMap['mseq']
			from chimera.Sequence import StructureSequence
			if not isinstance(mseq, StructureSequence):
				# model has closed and sequence updated;
				# model-close trigger should have cleaned things up
				continue
			mol = mseq.molecule
			if mol not in self.assocInfo:
				continue
			assocWidget, matchWidget = self.assocInfo[mol][
								'widgets'][2:4]
			assocWidget.setvalue('none')
			matchWidget.button.grid()

	def destroy(self):
		self.mav.triggers.deleteHandler(ADD_ASSOC,
							self.addAssocHandlerID)
		self.mav.triggers.deleteHandler(DEL_ASSOC,
							self.delAssocHandlerID)
		self.mav = None
		chimera.openModels.deleteAddHandler(self.addHandlerID)
		chimera.openModels.deleteRemoveHandler(self.removeHandlerID)
		ModelessDialog.destroy(self)

	def _modAlignCB(self, *args):
		for mol, info in self.assocInfo.items():
			seqMenu = info['widgets'][2]
			if mol in self.mav.associations:
				index = self.mav.seqs.index(
						self.mav.associations[mol]) + 1
			else:
				index = 0
			seqMenu.setitems(['none']
				+ [s.name for s in self.mav.seqs], index=index)

	def _newModelsCB(self, trigName=None, myData=None, models=None):
		mols = filter(lambda m: isinstance(m, chimera.Molecule),
						chimera.openModels.list())
		mols.sort(lambda a, b: oslModelCmp(a.oslIdent(), b.oslIdent()))
		for i in range(len(mols)):
			mol = mols[i]
			chains = mol.sequences()
			if mol in self.assocInfo:
				col = -1
				for widget in self.assocInfo[mol]['widgets']:
					col += 1
					if not widget:
						continue
					widget.grid_forget()
					if len(chains) == 0:
						widget.destroy()
					else:
						widget.grid(row=i+1, column=col,
								sticky='w')
				if len(chains) == 0:
					del self.assocInfo[mol]
				continue
			if len(chains) == 0:
				continue
			for chain in chains:
				chain.triggers.addHandler(chain.TRIG_DELETE,
						self._chainDeletionCB, None)
			assocInfo = {}
			self.assocInfo[mol] = assocInfo
			widgets = []
			assocInfo['widgets'] = widgets
			w = Tkinter.Label(self.parent,
				text="%s (%s)" % (mol.name, mol.oslIdent()))
			widgets.append(w)
			w.grid(row=i+1, column=0, sticky='w')

			if len(chains) > 1:
				w = Pmw.OptionMenu(self.parent,
					items=map(lambda s: s.name, chains))
				w.grid(row=i+1, column=1, sticky='w')
			else:
				w = None
			widgets.append(w)

			w = Pmw.OptionMenu(self.parent, items=['none']
					+ map(lambda s: s.name, self.mav.seqs),
					command=lambda v, w=widgets:
					self._assocMenuCB(v,w))
			widgets.append(w)
			w.grid(row=i+1, column=2, sticky='w')
				
			w = Tkinter.Frame(self.parent)
			widgets.append(w)
			w.grid(row=i+1, column=3, sticky='w')
			w.variable = Tkinter.IntVar(w)
			w.variable.set(False)
			w.button = Tkinter.Checkbutton(w, variable=w.variable,
				text="associate with best match")
			w.button.grid()

	def Apply(self):
		# block triggers to avoid having handlers prematurely
		# reset widgets...
		trigs = [DEL_ASSOC, ADD_ASSOC]
		for trig in trigs:
			self.mav.triggers.blockTrigger(trig)
		assocs = self.mav.associations
		for mol, info in self.assocInfo.items():
			widgets = info['widgets']
			if assocs.has_key(mol):
				aseq = assocs[mol]
				mseq = aseq.matchMaps[mol]['mseq']
				# sequences _could_ have the same name...
				if widgets[1] \
				and widgets[1].getvalue() != mseq.name \
				or widgets[2].index(Pmw.SELECT) - 1 != \
						self.mav.seqs.index(aseq):
					self.mav.disassociate(mol)
			if not assocs.has_key(mol):
				aseq = self.mav.seqs[widgets[2].index(
								Pmw.SELECT) - 1]
				if widgets[1]:
					mseq = mol.sequences()[
						widgets[1].index(Pmw.SELECT)]
				else:
					mseq = mol.sequences()[0]
				if widgets[2].getvalue() == 'none':
					if widgets[3].variable.get():
						self.mav.associate(mseq,
								force=True)
				else:
					self.mav.associate(mseq, seq=aseq,
								force=True)
		for trig in trigs:
			self.mav.triggers.releaseTrigger(trig)
