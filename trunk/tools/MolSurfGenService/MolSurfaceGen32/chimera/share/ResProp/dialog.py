# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: dialog.py 29372 2009-11-19 01:11:55Z pett $

"""Categorize residues (e.g. aliphatic)"""

import chimera
import Pmw
import Tkinter
from Tkinter import TRUE, TOP, BOTH, X, NORMAL, DISABLED, END, COMMAND, RAISED
import os
from chimera.baseDialog import ModelessDialog

from ResProp import _strSelSide, _strUnselSide, _strSelMain, \
						_strUnselMain, _strOther
_resCats = [_strSelSide, _strUnselSide, _strSelMain, _strUnselMain, _strOther]

from ResProp import schemaMgr 

class ResProp(ModelessDialog):
	"""Class for defining residue categories"""

	buttons = ("Close",)
	title = 'Residue Category Definition'
	help = 'ContributedSoftware/resprop/resprop.html'
	
	def fillInUI(self, parent):
		self.initialized = 0
		self.curSchema = schemaMgr.schemas[0]
		self.schemaPrompt = None

		self.frame = parent
		self.menu = Pmw.OptionMenu(self.frame, command=self.schemaPick,
		  initialitem=0, items=schemaMgr.schemas, labelpos="n")
		self.menu.configure(label_text = "Residue Category")
		self.menu.grid(row=0, column=0)

		if len(schemaMgr.selections.keys()) != len(schemaMgr.schemas):
			raise AssertionError("# of categories != # of selections")
		
		self.checklists = {}
		for schema in schemaMgr.schemas:
			self.addCheckList(schema)
		self.curSchema = schemaMgr.schemas[self.menu.index(Pmw.SELECT)]
		self.checklists[self.curSchema].grid(row=1, column=0)
		
		schemaGroup = Pmw.Group(self.frame, tag_text="Category Editing")
		groupFrame = schemaGroup.component('groupchildsite')
		Tkinter.Button(groupFrame, text="New category...",
			command=lambda s=self: s.promptSchemaName("add")
			).grid(row=0, column=0, sticky='nsew')
		Tkinter.Button(groupFrame, text="Rename...",
			command=lambda s=self: s.promptSchemaName("rename")
			).grid(row=1, column=0, sticky='nsew')
		Tkinter.Button(groupFrame, text="Delete...",
			command=self.deleteSchema
			).grid(row=0, column=1, sticky='nsew')
		Tkinter.Button(groupFrame, text="Revert to defaults",
			command=self.revertToDefaults
			).grid(row=1, column=1, sticky='nsew')

		schemaGroup.grid(row=3, column=0)

		self.initialized = 1

	def addCheckList(self, schema):
		checklistFrame = Tkinter.Frame(self.frame)
		checklist1 = Pmw.RadioSelect(checklistFrame,
		  buttontype='checkbutton', orient='vertical', pady=0,
		  command = lambda x,y,s=self,z=schema: s.click(x,y,z))
		checklist2 = Pmw.RadioSelect(checklistFrame,
		  buttontype='checkbutton', orient='vertical', pady=0,
		  command = lambda x,y,s=self,z=schema: s.click(x,y,z))
		for index in range(len(schemaMgr.residues)):
			if index < len(schemaMgr.residues)/2:
				checklist = checklist1
			else:
				checklist = checklist2
			residue = schemaMgr.residues[index]
			checked = schemaMgr.selections[schema][index]
			b = checklist.add(residue)
			if checked:
				checklist.invoke(
				  checklist.numbuttons()-1)
		checklist1.grid(row=0, column=0)
		checklist2.grid(row=0, column=1)
			
		self.checklists[schema] = checklistFrame

	def click(self, button, mode, schema):
		schemaMgr.selections[schema][
		  schemaMgr.residues.index(button)] = mode
		self.saveSchemas()
	
	def deleteCB(self, button):
		# callback function from delete confirmation dialog
		self._deleteDialog.withdraw()
		if button == 'Cancel':
			return
		schemaMgr.deleteSchema(self.curSchema)

	def deletedSchema(self, schema):
		# called by schema manager after schema deletion
		self.saveSchemas()
		if schema == self.curSchema:
			if schemaMgr.schemas[0] == self.curSchema:
				nextSchema = schemaMgr.schemas[1]
			else:
				nextSchema = schemaMgr.schemas[0]
			self.schemaPick(nextSchema)
		self.menu.setitems(schemaMgr.schemas, index=self.curSchema)
		del self.checklists[schema]

	def deleteSchema(self):
		if len(schemaMgr.schemas) < 2:
			PmwMessageDialog(
				message_text="Cannot delete last category")
			return
		self._deleteDialog = Pmw.MessageDialog(
				message_text="Really delete category %s?"
				% self.curSchema, buttons=('OK','Cancel'),
				command=self.deleteCB)
		self._deleteDialog.show()

	def revertCB(self, button):
		self._revertDialog.withdraw()
		if button == 'Cancel':
			return
		schemaMgr.revertToDefaults()
		self.saveSchemas()

	def revertToDefaults(self):
		if hasattr(self, '_revertDialog'):
			self._revertDialog.show()
			return
		self._revertDialog = Pmw.MessageDialog(buttons=('OK','Cancel'),
				command=self.revertCB, title='Confirm revert',
				message_text='Really revert to default values'
				' for category selections?')
		
	def schemaPick(self, schema):
		self.checklists[self.curSchema].grid_forget()
		self.checklists[schema].grid(row=1, column=0)
		self.curSchema = schema
	
	def promptSchemaName(self, addOrRename):
		self._schemaPromptMode = addOrRename
		if self.schemaPrompt != None:
			self.schemaPrompt.show()
			return

		self.schemaPrompt = Pmw.PromptDialog(buttons=('Cancel', 'OK'),
		  command=self.handleSchemaPrompt, defaultbutton='OK',
		  title='Specify Category Name',
		  entryfield_validate={'validator':'alphanumeric'},
		  entryfield_labelpos='w',
		  label_text='New category name:')
		self.schemaPrompt.show()

	def handleSchemaPrompt(self, button):
		prompt = self.schemaPrompt

		prompt.withdraw()
		if button == 'Cancel':
			return
		
		schemaName = prompt.component('entry').get()
		if schemaName in schemaMgr.schemas:
			Pmw.MessageDialog(message_text=
			  "Category named '%s' already exists!" % (schemaName))
			return

		if self._schemaPromptMode == "add":
			schemaMgr.addSchema(schemaName)
		else:
			# rename
			# since addSchema changes self.curSchema, remember it...
			curSchema = self.curSchema
			schemaMgr.addSchema(schemaName,
					schemaMgr.selections[curSchema],
					schemaMgr.colorSchemes[curSchema])
			schemaMgr.deleteSchema(curSchema)
		self.saveSchemas()

	def newSchema(self, schemaName):
		# call back from schemaMgr when new schema added
		self.menu.setitems(schemaMgr.schemas)
		self.addCheckList(schemaName)
		self.menu.invoke(index=Pmw.END)

	def saveSchemas(self):
		if not self.initialized:
			return

		saveLocs = chimera.pathFinder().pathList("ResProp",
						"schemaData.py", 0, 0, 1)
		for saveLoc in saveLocs:
			if not os.path.exists(saveLoc):
				# try to create
				dirPath, fileName = os.path.split(saveLoc)
				if not os.path.exists(dirPath):
					try:
						os.makedirs(dirPath)
					except:
						Pmw.MessageDialog(
						  title='Save Error',
						  message_text="Cannot create category save directory '%s'" % (dirPath))
						return
			try:
				saveFile = open(saveLoc, 'w')
			except IOError:
				print "Cannot write to %s" % saveLoc
				continue
			saveFile.write("self.schemas = %s\n"
						% repr(schemaMgr.schemas))
			saveFile.write("self.residues = %s\n"
						% repr(schemaMgr.residues))
			saveFile.write("self.selections = %s\n"
						% repr(schemaMgr.selections))
			saveFile.write("self.colorSchemes = {}\n")
			for schema in schemaMgr.schemas:
				saveFile.write("self.colorSchemes['%s'] = %s\n"
					% (schema,
					repr(schemaMgr.colorSchemes[schema])))
			saveFile.close()
			return
		Pmw.MessageDialog(message_text="Cannot save schema data.")

