# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: IdentityDialog.py 29150 2009-10-26 23:51:57Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from chimera.Sequence import percentIdentity
from MAViewer import MOD_ALIGN

class IdentityDialog(ModelessDialog):
	"""Compute percent identity for sequence pairs"""

	buttons = ("OK", "Apply", "Close")
	help = "ContributedSoftware/multalignviewer/multalignviewer.html#pid"
	
	ALL = "all sequences"

	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Compute Percent Identities for %s" % (mav.title,)
		ModelessDialog.__init__(self, *args, **kw)
		self.uiMaster().winfo_toplevel().wm_transient(
						mav.uiMaster().winfo_toplevel())

	def fillInUI(self, parent):
		from chimera.tkoptions import EnumOption, SymbolicEnumOption
		class SeqOption(EnumOption):
			values = [s.name for s in self.mav.seqs] + [self.ALL]
		self.seqMenu1 = SeqOption(parent, 0, "Compare",
						self.mav.seqs[0].name, None)
		self.seqMenu2 = SeqOption(parent, 1, "with",
						self.mav.seqs[1].name, None)
		self.handlerID = self.mav.triggers.addHandler(MOD_ALIGN,
						self._rebuildMenus, None)
		class DenomOption(SymbolicEnumOption):
			labels = ["shorter sequence length",
						"longer sequence length",
						"non-gap columns in common"]
			values = ["shorter", "longer", "in common"]
		self.denominator = DenomOption(parent, 2, "divide by",
							"shorter", None)
	def destroy(self):
		self.mav.triggers.deleteHandler(MOD_ALIGN, self.handlerID)
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		val = self.seqMenu1.get()
		if val == self.ALL:
			seqs1 = self.mav.seqs
		else:
			seqs1 = [s for s in self.mav.seqs if s.name == val]
		val = self.seqMenu2.get()
		if val == self.ALL:
			seqs2 = self.mav.seqs
		else:
			seqs2 = [s for s in self.mav.seqs if s.name == val]

		denom = self.denominator.get()
		for s1 in seqs1:
			for s2 in seqs2:
				pi = percentIdentity(s1, s2, denominator=denom)
				self.mav.status("%s vs. %s:\n"
					"   %.2f%% identity\n" % (s1.name,
					s2.name, pi))
				# since once OK is clicked, the mouse may be
				# over a part of the alignment that causes a
				# status message, also send to regular status
				# line
				replyobj.status("%s vs. %s: %.2f%% identity\n"
					% (s1.name, s2.name, pi), log=True)
		if len(seqs1) > 1 or len(seqs2) > 1:
			self.mav.status("Percent identity info in Reply Log")
			from chimera import dialogs, tkgui
			dialogs.display(tkgui._ReplyDialog.name)

	def _rebuildMenus(self, *args):
		newVals = [s.name for s in self.mav.seqs] + [self.ALL]
		for i, menu in enumerate([self.seqMenu1, self.seqMenu2]):
			val = menu.get()
			menu.values = newVals
			menu.remakeMenu()
			if val in newVals:
				menu.set(val)
			else:
				menu.set(newVals[i])
