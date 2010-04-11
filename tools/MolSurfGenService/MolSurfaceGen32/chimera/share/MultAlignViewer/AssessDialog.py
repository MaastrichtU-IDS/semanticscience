# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AssessDialog.py 27358 2009-04-21 00:32:47Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera.misc import oslModelCmp
from chimera.colorTable import colors
from chimera import replyobj
import Pmw, Tkinter
from MAViewer import MOD_ASSOC

class AssessDialog(ModelessDialog):
	"""Dialog to allow the user to show regions that are matched
	   closely or that are poorly matched
	"""

	buttons = ("OK", "Close")
	default = "OK"
	help = "ContributedSoftware/multalignviewer/multalignviewer.html" \
							"#assessment"

	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Show Match Quality for %s" % mav.title
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		self.refMenu = Pmw.OptionMenu(parent, command=self._newRefCB,
			labelpos="nw", label_text="Reference structure:")
		self.refMenu.grid(row=0, column=0)
		self.alignList = Pmw.ScrolledListBox(parent, items=[],
					labelpos="nw", listbox_height=6,
					label_text="Structures to evaluate:",
					listbox_exportselection=0,
					listbox_selectmode='extended')
		self.alignList.grid(row=1, column=0, sticky="nsew")
		parent.rowconfigure(1, weight=1)
		parent.columnconfigure(0, weight=1)

		subFrame = Tkinter.Frame(parent)
		subFrame.grid(row=2, column=0)
		from chimera.tkoptions import StringOption
		self.attrNameOption = StringOption(subFrame, 2,
			"Create residue attribute named", "matchDist", None,
			balloon="Create a residue attribute"
			" measuring the CA/C4' distance between\nreference and"
			" evaluated structures.  The attribute will be shown\n"
			"in the select-by-attribute dialog after you hit OK.")

		Tkinter.Label(parent, text="The attribute-selection dialog will"
			" display when OK is chosen").grid(row=3, column=0)
		self.refresh(initial=1)
		self.assocHandlerID = self.mav.triggers.addHandler(MOD_ASSOC,
							self.refresh, None)
	def destroy(self):
		self.mav.triggers.deleteHandler(MOD_ASSOC, self.assocHandlerID)
		self.mav = None
		ModelessDialog.destroy(self)

	def refresh(self, trig1=None, trig2=None, trig3=None, initial=0):
		self.matchMaps = {}
		self.mols = {}
		sortableNames = []
		for aseq in self.mav.seqs:
			if not hasattr(aseq, 'matchMaps'):
				continue
			for mol, matchMap in aseq.matchMaps.items():
				name = "%s (%s), %s" % (mol.name,
					mol.oslIdent(), matchMap['mseq'].name)
				sortableNames.append((mol.oslIdent(), name))
				self.matchMaps[name] = matchMap
				self.mols[name] = mol
		if len(sortableNames) < 2:
			self.mav._disableAssessDialog()
			return

		sortableNames.sort(oslModelCmp)
		self.names = []
		for osl, name in sortableNames:
			self.names.append(name)

		if initial:
			self.refMenu.setitems(self.names)
			self._newRefCB(self.names[0])
		else:
			refsel = self.refMenu.getvalue()
			if refsel in self.names:
				selItem = refsel
			else:
				selItem = self.names[0]
			self.refMenu.setitems(self.names, index=selItem)
			self._newRefCB(selItem)

	def Apply(self):
		from chimera import UserError
		attrName = self.attrNameOption.get()
		from chimera.misc import stringToAttr
		fixedAttrName = stringToAttr(attrName, collapse=False)
		if fixedAttrName != attrName:
			self.enter()
			raise UserError("Attribute name must be composed only"
				" of letters, digits, and underscores and must"
				" not start with a digit.")
		refName = self.refMenu.getvalue()

		sels = self.alignList.getcurselection()
		if len(sels) == 0:
			self.enter()
			raise UserError('Select at least one evaluation '
						'structure to assess')
		refMol = self.mols[refName]
		evalMols = []
		for sel in sels:
			evalMols.append(self.mols[sel])
		self.mav.assessMatch(refMol, evalMols, attrName)
		from chimera import dialogs
		from ShowAttr import ShowAttrDialog
		d = dialogs.display(ShowAttrDialog.name)
		d.configure(models=evalMols, attrsOf="residues",
					attrName=attrName, mode="Select")

	def _newRefCB(self, ref):
		self.alignList.setlist([n for n in self.names if n != ref])
		lb = self.alignList.component("listbox")
		lb.selection_set(0, 'end')
