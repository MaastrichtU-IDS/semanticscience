# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: modelInspector.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
import Tkinter
import Pmw
from chimera import replyobj, help, tkoptions
from chimera.baseDialog import ModelessDialog
from base import readableName
from chimera.tkoptions import getOptionsForClass, optionSortFunc, \
							AttributeHeader
from chimera.tkoptions import AtomSurfaceDisplayOption, \
	AtomDisplayOption, AtomDrawModeOption, HalfbondOption, \
	BondDrawModeOption, RibbonDisplayOption, RibbonXSectionOption, \
	RibbonScalingOption, \
	AtomBondColorOption, AtomMoleculeSurfaceColorOption, \
	AtomMoleculeSurfaceOpacityOption, RibbonColorOption

class ModelInspector(ModelessDialog):
	buttons = ['Close',]
	help = "UsersGuide/modelattrib.html"

	def __init__(self, model):
		self.model = model
		self.setInCallback = False
		self.title = "%s attributes (model %s)" % (
				readableName(model), model.oslIdent()[1:])
		self.triggers = [('Model', chimera.triggers.addHandler(
					'Model', self._refreshCB, None))]
		self.refreshFuncs = {}
		self.refreshFuncs['Model'] = []
			
		if isinstance(self.model, chimera.Molecule) \
		and len(self.model.pdbHeaders) > 0:
			self.buttons = self.buttons + ["PDB Headers..."]

		ModelessDialog.__init__(self)
	
	def fillInUI(self, parent):
		self.parent = parent
		self.contents = Tkinter.Frame(parent)
		self._fillInContents()
		self.contents.pack(expand=1, fill='both')

	def destroy(self):
		for trigName, trigHandler in self.triggers:
			chimera.triggers.deleteHandler(trigName, trigHandler)
			
		self._toplevel.destroy()

	def _refreshCB(self, trigName, myData, changes):
		if self.setInCallback:
			self.setInCallback = False
			return
		if self.model.__destroyed__:
			return
		for rf, reason in self.refreshFuncs[trigName]:
			if reason and reason not in changes.reasons:
				continue
			rf(self.model)
	
	def getAttr(self, attr):
		obj = self.model
		while '.' in attr:
			preattr, attr = attr.split('.', 1)
			if obj is None:
				raise AttributeError, "attribute of None"
			obj = getattr(obj, preattr)
		if obj is None:
			raise AttributeError, "attribute of None"
		return getattr(obj, attr)

	def setAttr(self, attr, val):
		self.setInCallback = True
		obj = self.model
		while '.' in attr:
			preattr, attr = attr.split('.', 1)
			obj = getattr(obj, preattr)
		setattr(obj, attr, val)

	def setOptAttr(self, opt):
		self.setInCallback = True
		obj = self.model
		opt.setAttribute(obj, opt.attribute, opt.get())

	def setOptSubattribute(self, items, opt):
		self.setInCallback = True
		set = opt.setAttribute
		attr = opt.attribute
		value = opt.get()
		for i in self.getAttr(items):
			set(i, attr, value)

	def _addModelOpt(self, opt, header, **kw):
		if hasattr(opt, 'callback'):
			cb = opt.callback
		else:
			cb = self.setOptAttr
		value = None
		refresh = hasattr(opt, 'attribute')
		if not refresh:
			if opt.__name__ == 'CoordSetOption':
				value = str(self.model.activeCoordSet.id)
			else:
				value = opt.default
		widget = header.addOption(opt, None, value, cb)
		if hasattr(opt, 'storeAs'):
			setattr(self, opt.storeAs, widget)
		if refresh:
			refreshFunc = lambda m, w=widget: w.display([m])
		elif opt.__name__ == 'CoordSetOption':
			refreshFunc = lambda m, w=widget: \
						w.set(str(m.activeCoordSet.id))
		else:
			return
		refreshFunc(self.model)

		trigName = 'Model'
		if hasattr(opt, 'triggerClass'):
			trigName = opt.triggerClass.__name__
		if trigName not in self.refreshFuncs:
			self.refreshFuncs[trigName] = []
			self.triggers.append((trigName,
					chimera.triggers.addHandler(trigName,
					self._refreshCB, None)))
		reason = None
		if hasattr(opt, 'reason'):
			reason = opt.reason
		self.refreshFuncs[trigName].append((refreshFunc, reason))

	def _addAggregateOpt(self, opt, aggAttr, aggClass, header, **kw):
		widget = header.addOption(opt, None, None,
			lambda o, f=self.setOptSubattribute, a=aggAttr, kw=kw: 
			f(a, o, **kw))
		def refreshFunc(m, w=widget, a=aggAttr):
			try:
				val = self.getAttr(a)
			except AttributeError:
				w.disable()
				return
			w.display(val)
		trigName = aggClass
		if hasattr(opt, 'triggerClass'):
			trigName = opt.triggerClass.__name__
		if trigName not in self.refreshFuncs:
			self.refreshFuncs[trigName] = []
			self.triggers.append((trigName,
					chimera.triggers.addHandler(trigName,
					self._refreshCB, None)))
		self.refreshFuncs[aggClass].append((refreshFunc, None))
		widget.display(self.getAttr(aggAttr))

	def _fillInContents(self):
		contents = "Model is of class %s" \
					% self.model.__class__.__name__
		Tkinter.Label(self.contents, text=contents, justify='center'
					).grid(row=0, column=0, columnspan=2)

		self.contents.rowconfigure(1, minsize="0.1i")

		mainHeader = AttributeHeader(self.contents,
						klass=self.model.__class__)
		mainHeader.grid(row=2, column=0, sticky='ew')
		row = 3

		options = getOptionsForClass(self.model.__class__)
		if isinstance(self.model, chimera.Molecule):
			widget = mainHeader.addWidget(Tkinter.Label,
							justify='center')
			self.refreshFuncs['Model'].append((lambda m, w=widget:
				w.config(text="%d residues, %d atoms, %d bonds"
				% (len(m.residues),len(m.atoms),len(m.bonds))),
				None))
			self.refreshFuncs['Model'][-1][0](self.model)

			def setCS(opt):
				self.setAttr('activeCoordSet',
					self.model.coordSets[int(opt.get())])
			class CoordSetOption(tkoptions.EnumOption):
				name = "current coordinate set"
				values = map(str, self.model.coordSets.keys())
				balloon="Current frame of trajectory"
				callback = setCS
				storeAs = 'csOpt'
			options.append(CoordSetOption)
			options.sort(optionSortFunc)

		for opt in options:
			self._addModelOpt(opt, mainHeader)

		if hasattr(self, 'csOpt') and len(self.model.coordSets) < 2:
			self.csOpt.disable()

		if isinstance(self.model, chimera.Molecule):
			aggOpts = {
				chimera.Atom: ('atoms', [
					AtomDisplayOption,
					AtomDrawModeOption,
					AtomBondColorOption,
					AtomMoleculeSurfaceColorOption,
					AtomMoleculeSurfaceOpacityOption,
				]),
				chimera.Bond: ('bonds', [
					HalfbondOption,
					BondDrawModeOption,
				]),
				chimera.Residue: ('residues', [
					RibbonDisplayOption,
					RibbonScalingOption,
					RibbonXSectionOption,
					RibbonColorOption,
				])
			}
		elif isinstance(self.model, chimera.MSMSModel) \
		and self.model.molecule is not None:
			aggOpts = {
				chimera.Atom: ('molecule.atoms', [
					AtomSurfaceDisplayOption,
					AtomMoleculeSurfaceColorOption,
					AtomMoleculeSurfaceOpacityOption,
				])
			}
		else:
			return

		aggs = aggOpts.keys()
		aggs.sort(lambda a, b:
				cmp(a.__name__.lower(), b.__name__.lower()))
		for agg in aggs:
			self.contents.rowconfigure(row, minsize="0.1i")
			row += 1

			header = AttributeHeader(self.contents, klass=agg,
								composite=True)
			header.grid(row=row, column=0, sticky='ew')
			row += 1

			attr, opts = aggOpts[agg]
			opts.sort(optionSortFunc)
			for opt in opts:
				self._addAggregateOpt(opt, attr, agg.__name__,
									header)

	def Close(self):
		from base import _deleteInspector, _attrInspectors
		ModelessDialog.Close(self)
		_deleteInspector(self.model, _attrInspectors)
	
	def PDBHeaders(self):
		from base import _headers
		from pdbHeadersDialog import PDBHeadersDialog
		if not _headers.has_key(self.model):
			_headers[self.model] = PDBHeadersDialog(self.model)
		_headers[self.model].enter()
