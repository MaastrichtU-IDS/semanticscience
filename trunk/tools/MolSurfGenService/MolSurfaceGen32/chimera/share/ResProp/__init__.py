# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26655 2009-01-07 22:02:30Z gregc $

"""Color residues by property (e.g. aliphatic)"""

import chimera
import os
_strSelSide = intern("Chosen side chains")
_strUnselSide = intern("Remaining side chains")
_strSelMain = intern("Chosen main chain")
_strUnselMain = intern("Remaining main chain")
_strOther = intern("Unknown residues")

_oldSelSide = intern("Selected side chains")
_oldUnselSide = intern("Unselected side chains")
_oldSelMain = intern("Selected main chain")
_oldUnselMain = intern("Unselected main chain")
_translationDict = {
	_oldSelSide: _strSelSide,
	_oldUnselSide: _strUnselSide,
	_oldSelMain: _strSelMain,
	_oldUnselMain: _strUnselMain,
}

ui = None
selCategory = 'amino acid category'

def doUI():
	global ui
	if ui == None:
		from dialog import ResProp
		ui = ResProp()
	else:
		ui.enter()

try:
	from chimera.selection.manager import selMgr
except ImportError:
	selMgr = None

class SchemaMgr:
	"""Class for management of residue property schemas"""

	def __init__(self):
		dataFile = chimera.pathFinder().firstExistingFile("ResProp",
							"schemaData.py", 0, 1)
		if not dataFile:
			raise ImportError, "Could not find schema data file"

		execfile(dataFile)
		for name, colorScheme in self.colorSchemes.items():
			if _oldSelMain in colorScheme:
				for old, new in _translationDict.items():
					colorScheme[new] = colorScheme[old]
					del colorScheme[old]
		for schema in self.schemas:
			self.registerSchemaAsSelector(schema)
	
	def addSchema(self, schemaName, selections=None, colorScheme=None):
		self.schemas.append(schemaName)
		if selections:
			self.selections[schemaName] = selections[:]
		else:
			self.selections[schemaName] = [0] * len(
				self.selections[self.selections.keys()[0]])
		if colorScheme:
			self.colorSchemes[schemaName] = colorScheme.copy()
		else:
			self.colorSchemes[schemaName] =  {
				_strSelSide: 'green',
				_strUnselSide: 'yellow',
				_strSelMain: 'white',
				_strUnselMain: 'white',
				_strOther: None
			}
		if ui:
			ui.newSchema(schemaName)
		self.registerSchemaAsSelector(schemaName, makeSelMgrCallbacks=1)
	
	def deleteSchema(self, schemaName):
		self.schemas.remove(schemaName)
		del self.selections[schemaName]
		del self.colorSchemes[schemaName]

		if selMgr:
			selMgr.deleteSelector(self.__class__.__module__,
				[selMgr.RESIDUE, selCategory,
				schemaName.lower()], makeCallbacks=1)

		if ui:
			ui.deletedSchema(schemaName)

	def registerSchemaAsSelector(self, schema, makeSelMgrCallbacks=0):
		if not selMgr:
			return

		selectorText = """
from %s import schemaMgr

osl = ''
for i in range(len(schemaMgr.residues)):
	if schemaMgr.selections['%s'][i]:
		osl = osl + '::' + schemaMgr.residues[i]

oslSel = selection.OSLSelection(osl)
sel.merge(selection.REPLACE, oslSel)

# residue selection should be fast enough that it seems unnecessary to
# worry about restricting the models beforehand by constructing a complicated
# OSL string; instead just intersect with the model restriction afterward...
modelSel = selection.ItemizedSelection()
modelSel.add(molecules)
sel.merge(selection.INTERSECT, modelSel)

sel.addImplied(vertices=0)
""" % (self.__class__.__module__,  schema)

		selMgr.addSelector(self.__class__.__module__,
			[selMgr.RESIDUE, selCategory, schema.lower()],
			selectorText, makeCallbacks=makeSelMgrCallbacks)
		
	def revertToDefaults(self):
		# temporarily protect 'self' from the execfile()
		s = self
		class dummyClass:
			pass
		self = dummyClass()
		dataFile = chimera.pathFinder().firstExistingFile("ResProp",
							"schemaData.py", 0, 0)
		if not dataFile:
			raise ImportError, "Could not find schema data file"
		execfile(dataFile)
		data = self
		self = s
		
		for schema in data.schemas:
			if schema in self.schemas:
				self.deleteSchema(schema)
			self.addSchema(schema, data.selections[schema],
						data.colorSchemes[schema])
	
schemaMgr = SchemaMgr()
