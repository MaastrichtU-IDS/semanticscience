# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ksdsspDialog.py 26655 2009-01-07 22:02:30Z gregc $

"""dialog for computing secondary structure elemenst of models"""

from chimera import replyobj
from chimera.baseDialog import ModelessDialog

class KsdsspDialog(ModelessDialog):
	oneshot = 1
	default = 'OK'
	buttons = ('OK', 'Apply', 'Save as Defaults', 'Cancel')
	help = "UsersGuide/modelpanel.html#computess"

	def __init__(self, models):
		self.models = models
		if len(models) > 1:
			name = "Multiple Models"
		else:
			name = models[0].name
		self.title = "Compute Secondary Structure for %s" % name
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		import Tkinter, Pmw
		from chimera.initprefs import ksdsspPrefs, KSDSSP_ENERGY, \
				KSDSSP_HELIX_LENGTH, KSDSSP_STRAND_LENGTH

		self.fields= []
		self.energyField = Pmw.EntryField(parent, labelpos='w',
			label_text='H-bond energy cutoff (kcal/mol):',
			validate='real', value=str(ksdsspPrefs[KSDSSP_ENERGY]))
		self.fields.append(self.energyField)

		self.helixField = Pmw.EntryField(parent, labelpos='w',
				label_text='Minimum helix length:',
				validate='numeric',
				value=str(ksdsspPrefs[KSDSSP_HELIX_LENGTH]))
		self.fields.append(self.helixField)

		self.strandField = Pmw.EntryField(parent, labelpos='w',
				label_text='Minimum strand length:',
				validate='numeric',
				value=str(ksdsspPrefs[KSDSSP_STRAND_LENGTH]))
		self.fields.append(self.strandField)

		for i in range(len(self.fields)):
			self.fields[i].grid(row=i, column=0)
		Pmw.alignlabels(self.fields, sticky='e')

	def Apply(self):
		if not self.validate():
			return
		en = float(self.energyField.getvalue())
		hl = int(self.helixField.getvalue())
		sl = int(self.strandField.getvalue())
		from Midas import ksdssp
		ksdssp(self.models, en, hl, sl)

	def SaveasDefaults(self):
		if not self.validate():
			return
		en = float(self.energyField.getvalue())
		hl = int(self.helixField.getvalue())
		sl = int(self.strandField.getvalue())
		from chimera.initprefs import ksdsspPrefs, KSDSSP_ENERGY, \
				KSDSSP_HELIX_LENGTH, KSDSSP_STRAND_LENGTH
		from chimera import preferences
		ksdsspPrefs[KSDSSP_ENERGY] = en
		ksdsspPrefs[KSDSSP_HELIX_LENGTH] = hl
		ksdsspPrefs[KSDSSP_STRAND_LENGTH] = sl

	def validate(self):
		for field in self.fields:
			field.invoke()
			if not field.valid():
				replyobj.error("Invalid value for %s\n" %
					field.cget("label_text"))
				return False
		return True
