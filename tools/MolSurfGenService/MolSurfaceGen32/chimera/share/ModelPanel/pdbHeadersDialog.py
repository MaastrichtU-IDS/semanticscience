# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: pdbHeadersDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog

class PDBHeadersDialog(ModelessDialog):
	buttons = ('Close',)
	help="UsersGuide/moleculeattrib.html#pdbheaders"

	def __init__(self, model):
		self.title = 'PDB Headers for %s' % model.name
		self.model = model
		from chimera import preferences
		self.prefs = preferences.addCategory("PDB headers dialog",
				preferences.HiddenCategory,
				optDict={"ordering": "Alphabetical"})
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		import Pmw
		self.text = Pmw.ScrolledText(parent,
						text_font=('TkFixedFont', 10))
		self.text.grid(row=0, column=0, sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)
		self.sorting = Pmw.RadioSelect(parent, buttontype='radiobutton',
				hull_borderwidth=2, hull_relief="ridge",
				command=self.sort, labelpos='n',
				label_text="Record Type Order")
		self.sorting.add("Alphabetical")
		self.sorting.add("PDB")
		self.sorting.grid(row=1, column=0)
		self.sorting.invoke(self.prefs["ordering"])
	
	def Close(self):
		from base import _deleteInspector, _headers
		ModelessDialog.Close(self)
		_deleteInspector(self.model, _headers)

	def sort(self, sortType):
		self.prefs['ordering'] = sortType
		pdbHeaders = self.model.pdbHeaders
		hdrIndex = pdbHeaders.keys()
		if sortType == "Alphabetical":
			hdrIndex.sort()
		else:
			ro = chimera.PDBio.getRecordOrder()
			def recordIndex(hdr):
				try:
					return ro.index(hdr)
				except ValueError:
					return len(ro)
			hdrIndex.sort(lambda h1, h2: cmp(recordIndex(h1),
							recordIndex(h2)))
		t = self.text.component('text')
		t.config(state="normal")
		t.delete("0.0", "end")
		for hdrType in hdrIndex:
			for hdrLine in pdbHeaders[hdrType]:
				t.insert('end', hdrLine)
				t.insert('end', '\n')
		t.config(state='disabled')
