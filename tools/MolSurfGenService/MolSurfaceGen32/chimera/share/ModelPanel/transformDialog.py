# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: transformDialog.py 26655 2009-01-07 22:02:30Z gregc $

"""dialog for transforming models same as another model"""

from chimera.baseDialog import ModelessDialog
from chimera import replyobj

class TransformDialog(ModelessDialog):
	oneshot = 1
	default = 'OK'
	buttons = ('OK', 'Cancel')
	help = "UsersGuide/modelpanel.html#transform"

	def __init__(self, models):
		self.models = models
		if len(models) > 1:
			name = "Multiple Models"
		else:
			name = models[0].name
		self.title = "Set Transformation of %s" % name
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		import Tkinter, Pmw

		Tkinter.Label(parent, justify='left', text=
"""The "transform as" function applies the rotation/translation matrix of a
single reference model to other models (those chosen in the Model Panel
when this dialog was started).  Choose a single reference model in the
Model Panel and click OK to perform the transformation(s).""").grid()

	def Apply(self):
		from ModelPanel import ModelPanel
		from chimera import dialogs
		mp = dialogs.find(ModelPanel.name, create=1)
		sels = mp.selected()
		if len(sels) != 1:
			replyobj.error("Must choose exactly one model"
				" in model panel.\n")
			return
		refXform = sels[0].openState.xform

		for model in self.models:
			model.openState.xform = refXform
