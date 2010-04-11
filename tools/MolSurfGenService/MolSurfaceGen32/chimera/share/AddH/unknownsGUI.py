# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: unknownsGUI.py 26655 2009-01-07 22:02:30Z gregc $

"""GUI to query user for hydrogen-addition info of non-IDATMed atoms"""

from chimera.baseDialog import ModelessDialog, OK, Cancel
from chimera.idatm import *
from chimera import tkgui, dialogs
import Tkinter
import tkFont
import Pmw
import Tix
import AddH

class addHinfoDialog(ModelessDialog):
	title="Hydrogen Geometry Info"
	buttons=[OK, Cancel]
	name="hydrogen geometry"
	help=("unknownsGUI.html", AddH)

	def fillInUI(self, parent):
		# the topmost text is done last since we make it's width the
		# same as the side-by-side radio selectors

		parent.columnconfigure(0, weight=1)
		parent.columnconfigure(1, weight=1)
		parent.rowconfigure(25, weight=1)

		# put in a horizontal bar for esthetics
		hr = Tkinter.Frame(parent, relief='raised', borderwidth=1,
								height=2)
		hr.grid(row=20, columnspan=2, pady=5, sticky='ew')

		self.unknownsLB = Tix.ScrolledHList(parent, options=
		"hlist.background #000099 hlist.columns 4 hlist.header 1")
		hlist = self.unknownsLB.hlist
		hlist.config(separator='|') # hopefully not found in res names
		hlist.config(browsecmd=self.selectAtomCB)
		hlist.header_create(0, itemtype=Tix.TEXT, text='Residue')
		hlist.header_create(1, itemtype=Tix.TEXT, text='Atom')
		hlist.header_create(2, itemtype=Tix.TEXT, text='#')
		hlist.header_create(3, itemtype=Tix.TEXT, text='Assigned')
		self.unknownsLB.grid(row=25, columnspan=2, sticky='ewns')

		boldfont = hlist.tk.call('tix','option','get','bold_font')
		self._regStyle = Tix.DisplayStyle(Tix.TEXT,
			refwindow=self.unknownsLB, fg='#ffff00',
			selectforeground='#7f7f00', bg='#000099', font=boldfont)
		self._okStyle = Tix.DisplayStyle(Tix.TEXT,
			refwindow=self.unknownsLB, fg='#00ff00',
			selectforeground='#00ff00', bg='#000099', font=boldfont)
		self._emphStyle = Tix.DisplayStyle(Tix.TEXT,
			refwindow=self.unknownsLB, bg='#000099',
		        fg='#ff0000', selectforeground='#ff0000',
			font=boldfont)

		self._geometriesList = Pmw.RadioSelect(parent,
		  buttontype='radiobutton', command=self.selectGeometryCB,
		  labelpos='n', orient='vertical', pady=0,
		  label_text="Substituent\nGeometry")
		self._geometriesList.add("unassigned")
		for geom in geometryName:
			self._geometriesList.add(geom)
		self._geometriesList.grid(row=30, column=0, sticky='n')

		self._substituentsList = Pmw.RadioSelect(parent,
		  buttontype='radiobutton', command=self.selectSubstituentsCB,
		  labelpos='n', orient='vertical', pady=0,
		  label_text="Number of\nSubstituents")
		for subs in range(5):\
			self._substituentsList.add(str(subs))
		self._substituentsList.grid(row=30, column=1, sticky='n')

		tkgui.app.update_idletasks() # so winfo calls work right
		self._intro = Tkinter.Label(parent, justify="left",
		  wraplength=self._geometriesList.winfo_reqwidth()
		  + self._substituentsList.winfo_reqwidth(),
		  font=tkFont.Font(weight="normal", size=10),
		  text="The geometries and expected number of substituents for some atoms in the current models are unknown.  These atoms are listed below.  For each, please indicate the expected geometry and number of substituents.  When done, click 'OK'.")
		self._intro.grid(row=10, columnspan=2, sticky="ew")

		self._noSelection()
		self.buttonWidgets['OK'].config(state="disabled")

	def Cancel(self):
		ModelessDialog.Cancel(self)
		if self.cancelCB:
			self.cancelCB()

	def Apply(self):
		newUnknowns = AddH.gatherUnknowns(self.models,
							prevUnknowns=self.atoms)
		if newUnknowns:
			self.setAtoms(self.atoms + newUnknowns)
			Pmw.MessageDialog(message_text=
				"There are now additional atoms with unknown " +
				"substituents/geometries.\nPlease fill out " +
				"the dialog again.")
			self.buttonWidgets['OK'].config(state="disabled")
			self.enter()
			return
		else:
			# reprocess self.unknownsInfo into the form expected
			# addFunc (i.e. keyed by atom and with geometry names
			# replaced by values)
			unknownsInfo = {}
			for atom in self.atoms:
				g,s = self.unknownsInfo[
					(atom.residue.type, atom.name)][0]
				unknownsInfo[atom] = AddH.IdatmTypeInfo(
						geometryName.index(g), s)
			self.addFunc(self.models, unknownsInfo=unknownsInfo,
						hisScheme=self.hisScheme)
			if self.okCB:
				self.okCB()

	def selectAtomCB(self, index):
		for i in range(self._geometriesList.numbuttons()):
			self._geometriesList.button(i).config(state='normal')
		if self._selectedAtom:
			g,s = self.unknownsInfo[self._selectedAtom][0]
			self._geometriesList.button(g).deselect()
			self._substituentsList.button(s).deselect()
		self._selectedAtom = tuple(index.split('~', 1))
		geometry, substituents = self.unknownsInfo[
							self._selectedAtom][0]
		self._limitSubsToGeom(geometry)
		self._geometriesList.button(geometry).select()
		self._substituentsList.button(substituents).select()

	def selectGeometryCB(self, geom):
		self._limitSubsToGeom(geom)
		self.unknownsInfo[self._selectedAtom][0][0] = geom
		self._updateHListAssignment(self._selectedAtom,
				self.unknownsInfo[self._selectedAtom][0])
		allAssigned = 1
		for geomInfo in self.unknownsInfo.values():
			if geomInfo[0][0] == "unassigned":
				allAssigned = 0
				break
		if allAssigned:
			self.buttonWidgets['OK'].config(state="normal")
		else:
			self.buttonWidgets['OK'].config(state="disabled")

	def selectSubstituentsCB(self, subs):
		self.unknownsInfo[self._selectedAtom][0][1] = int(subs)
		self._updateHListAssignment(self._selectedAtom,
				self.unknownsInfo[self._selectedAtom][0])
	
	def setAtoms(self, atoms):
		self.atoms = atoms
		
		if hasattr(self, 'unknownsInfo'):
			oldUnknowns = self.unknownsInfo
		else:
			oldUnknowns = {}
		self.unknownsInfo = {}
		for atom in atoms:
			key = (atom.residue.type, atom.name)
			if self.unknownsInfo.has_key(key):
				self.unknownsInfo[key][1] = \
						self.unknownsInfo[key][1] + 1
			else:
				# value is [geometry, occurances]
				if oldUnknowns.has_key(key):
					geomInfo = oldUnknowns[key][0]
				else:
					geomInfo = ["unassigned", 0]
				self.unknownsInfo[key] = [geomInfo, 1]

		hlist = self.unknownsLB.hlist
		hlist.delete_all()
		self._noSelection()

		firstKey = None
		for res, atom in self.unknownsInfo.keys():
			hlkey = res + '~' + atom
			if firstKey is None:
				firstKey = hlkey
			hlist.add(hlkey, itemtype=Tix.TEXT, text=res,
							style=self._regStyle)
			hlist.item_create(hlkey, 1, itemtype=Tix.TEXT,
						text=atom, style=self._regStyle)
			typeInfo, occurances = self.unknownsInfo[(res,atom)]
			hlist.item_create(hlkey, 2, itemtype=Tix.TEXT,
				text=str(occurances), style=self._regStyle)
			if oldUnknowns.has_key((res,atom)):
				assign = oldUnknowns[(res,atom)][0]
			else:
				assign = ["unassigned", 0]
			self._updateHListAssignment(hlkey, assign)
		if firstKey:
			hlist.selection_set(firstKey)
			self.selectAtomCB(firstKey)

	def _limitSubsToGeom(self, geom):
		try:
			maxSubstituents = geometryName.index(geom)
		except ValueError:
			# presumably unassigned
			maxSubstituents = -1
		for i in range(self._substituentsList.numbuttons()):
			button = self._substituentsList.button(i)
			if i > maxSubstituents:
				button.config(state='disabled')
			else:
				button.config(state='normal')

	def _noSelection(self):
		self._selectedAtom = None
		for i in range(self._geometriesList.numbuttons()):
			self._geometriesList.button(i).config(state='disabled')
		for i in range(self._substituentsList.numbuttons()):
			self._substituentsList.button(i).config(
							state='disabled')
		self._geometriesList.button("unassigned").select()
		self._substituentsList.button("0").select()

	def _updateHListAssignment(self, key, assignment):
		if not isinstance(key, basestring):
			res, atom = key
			key = res + '~' + atom
		if assignment[0] == "unassigned":
			text = "Unassigned"
			style = self._emphStyle
		else:
			text = "%s/%d" % tuple(assignment)
			style = self._okStyle
		self.unknownsLB.hlist.item_create(key, 3, itemtype=Tix.TEXT,
						  text=text, style=style)

dialogs.register(addHinfoDialog.name, addHinfoDialog)

def initiateAddHyd(models, cancelCB=None, okCB=None, hisScheme=None,
					addFunc=AddH.hbondAddHydrogens):
	"""Request the addition of hydrogens to the given models.

	If all atoms in the models have known hydrogen-adding geometries,
	the hydrogens are added immediately.  Otherwise, a dialog is
	started to request the missing information from the user.  Once
	the user 'Ok's the information-gathering dialog, the hydrogens are
	added.  The dialog can instead be cancelled, in which case no 
	hydrogens are added.

	This function may be called from the user interface or from other
	functions.  If the latter, then typically the cancelCB and okCB
	callback functions are provided so that the calling function can
	ascertain whether hydrogens were in fact added to the models.
	"""
	unks = AddH.gatherUnknowns(models)
	if unks:
		dialogs.display(addHinfoDialog.name)
		dialog = dialogs.find(addHinfoDialog.name)
		dialog.setAtoms(unks)
		dialog.models = models
		dialog.cancelCB = cancelCB
		dialog.okCB = okCB
		dialog.hisScheme = hisScheme
		dialog.addFunc = addFunc
	else:
		addFunc(models, hisScheme=hisScheme)
		if okCB:
			okCB()
