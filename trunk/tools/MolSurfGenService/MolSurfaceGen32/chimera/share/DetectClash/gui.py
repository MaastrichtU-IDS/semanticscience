# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 29458 2009-11-26 01:01:32Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
import Pmw, Tkinter

from prefs import prefs, CLASH_THRESHOLD, CLASH_COLOR, NONCLASH_COLOR, \
		ACTION_ATTR, ACTION_SELECT, ACTION_COLOR, HBOND_ALLOWANCE, \
		ACTION_PSEUDOBONDS, PB_COLOR, PB_WIDTH, BOND_SEPARATION, \
		ACTION_WRITEINFO, IGNORE_INTRA_RES, ACTION_REPLYLOG

class DetectClashDialog(ModelessDialog):
	name = "detect clashes"
	title = "Find Clashes/Contacts"
	provideStatus = True
	statusPosition = "above"
	help = "ContributedSoftware/findclash/findclash.html"

	FREQ_APPLY = "when OK/Apply clicked"
	FREQ_MOTION = "after relative motions (until dialog closed)"
	FREQ_CONTINUOUS = "continuously (until dialog closed)"

	CHECK_SET = "second set of designated atoms"

	def fillInUI(self, parent):
		self._handlers = {}
		desigGroup = Pmw.Group(parent, tag_text="Atoms to Check", hull_padx=2)
		desigGroup.grid(row=0, sticky="ew")
		from chimera.tkgui import windowSystem
		Tkinter.Button(desigGroup.interior(), command=self._desigCB,
				text="Designate").grid(row=0, column=0, sticky='e')
		Tkinter.Label(desigGroup.interior(), text="currently selected"
			" atoms for checking").grid(row=0, column=1, sticky='w')
		self.desigStatus = Tkinter.Label(desigGroup.interior())
		from tkFont import Font
		font = Font(font=self.desigStatus.cget('font'))
		size = int(font.cget('size'))
		if size > 2:
			font.config(size=size-2)
		font.config(weight='normal')
		self.desigStatus.config(font=font)
		from chimera.selection import ItemizedSelection
		self.designated = ItemizedSelection(
					selChangedCB=self._updateDesigStatus)
		self.desigStatus.grid(row=1, column=0, columnspan=2)
		self.designated2 = ItemizedSelection(selChangedCB=self._locButtonCB)
		if windowSystem == 'aqua':
			pady = None
		else:
			pady = 0
		Tkinter.Button(desigGroup.interior(), command=self._desig2CB,
				pady=pady, text="Designate selection as second set"
				).grid(row=3, column=1)
		self.desig2Status = Tkinter.Label(desigGroup.interior())
		if size > 4:
			font2 = Font(font=font)
			font2.config(size=size-4)
		else:
			font2 = font
		self.desig2Status.config(font=font2)
		self.desig2Status.grid(row=4, column=1)
		self.checkLocButtons = Pmw.RadioSelect(desigGroup.interior(),
			pady=0, orient='vertical', buttontype='radiobutton',
			labelpos='w', label_text="Check designated\natoms"
			" against:", command=self._locButtonCB)
		self.checkLocButtons.grid(row=2, column=0, columnspan=2)
		self.checkLocButtons.add("themselves")
		self.checkLocButtons.add("all other atoms")
		self.checkLocButtons.add("other atoms in same model")
		self.checkLocButtons.add(self.CHECK_SET)
		self.checkLocButtons.invoke(1)

		defGroup = Pmw.Group(parent,
			tag_text="Clash/Contact Parameters", hull_padx=2)
		defGroup.grid(row=1, sticky='ew')
		self.clashDef = ClashDef(defGroup.interior(),
					command=self._checkContinuous,
					value=str(prefs[CLASH_THRESHOLD]))
		self.clashDef.grid(row=0, sticky='w')
		self.hbondAllow = HbondAllow(defGroup.interior(),
					command=self._checkContinuous,
					value=str(prefs[HBOND_ALLOWANCE]))
		self.hbondAllow.grid(row=1, sticky='w')
		defaultsFrame = Tkinter.Frame(defGroup.interior())
		defaultsFrame.grid(row=2)
		Tkinter.Label(defaultsFrame, text="Default").grid(
							row=0, column=0)
		Tkinter.Button(defaultsFrame, text="clash", pady=pady,
			command=self._clashDefaultsCB).grid(row=0, column=1)
		Tkinter.Label(defaultsFrame, text="/").grid(row=0, column=2)
		Tkinter.Button(defaultsFrame, text="contact", pady=pady,
			command=self._contactDefaultsCB).grid(row=0, column=3)
		Tkinter.Label(defaultsFrame, text="criteria").grid(
							row=0, column=4)
		bondsFrame = Tkinter.Frame(defGroup.interior())
		bondsFrame.grid(row=3, sticky='w')
		self.bondsApart = Pmw.OptionMenu(bondsFrame, labelpos='w',
			label_text="Ignore contacts of pairs",
			command=self._checkContinuous,
			initialitem=str(prefs[BOND_SEPARATION]),
			items=[str(i+2) for i in range(4)])
		self.bondsApart.grid(row=0, column=0)
		Tkinter.Label(bondsFrame, text="or fewer bonds apart").grid(
							row=0, column=1)
		self.ignoreIntraResVar = Tkinter.IntVar(parent)
		self.ignoreIntraResVar.set(prefs[IGNORE_INTRA_RES])
		Tkinter.Checkbutton(defGroup.interior(), text="Ignore intra-"
			"residue contacts", variable=self.ignoreIntraResVar,
			command=self._checkContinuous
			).grid(row=4)
			
		actionGroup = Pmw.Group(parent, tag_text=
				"Treatment of Clash/Contact Atoms", hull_padx=2)
		actionGroup.grid(row=2, sticky='ew')
		self.actionSelVar = Tkinter.IntVar(parent)
		self.actionSelVar.set(prefs[ACTION_SELECT])
		Tkinter.Checkbutton(actionGroup.interior(), text="Select",
			command=self._checkContinuous,
			variable=self.actionSelVar).grid(row=0, sticky='w')
		self.actionColorVar = Tkinter.IntVar(parent)
		self.actionColorVar.set(prefs[ACTION_COLOR])
		f = Tkinter.Frame(actionGroup.interior())
		f.grid(row=1, sticky='w')
		Tkinter.Checkbutton(f, text="Color",
			command=self._checkContinuous,
			variable=self.actionColorVar).grid(row=0, column=0)
		from CGLtk.color.ColorWell import ColorWell
		self.clashColorWell = ColorWell(f, noneOkay=True,
						callback=self._checkContinuous,
						color=prefs[CLASH_COLOR])
		self.clashColorWell.grid(row=0, column=1)
		Tkinter.Label(f, text=" (and color all other atoms").grid(row=0,
								column=2)
		self.nonclashColorWell = ColorWell(f, noneOkay=True,
						callback=self._checkContinuous,
						color=prefs[NONCLASH_COLOR])
		self.nonclashColorWell.grid(row=0, column=3)
		Tkinter.Label(f, text=")").grid(row=0, column=4)
		self.actionPBVar = Tkinter.IntVar(parent)
		self.actionPBVar.set(prefs[ACTION_PSEUDOBONDS])
		f = Tkinter.Frame(actionGroup.interior())
		f.grid(row=2, sticky='w')
		Tkinter.Checkbutton(f, text="Draw pseudobonds of color",
			command=self._checkContinuous,
			variable=self.actionPBVar).grid(row=0, column=0)
		from CGLtk.color.ColorWell import ColorWell
		self.pbColorWell = ColorWell(f, noneOkay=False,
						callback=self._checkContinuous,
						color=prefs[PB_COLOR])
		self.pbColorWell.grid(row=0, column=1)
		self.pbWidthEntry = Pmw.EntryField(f, labelpos='w',
			label_text=" and width", validate={'validator': 'real',
			'min': 0.01}, entry_width=4, entry_justify="center",
			command=self._checkContinuous,
			value=str(prefs[PB_WIDTH]))
		self.pbWidthEntry.grid(row=0, column=2)
		self.actionAttrVar = Tkinter.IntVar(parent)
		self.actionAttrVar.set(prefs[ACTION_ATTR])
		self.assignAttrButton = Tkinter.Checkbutton(
					actionGroup.interior(),
					text="Assign 'overlap' attribute",
					variable=self.actionAttrVar)
		self.assignAttrButton.grid(row=3, sticky='w')
		self.actionWriteInfoVar = Tkinter.IntVar(parent)
		self.actionWriteInfoVar.set(prefs[ACTION_WRITEINFO])
		self.writeInfoButton = Tkinter.Checkbutton(
			actionGroup.interior(), text="Write information to"
			" file", variable=self.actionWriteInfoVar)
		self.writeInfoButton.grid(row=4, sticky='w')
		self.actionLogInfoVar = Tkinter.IntVar(parent)
		self.actionLogInfoVar.set(prefs[ACTION_REPLYLOG])
		self.logInfoButton = Tkinter.Checkbutton(
			actionGroup.interior(), text="Write information to"
			" reply log", variable=self.actionLogInfoVar)
		self.logInfoButton.grid(row=5, sticky='w')

		freqGroup = Pmw.Group(parent, tag_text="Frequency of Checking",
								hull_padx=2)
		freqGroup.grid(row=3, sticky="ew")
		self.freqButtons = Pmw.RadioSelect(freqGroup.interior(),
			pady=0, orient='vertical', buttontype='radiobutton',
			labelpos='w', label_text= "Check...",
			command=self._freqChangeCB)
		self.freqButtons.grid(sticky='w')
		self.freqButtons.add(self.FREQ_APPLY)
		self.freqButtons.add(self.FREQ_MOTION)
		self.freqButtons.add(self.FREQ_CONTINUOUS)

		self.freqButtons.invoke(0)
		self._updateDesigStatus()

	def OK(self, *args):
		# use main status line if dialog closing
		from chimera.replyobj import status
		self.status = status
		ModelessDialog.OK(self, *args)

	def Apply(self, *args):
		# workaround: remove pseudobonds before recreating colors
		# so C++ layer doesn't end up with pointers to deleted
		# colors in obscure circumstances
		from DetectClash import nukeGroup
		nukeGroup()
		from chimera import UserError
		self.status("")
		checkAtoms = self.designated.atoms()
		if not checkAtoms:
			self.enter()
			raise UserError("No atoms designated for clash detection")
		self.clashDef['command'] = None
		self.clashDef.invoke()
		self.clashDef['command'] = self._checkContinuous
		if not self.clashDef.valid():
			self.enter()
			raise UserError("Invalid clash amount"
					" (in Clash/Contact Parameters)")
		prefs[CLASH_THRESHOLD] = float(self.clashDef.getvalue())
		self.hbondAllow['command'] = None
		self.hbondAllow.invoke()
		self.hbondAllow['command'] = self._checkContinuous
		if not self.hbondAllow.valid():
			self.enter()
			raise UserError("Invalid H-bond overlap amount"
					" (in Clash/Contact Parameters)")
		prefs[HBOND_ALLOWANCE] = float(self.hbondAllow.getvalue())
		prefs[BOND_SEPARATION] = int(self.bondsApart.getvalue())
		prefs[IGNORE_INTRA_RES] = self.ignoreIntraResVar.get()
		checkVal = self.checkLocButtons.getvalue()
		if checkVal == "themselves":
			test = "self"
		elif checkVal == "all other atoms":
			test = "others"
		elif checkVal == "other atoms in same model":
			test = "model"
		else:
			test = self.designated2.atoms()
			if not test:
				self.enter()
				raise UserError("No second-set atoms designated")
		actionAttr = prefs[ACTION_ATTR] = self.actionAttrVar.get()
		actionSelect = prefs[ACTION_SELECT] = self.actionSelVar.get()
		actionColor = prefs[ACTION_COLOR] = self.actionColorVar.get()
		actionPseudobonds = prefs[ACTION_PSEUDOBONDS] = \
							self.actionPBVar.get()
		actionWriteInfo = prefs[ACTION_WRITEINFO] = \
						self.actionWriteInfoVar.get()
		actionLogInfo = prefs[ACTION_REPLYLOG] = \
						self.actionLogInfoVar.get()
		if self.freqButtons.getvalue() != self.FREQ_APPLY:
			actionAttr = actionWriteInfo = actionLogInfo = False
		if not actionAttr and not actionSelect and not actionColor \
		and not actionPseudobonds and not actionWriteInfo \
		and not actionLogInfo:
			self.enter()
			raise UserError("No actions selected for clashes")
		self.status("Checking for clashes")
		clashColor = nonclashColor = None
		if actionColor:
			prefs[CLASH_COLOR] = self.clashColorWell.rgba
			prefs[NONCLASH_COLOR] = self.nonclashColorWell.rgba
			if prefs[CLASH_COLOR] == None:
				clashColor = None
			else:
				clashColor = chimera.MaterialColor(
							*prefs[CLASH_COLOR])
			if prefs[NONCLASH_COLOR] == None:
				nonclashColor = None
			else:
				nonclashColor = chimera.MaterialColor(
							*prefs[NONCLASH_COLOR])
		pbColor = None
		if actionPseudobonds:
			prefs[PB_COLOR] = self.pbColorWell.rgba
			pbColor = chimera.MaterialColor(*prefs[PB_COLOR])
			self.pbWidthEntry['command'] = None
			self.pbWidthEntry.invoke()
			self.pbWidthEntry['command'] = self._checkContinuous
			if not self.pbWidthEntry.valid():
				self.enter()
				raise UserError("Invalid pseudobond width "
					"(in Treatment of Clash/Contact Atoms)")
			prefs[PB_WIDTH] = float(self.pbWidthEntry.getvalue())

		from DetectClash import cmdDetectClash
		if actionWriteInfo:
			saveFile = "-"
		else:
			saveFile = None
		clashes = cmdDetectClash(checkAtoms, test=test,
			overlapCutoff=prefs[CLASH_THRESHOLD],
			hbondAllowance=prefs[HBOND_ALLOWANCE],
			bondSeparation=prefs[BOND_SEPARATION],
			ignoreIntraRes=prefs[IGNORE_INTRA_RES],
			setAttrs=actionAttr,
			selectClashes=actionSelect,
			colorClashes=actionColor,
			clashColor=clashColor, nonclashColor=nonclashColor,
			makePseudobonds=actionPseudobonds,
			pbColor=pbColor, lineWidth=prefs[PB_WIDTH],
			saveFile=saveFile, log=actionLogInfo,
			summary=self.status)
		if actionAttr:
			from ShowAttr import ShowAttrDialog
			from chimera import dialogs
			from DetectClash import attrName
			d = dialogs.display(ShowAttrDialog.name)
			d.configure(attrsOf="atoms", attrName=attrName,
								mode="Render")

	def Close(self):
		ModelessDialog.Close(self)
		if self.freqButtons.getvalue() != self.FREQ_APPLY:
			self.freqButtons.invoke(self.FREQ_APPLY)

	def _checkContinuous(self, *args):
		if self.freqButtons.getvalue() == self.FREQ_CONTINUOUS:
			self.Apply()

	def _clashDefaultsCB(self):
		from prefs import defaults
		self.hbondAllow.setvalue(str(defaults[HBOND_ALLOWANCE]))
		self.clashDef.setvalue(str(defaults[CLASH_THRESHOLD]))
		self._checkContinuous()

	def _clearHandlers(self):
		while self._handlers:
			trigName, handler = self._handlers.popitem()
			chimera.triggers.deleteHandler(trigName, handler)

	def _contactDefaultsCB(self):
		self.hbondAllow.setvalue("0.0")
		self.clashDef.setvalue("-0.4")
		self._checkContinuous()

	def _desigCB(self):
		self.designated.clear()
		self.designated.add(chimera.selection.currentAtoms())
		self._updateDesigStatus()

	def _desig2CB(self):
		self.designated2.clear()
		self.designated2.add(chimera.selection.currentAtoms())
		self._locButtonCB()
		self._updateDesig2Status()

	def _freqChangeCB(self, freqVal):
		self._clearHandlers()
		if freqVal == self.FREQ_APPLY:
			self.assignAttrButton.configure(state='normal')
			self.writeInfoButton.configure(state='normal')
			self.logInfoButton.configure(state='normal')
			return
		self.assignAttrButton.configure(state='disabled')
		self.writeInfoButton.configure(state='disabled')
		self.logInfoButton.configure(state='disabled')
		def modCoordSets(trigName, myData, changes):
			if changes.modified:
				self.Apply()
		self._handlers['CoordSet'] = chimera.triggers.addHandler(
						'CoordSet', modCoordSets, None)
		def justCoordSets(trigName, myData, changes):
			if 'activeCoordSet changed' in changes.reasons:
				self.Apply()
		self._handlers['Molecule'] = chimera.triggers.addHandler(
						'Molecule', justCoordSets, None)
		if freqVal == self.FREQ_MOTION:
			self._handlers[chimera.MOTION_STOP] = chimera.triggers\
					.addHandler(chimera.MOTION_STOP,
					self._motionCB, None)
		elif freqVal == self.FREQ_CONTINUOUS:
			def preCB(trigName, myData, changes):
				if 'transformation change' in changes.reasons:
					self._motionCB()
			self._handlers['OpenState'] = chimera.triggers\
					.addHandler('OpenState', preCB, None)
		self.Apply()

	def _locButtonCB(self, butName=None):
		checkSetBut = self.checkLocButtons.button(self.CHECK_SET)
		if self.checkLocButtons.getvalue() == self.CHECK_SET \
		and not self.designated2.atoms():
			checkSetBut.config(fg="red", activeforeground="red")
		else:
			checkSetBut.config(fg="black", activeforeground="black")
		self._updateDesig2Status()

	def _motionCB(self, *args):
		# if all molecule activities are the same (i.e. no possible
		# relative motion), do nothing
		activity = None
		for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
			if activity is None:
				activity = m.openState.active
			elif activity != m.openState.active:
				self.Apply()
				return

	def _updateDesigStatus(self):
		numAtoms = len(self.designated.atoms())
		if numAtoms:
			statusText = "%d atoms designated" % numAtoms
			color = 'blue'
		else:
			statusText = "No atoms designated"
			color = 'red'
			self.freqButtons.invoke(self.FREQ_APPLY)
		self.desigStatus.config(text=statusText, fg=color)
		self._checkContinuous()

	def _updateDesig2Status(self):
		numAtoms = len(self.designated2.atoms())
		checkSet = self.checkLocButtons.getvalue() == self.CHECK_SET
		color = 'black'
		if numAtoms:
			statusText = "Second set: %d atoms" % numAtoms
		else:
			statusText = "No second set"
			if checkSet:
				color = 'red'
				self.freqButtons.invoke(self.FREQ_APPLY)
		self.desig2Status.config(text=statusText, fg=color)
		if checkSet:
			self._checkContinuous()

class MidEntry(Tkinter.Frame):
	def __init__(self, parent, **kw):
		Tkinter.Frame.__init__(self, parent)
		leftText = kw.pop('left_text')
		rightText = kw.pop('right_text')
		defaults = {
			'labelpos': 'w',
			'label_text': leftText,
			'validate': 'real',
			'entry_width': 5,
			'entry_justify': "center"
		}
		defaults.update(kw)
		self.entry = Pmw.EntryField(self, **defaults)
		self.entry.grid(row=0, column=0, sticky='e')
		for attrName in ["checkentry", "clear", "getvalue", "invoke",
				"setentry", "setvalue", "valid", "__setitem__"]:
			setattr(self, attrName, getattr(self.entry, attrName))
		Tkinter.Label(self, text=rightText).grid(
						row=0, column=1, sticky='w')

class ClashDef(MidEntry):
	def __init__(self, parent, **kw):
		MidEntry.__init__(self, parent, left_text="Find atoms with VDW"
				" overlap >=", right_text="angstroms", **kw)

class HbondAllow(MidEntry):
	def __init__(self, parent, **kw):
		MidEntry.__init__(self, parent, left_text="Subtract",
					right_text="from overlap for"
					" potentially H-bonding pairs", **kw)
from chimera import dialogs
dialogs.register(DetectClashDialog.name, DetectClashDialog)
