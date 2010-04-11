# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkinter
import Pmw

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from chimera import tkoptions
from CGLutil import vrml

import base

class Interface(ModelessDialog):

	title = 'Pipes and Planks'
	help = "ContributedSoftware/pipesandplanks/pipesandplanks.html"

	def fillInUI(self, parent):
		self.molecules = Pmw.ComboBox(parent, label_text=self.title,
						labelpos='nw')
		self.molecules.pack(side=Tkinter.TOP, fill=Tkinter.X)
		self.frame = Tkinter.Frame(parent)
		self.frame.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)

		import itertools
		row = itertools.count()

		#
		# Helix options
		#
		self.helixColor = tkoptions.ColorOption(
						self.frame, row.next(),
						'Helix color', 'red', None,
						noneOkay=0)
		self.helixFixedRadius = tkoptions.BooleanOption(
						self.frame, row.next(),
						'Fixed helix radius', 0, None)
		self.helixRadius = tkoptions.FloatOption(
						self.frame, row.next(),
						'Helix radius', 2.5, None)
		self.helixSplit = tkoptions.BooleanOption(
						self.frame, row.next(),
						'Split curved helices', 0, None)
		self.helixSplitRatio = tkoptions.FloatOption(
						self.frame, row.next(),
						'Helix split threshold',
						2.5, None)

		#
		# Strand options
		#
		self.strandColor = tkoptions.ColorOption(
						self.frame, row.next(),
						'Strand color', 'green', None,
						noneOkay=0)
		self.strandFixedWidth = tkoptions.BooleanOption(
						self.frame, row.next(),
						'Fixed strand width', 0, None)
		self.strandWidth = tkoptions.FloatOption(
						self.frame, row.next(),
						'Strand width', 4.0, None)
		self.strandFixedThickness = tkoptions.BooleanOption(
						self.frame, row.next(),
						'Fixed strand thickness',
						0, None)
		self.strandThickness = tkoptions.FloatOption(
						self.frame, row.next(),
						'Strand thickness', 0.25, None)
		self.strandSplit = tkoptions.BooleanOption(
						self.frame, row.next(),
						'Split curved strands', 0, None)
		self.strandSplitRatio = tkoptions.FloatOption(
						self.frame, row.next(),
						'Strand split threshold',
						2.5, None)

		#
		# Turn options
		#
		self.displayTurns = tkoptions.BooleanOption(
						self.frame, row.next(),
						'Display turns', True, None)
		self.turnColor = tkoptions.ColorOption(
						self.frame, row.next(),
						'Turn color', 'cyan', None,
						noneOkay=0)
		self.turnWidth = tkoptions.FloatOption(
						self.frame, row.next(),
						'Turn width', 0.5, None)
		self.turnThickness = tkoptions.FloatOption(
						self.frame, row.next(),
						'Turn thickness', 0.5, None)

		self.openModels = {}
		self.molTrigger = chimera.triggers.addHandler('Molecule',
						self._setMolList, None)
		self.vrmlTrigger = chimera.triggers.addHandler('VRMLModel',
						self._setVRMLList, None)
		self.molList = []
		self._setMolList()

	def _setMolList(self, triggerName=None, closure=None, m=None):
		if m and not m.created and not m.deleted:
			return
		molList = chimera.openModels.list(modelTypes=[chimera.Molecule])
		self.molList = map(lambda m: (m.name, m.id, m.subid), molList)
		self.molList.sort()
		nameList = map(lambda t: t[0], self.molList)
		self.molecules.setlist(nameList)
		if len(nameList) == 1:
			self.molecules.selectitem(0)

		if m:
			for mol in m.deleted:
				try:
					del self.openModels[mol]
				except KeyError:
					pass

	def _setVRMLList(self, triggerName=None, closure=None, m=None):
		if not m.deleted:
			return
		for mol, vrml in self.openModels.items():
			if vrml in m.deleted:
				del self.openModels[mol]

	def Apply(self):
		molList = chimera.openModels.list(modelTypes=[chimera.Molecule])
		selList = self.molecules.curselection() 
		if len(selList) != 1:
			return
		molName, molId, molSubid = self.molList[int(selList[0])]
		for m in molList:
			if m.id == molId and m.subid == molSubid:
				mol = m
				break
		else:
			replyobj.error('No selected molecule')
			return
		base.initialize()
		wrl = vrml.Transform()
		helices = base.displayHelices(mol, self.helixColor,
						self.helixFixedRadius.get(),
						self.helixRadius.get(),
						self.helixSplit.get(),
						self.helixSplitRatio.get())
		for node in helices:
			wrl.addChild(node)
		strands = base.displayStrands(mol, self.strandColor,
						self.strandFixedWidth.get(),
						self.strandWidth.get(),
						self.strandFixedThickness.get(),
						self.strandThickness.get(),
						self.strandSplit.get(),
						self.strandSplitRatio.get())
		for node in strands:
			wrl.addChild(node)
		if self.displayTurns.get():
			turns = base.displayTurns(mol, self.turnColor,
						self.turnWidth.get(),
						self.turnThickness.get())
			for node in turns:
				wrl.addChild(node)
		base.deinitialize()
		if not helices and not strands and not turns:
			replyobj.error('No helices, sheets, nor turns found')
			return
		try:
			chimera.openModels.close(self.openModels[mol])
		except KeyError:
			pass
		mList = chimera.openModels.open(vrml.vrml(wrl),
				type='VRML', sameAs=mol,
				identifyAs='%s - Pipes and Planks' % mol.name)
		self.openModels[mol] = mList[0]
		self.openModels[mList[0]] = None

singleton = None

def gui():
	global singleton
	if not singleton:
		singleton = Interface()
	singleton.enter()
