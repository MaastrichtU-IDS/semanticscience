# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 29582 2009-12-10 22:15:31Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import UserError, replyobj
from prefs import prefs
from SimpleSession import SAVE_SESSION, registerAttribute

def processModBaseID(IDcode):
	"""Locate a database ID code via ModBase, read it, and add it to the list of open models.

	_openModBaseIDModel(IDcode) => [model(s)]

	'explodeNMR' controls whether multi-MODEL files are split into
	multiple Molecules (if False, use coord sets instead)
	"""
	identifyAs = IDcode

	from chimera import replyobj
	statusName = identifyAs or IDcode

	path = fetchModBase(IDcode)

	# Open PDB file as models
	from chimera import PDBio
	import os
	pdbio = PDBio()
	pdbio.explodeNMR = False
	molList = pdbio.readPDBfile(path)
	if not pdbio.ok():
		replyobj.status("\n")
		raise UserError("Error reading PDB file: %s" % pdbio.error())
	for m in molList:
		m.name = identifyAs

	# Post-process models to convert remark records
	# into molecule dictionary attribute
	#from baseDialog import buttonFuncName as makeIdentifier
	for m in molList:
		attr = {}
		remarks = m.pdbHeaders.get("REMARK", [])
		for remark in remarks:
			parts = remark.split(None, 2)
			try:
				info = parts[2]
			except IndexError:
				continue
			try:
				key, value = [ v.strip()
						for v in info.split(':', 1) ]
			except ValueError:
				continue
			try:
				value = int(value)
			except ValueError:
				try:
					value = float(value)
				except ValueError:
					pass
			attr[key] = value
			#setattr(m, "modbase_%s" % makeIdentifier(key), value)
		assignModbaseInfo(m, attr)

	# Register open message
	chimera._openedInfo = "Opened %s\n" % statusName
	ModBaseDialog(IDcode, molList)
	return molList

def fetchModBase(IDcode):
	"""Fetch the output from ModBase and fix it up since the generated file
	(illegally) contains multiple XML tags at the document level"""

	from chimera import fetch
	path = fetch.fetch_local_file('ModBase', IDcode + '.pdb')
	if path:
		return path

	from urllib import FancyURLopener
	class Wget(FancyURLopener):
		version = "Wget/1.10.2"
	f = Wget().open("http://salilab.org/modbase/retrieve/modbase"
				"?databaseID=%s" % IDcode)
	from OpenSave import osTemporaryFile
	filename = osTemporaryFile()
	tf = open(filename, "w")
	tf.write(f.readline())
	tf.write("<document>\n")
	tf.write(f.read())
	tf.write("</document>\n")
	tf.close()
	f.close()

	# Parse the XML file and write out
	# a temporary PDB file
	import xml.sax, xml.sax.handler
	from xml.sax import SAXException
	from xml.sax.handler import ContentHandler
	class Handler(ContentHandler):
		def __init__(self, *args, **kw):
			ContentHandler.__init__(self, *args, **kw)
			self.pdbContent = []
			self.pdbActive = False
		def pdbFile(self):
			return ''.join(self.pdbContent).strip()
		def startElement(self, name, attrs):
			self.pdbActive = (name == "content")
			ContentHandler.startElement(self, name, attrs)
		def endElement(self, name):
			if name == "content":
				self.pdbActive = False
			ContentHandler.endElement(self, name)
		def characters(self, content):
			if self.pdbActive:
				self.pdbContent.append(content)
			ContentHandler.characters(self, content)
	handler = Handler()
	try:
		xml.sax.parse(filename, handler)
	except SAXException:
		raise UserError("No matching ModBase entry found for %s"
					% IDcode)
	content = handler.pdbFile()
	del handler
	if not content:
		raise UserError("No ModBase structure found for %s" % IDcode)
	f = open(filename, "w")
	print >> f, content
	f.close()
	del content

	spath = fetch.save_fetched_file(filename, 'ModBase', IDcode + '.pdb')
	if spath:
		return spath

	return filename

class ModBaseDialog(ModelessDialog):

	buttons = ( "Hide", "Quit" )
	help = "UsersGuide/modbase.html"

	def __init__(self, name, molList, tableData=None):
		self.title = "ModBase: %s" % name
		self.molList = molList
		self.tableData = tableData
		ModelessDialog.__init__(self)
		self.closeHandler = chimera.openModels.addRemoveHandler(
						self._modelClosedCB, None)
		self.selHandler = chimera.triggers.addHandler(
						"selection changed",
						self._selectionChangedCB, None)
		self.sesHandler = chimera.triggers.addHandler(
						SAVE_SESSION,
						self._sessionCB, None)
		chimera.extension.manager.registerInstance(self)

	def fillInUI(self, parent):
		import Tkinter
		top = parent.winfo_toplevel()
		menubar = Tkinter.Menu(top, type="menubar", tearoff=False)
		top.config(menu=menubar)
		self.columnMenu = Tkinter.Menu(menubar)
		menubar.add_cascade(label="Columns", menu=self.columnMenu)

		from chimera.tkgui import aquaMenuBar
		aquaMenuBar(menubar, parent, pack = 'top')

		self._makeActionGroup(parent)

		from CGLtk.Table import SortableTable
		from prefs import colAttr, colOrder, prefs, defaults
		self.modBaseTable = SortableTable(parent, menuInfo=(
							self.columnMenu,
							prefs,
							defaults,
							False ))
		if not self.tableData:
			self._addColumn("Model",
					"lambda m: m.oslIdent()",
					format="%s",
					shown=True)
			for fieldName in colOrder:
				keyName, format = colAttr[fieldName]
				self._addColumn(fieldName,
					"lambda m: m.modbaseInfo['%s']"
						% keyName,
					format=format)
		self.modBaseTable.setData(self.molList)
		chimera.triggers.addHandler("post-frame", self._launchTable,
						None)
		self.modBaseTable.pack(expand=True, fill="both")

	def _makeActionGroup(self, parent):
		from prefs import prefs
		from chimera import chimage
		import Tkinter, Pmw

		d = prefs.get("treatment", {})
		self.treatmentShow = d.get("show", 0)
		selAtoms = d.get("selectAtoms", 0)
		selModels = d.get("selectModels", 0)
		hideOthers = d.get("hideOthers", 1)

		self.rightArrow = chimage.get("rightarrow.png", parent)
		self.downArrow = chimage.get("downarrow.png", parent)

		if self.treatmentShow:
			relief = "groove"
			image = self.downArrow
		else:
			relief = "flat"
			image = self.rightArrow
		self.treatmentGroup = Pmw.Group(parent,
				collapsedsize=0,
				tagindent=0,
				ring_relief=relief,
				tag_pyclass=Tkinter.Button,
				tag_text=" Treatment of Chosen Models",
				tag_relief="flat",
				tag_compound="left",
				tag_image=image,
				tag_command=self._treatmentCB)
		if not self.treatmentShow:
			self.treatmentGroup.collapse()
		self.treatmentGroup.pack(side="top", fill="x", padx=3)
		interior = self.treatmentGroup.interior()
		self.treatmentSelAtom = Tkinter.IntVar(parent)
		self.treatmentSelAtom.set(selAtoms)
		b = Tkinter.Checkbutton(interior,
					text="Select atoms",
					onvalue=1, offvalue=0,
					variable=self.treatmentSelAtom,
					command=self._treatmentChangedCB)
		b.pack(side="left")
		self.treatmentSelModel = Tkinter.IntVar(parent)
		self.treatmentSelModel.set(selModels)
		b = Tkinter.Checkbutton(interior,
					text="Choose in Model Panel",
					onvalue=1, offvalue=0,
					variable=self.treatmentSelModel,
					command=self._treatmentChangedCB)
		b.pack(side="left")
		self.treatmentHideOthers = Tkinter.IntVar(parent)
		self.treatmentHideOthers.set(hideOthers)
		b = Tkinter.Checkbutton(interior,
					text="Hide others",
					onvalue=1, offvalue=0,
					variable=self.treatmentHideOthers,
					command=self._treatmentChangedCB)
		b.pack(side="left")

	def _treatmentCB(self):
		self.treatmentShow = not self.treatmentShow
		if self.treatmentShow:
			self.treatmentGroup.configure(ring_relief="groove",
						tag_image=self.downArrow)
			self.treatmentGroup.expand()
		else:
			self.treatmentGroup.configure(ring_relief="flat",
						tag_image=self.rightArrow)
			self.treatmentGroup.collapse()
		self._savePrefs()

	def _addColumn(self, title, attrFetch, format="%s", shown=None):
		if title in [c.title for c in self.modBaseTable.columns]:
			return
		if title in ["Model Score", "Sequence Identity"]:
			# try to align decimal points
			kw = {'font': 'TkFixedFont'}
		else:
			kw = {}
		c = self.modBaseTable.addColumn(title, attrFetch, format=format,
						display=shown, **kw)
		self.modBaseTable.columnUpdate(c)

	def _launchTable(self, trigger, closure, mols):
		self.modBaseTable.launch(browseCmd=self._selectModelCB,
						restoreInfo=self.tableData)
		return chimera.triggerSet.ONESHOT

	def _modelClosedCB(self, trigger, closure, mols):
		remainder = [ m for m in self.molList if m not in mols ]
		if len(remainder) == 0:
			self.molList = []
			self.exit()
		elif len(remainder) != len(self.molList):
			self.molList = remainder
			self.modBaseTable.setData(self.molList)
			self.modBaseTable.refresh(rebuild=True)

	def _selectionChangedCB(self, trigger, closure, ignore):
		from chimera import selection
		mols = selection.currentMolecules()
		selected = [ m for m in mols if m in self.molList ]
		self.modBaseTable.highlight(selected)

	def _selectModelCB(self, tableSel):
		if self.treatmentSelAtom.get():
			from chimera import selection
			selection.clearCurrent()
			selection.addCurrent(tableSel)
			selection.addImpliedCurrent()
		if self.treatmentSelModel.get():
			from ModelPanel import ModelPanel
			from chimera import dialogs
			d = dialogs.display(ModelPanel.name)
			d.selectionChange(tableSel)
		shown = {}
		if self.treatmentHideOthers.get():
			for m in self.molList:
				key = (m.id, m.subid)
				shown[key] = m in tableSel or not tableSel
		else:
			for m in tableSel:
				key = (m.id, m.subid)
				shown[key] = True
		for m in chimera.openModels.list():
			key = (m.id, m.subid)
			try:
				m.display = shown[key]
			except KeyError:
				pass

	def _treatmentChangedCB(self):
		self._selectModelCB(self.modBaseTable.selected())
		self._savePrefs()

	def _savePrefs(self):
		from prefs import prefs
		prefs["treatment"] = {
			"show": self.treatmentShow,
			"selectAtoms": self.treatmentSelAtom.get(),
			"selectModels": self.treatmentSelModel.get(),
			"hideOthers": self.treatmentHideOthers.get(),
		}
		prefs.save()

	def _sessionCB(self, trigger, myData, sesFile):
		from SimpleSession import sessionID
		data = (1,					# version
			self.title,				# title
			[ sessionID(m) for m in self.molList ],	# molecules
			[ m.modbaseInfo for m in self.molList ],# stats
			self.modBaseTable.getRestoreInfo())	# GUI
		print >> sesFile, """
try:
	from ModBase.gui import sessionRestore
	sessionRestore(%s)
except:
	reportRestoreError("Error restoring ModBase")
""" % repr(data)

	def exit(self):
		if self.molList:
			chimera.openModels.close(self.molList)
		if self.closeHandler:
			chimera.openModels.deleteRemoveHandler(
							self.closeHandler)
			self.closeHandler = None
		if self.selHandler:
			chimera.triggers.deleteHandler("selection changed",
							self.selHandler)
			self.selHandler = None
		if self.sesHandler:
			chimera.triggers.deleteHandler(SAVE_SESSION,
							self.sesHandler)
			self.sesHandler = None
		chimera.extension.manager.deregisterInstance(self)
		self.destroy()

	def emName(self):
		return self.title

	def emRaise(self):
		self.enter()

	def emHide(self):
		self.Close()
	Hide = emHide

	def emQuit(self):
		self.exit()
	Quit = emQuit

def assignModbaseInfo(m, info):
	from prefs import attrMap
	m.modbaseInfo = info
	for k, v in info.iteritems():
		try:
			attrName = attrMap[k]
		except KeyError:
			pass
		else:
			setattr(m, attrName, v)

def sessionRestore(sessionData):
	from SimpleSession import idLookup
	version = sessionData[0]
	if version == 1:
		ignore, name, molIdList, infoList, tableData = sessionData
		molList = [ idLookup(mid) for mid in molIdList ]
		for m, info in zip(molList, infoList):
			assignModbaseInfo(m, info)
	else:
		raise ValueError("unknown ModBase version: %s" % str(version))
	ModBaseDialog(name, molList, tableData=tableData)
