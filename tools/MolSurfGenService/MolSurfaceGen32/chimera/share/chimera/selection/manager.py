# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: manager.py 26655 2009-01-07 22:02:30Z gregc $

import string
import sys
import traceback
import chimera
from chimera import selection, triggers, SelVertex, Molecule, replyobj

OSL_START_CHAR = "\t #:@/"


builtin = intern('built-in')
ui = intern('user interface')

class SelectionMgr:
	# main category names
	CHEMISTRY = "Chemistry"
	STRUCTURE = "Structure"
	RESIDUE = "Residue"
	CHAINID = "Chain"

	def __init__(self, **kw):
		# self.selectors is a dictionary whose keys identify the
		# registrant of the selector, and whose values are
		# dictionaries.  The value dictionaries have keys that are
		# strings (names) and whose values are either:
		#  1) a string/int/"string" tuple:
		#    a) either python code or an OSL
		#    b) grouping (if the selectors at that level should be 
		#       sub-sorted)
		#    c) a description of the selector's function (can be None).
		#  2) a dictionary that describes a subcategory in the same
		#    manner as the self.selectors value dictionary
		self.selectors = {}
		self.dictStack = []
		
		# list of callbacks to make when selectors change.
		self.callbacks = []

	def addCategory(self, registrant, path, makeCallbacks=False):
		self.addSelector(registrant, path + [None], None, makeCallbacks)

	def addSelector(self, registrant, path, text, grouping=0,
					description=None, makeCallbacks=False):
		# text is 'None' if called by addCategory()
		try:
			enumDict = self.selectors[registrant]
		except KeyError:
			enumDict = {}
			self.selectors[registrant] = enumDict
			self.dictStack = [registrant] + self.dictStack
		while len(path) > 1:
			category = path[0]
			if enumDict.has_key(category):
				if isinstance(enumDict[category], basestring):
					enumDict[category] = {}
			else:
				enumDict[category] = {}
			enumDict = enumDict[category]
			path = path[1:]
		if text:
			enumDict[path[0]] = (text, grouping, description)

		if makeCallbacks:
			self.makeCallbacks()

	def addCallback(self, cb):
		self.callbacks.append(cb)

	def deleteSelector(self, registrant, selector, prune=False,
							makeCallbacks=False):
		selDict = self.selectors[registrant]
		for component in selector[0:-1]:
			selDict = selDict[component]
		del selDict[selector[-1]]

		if prune:
			# remove empty categories
			dictPath = selector[0:-1]
			while not selDict:
				if not dictPath:
					break
				selDict = self.selectors[registrant]
				for component in dictPath[0:-1]:
					selDict = selDict[component]
				del selDict[dictPath[-1]]
				dictPath = dictPath[0:-1]

		if makeCallbacks:
			for cb in self.callbacks:
				cb()
		
	def doOp(self, op, enum1, enum2, inverse=0):
		# 'workhorse' function for performing a logical operation
		# on two selectors
		#
		# 'op' should be a string (e.g. 'REMOVE') indicating
		# the operation to perform
		if enum1[0] in OSL_START_CHAR and '\n' not in enum1:
			enum1 = self._osl2code(enum1)
		if enum2[0] in OSL_START_CHAR and '\n' not in enum2:
			enum2 = self._osl2code(enum2)
		enum1 = enum1 + """
sels.append(sel)
sel = selection.ItemizedSelection()
""" + enum2
		if not inverse:
			enum1 = enum1 + """
sels[-1].merge(selection.%s, sel)
"""% (op)
		else:
			enum1 = enum1 + """
sel.merge(selection.%s, sels[-1])
sels[-1].merge(selection.REPLACE, sel)
""" % (op)
		enum1 = enum1 + """
sel = sels[-1]
sels = sels[0:-1]
"""
		return enum1

	def integrateSelDict(self, selDict, leadPath=[], makeCallbacks=True):
		# take the kind of dictionary returned by selectorDict()
		# and integrate it into current dictionaries
		for key in selDict.keys():
			registrant, value = selDict[key]
			if isinstance(value, dict):
				self.integrateSelDict(value, leadPath+[key], 0)
			else:
				self.addSelector(registrant, leadPath+[key],
						value[0], grouping=value[1],
						description=value[-1])
		if makeCallbacks:
			self.makeCallbacks()
			

	def registerSelectorBalloons(self, balloon, selectors=None, path=[]):
		"""Register balloon help for selectors

		Register balloon help for a MenuBalloon ('balloon') as per
		the selector information in 'selectors'.  This routine is
		called recursively for submenus.  At the root menu, the
		'path' variable should be '[]'"""

		if selectors is None:
			selectors = self.selectorDict()

		for sel in selectors.keys():
			registrant, selInfo = selectors[sel]
			if isinstance(selInfo, dict):
				self.registerSelectorBalloons(balloon,
							selInfo, path + [sel])
				continue

			help = selInfo[-1]
			if not help:
				continue

			formattedHelp = help[:]
			helpLen = len(help)
			if helpLen >= 30 and '\n' not in help:
				lines = 2
				while helpLen / lines >= 30:
					lines = lines + 1
				for split in range(1, lines):
					start = int(helpLen * split / lines) - 3
					for index in range(start, start + 19):
						if formattedHelp[index] == " ":
							formattedHelp = formattedHelp[:index] + '\n' + formattedHelp[index+1:]
							break
			balloon.bind(path + [sel], formattedHelp)

	def selectorDict(self, dictStack = [], argDictsOnly=0):
		"""Return a dictionary describing the hierarchy of
		   selectors.

		   'dictStack' dictionaries are searched left-to-right.
		   
		   The returned dictionary has keys that are names of selectors
		   or of selector categories and values that are 2-tuples.
		   The first member of the 2-tuple identifies who registered
		   this value, and the second member is a tuple (if this
		   is Python code or an OSL) or a dictionary (if this is
		   a category).  If a dictionary, it is recursively of the
		   form of the parent dictionary.  If a tuple, the first
		   component is the Python code/OSL and the second is an
		   integer to indicate any sub-sorting at this level, and
		   the last is a help description of the selector"""
		if not argDictsOnly:
			dictStack = dictStack + self.dictStack

		dictStack.reverse()
		eDict = {}
		for registrant in dictStack:
			selDict = self.selectors[registrant]
			eDict = self._mkRegDict(registrant, eDict, selDict)
		return eDict
	
	def makeCallbacks(self):
		for cb in self.callbacks:
			cb()

	def _mkRegDict(self, registrant, target, source):
		for key in source.keys():
			svalue = source[key]
			if isinstance(svalue, dict):
				# source is a dictionary
				if target.has_key(key):
					if type(svalue) != type(target[key][1]):
						# target must be tuple;
						# override
						target[key] = (registrant,
						  self._mkRegDict(registrant,
					  	  {}, source[key]))
					else:
						# both target and source are
						# dictionaries, add source to
						# target
						target[key] = (target[key][0],
						  self._mkRegDict(registrant,
						  target[key][1], source[key]))
				else:
					target[key] = (registrant,
					  self._mkRegDict(registrant,
					  {}, source[key]))
			else:
				# if the source is a tuple, override
				# whatever was there before in target
				target[key] = (registrant, svalue)
		return target
	
	def _osl2code(self, code):
		return """\
sel.merge(selection.REPLACE, selection.OSLSelection('%s'))
sel.addImplied(vertices=0)
""" % (string.strip(code))

	def removeCallback(self, cb):
		self.callbacks.remove(cb)

	def selectionFromText(self, enumText, models=None):
		if enumText[0] in OSL_START_CHAR and '\n' not in enumText:
			sel = selection.ItemizedSelection()
			sel.merge(selection.REPLACE,
					selection.OSLSelection(enumText))
			sel.addImplied(vertices=0)
			return sel
		else:
			return CodeItemizedSelection(enumText, models=models)
		
class CodeItemizedSelection(selection.CodeSelection):
	"""similar to selection.CodeSelection

	differences are that the code local variables are:

		sel -- empty ItemizedSelection
		models -- reference to list of all non-hidden models
		molecules -- reference to models (above) that are molecules
	
	and the code is expected to fill in 'sel' with selected items
	"""

	def __init__(self, *args, **kw):
		try:
			self.models = kw["models"]
		except KeyError:
			self.models = None
		else:
			del kw["models"]
		selection.CodeSelection.__init__(self, *args, **kw)

	def apply(self, vFunc = None, eFunc = None):
		sel = selection.ItemizedSelection()
		sels = []  # used as a stack when selections get composited
		funcGlobals = {
			"__doc__": None,
			"__name__": "CodeItemizedSelection",
			"__builtins__": __builtins__
		}
		if self.models is None:
			sm = chimera.openModels.list()
		else:
			sm = self.models
		funcLocals = {
			"models": sm,
			"molecules": filter(lambda m, M=Molecule:
							isinstance(m, M), sm),
			"sel": sel,
			"sels": sels,
			"selection": selection
		}

		try:
			exec self.codeObj in funcGlobals, funcLocals
		except:
			from chimera import replyobj
			replyobj.error(" CodeItemizedSelection failed\n")
			s = apply(traceback.format_exception,
					sys.exc_info())
			replyobj.message(string.join(s, ''))
		sel.apply(vFunc, eFunc)

selMgr = SelectionMgr()

from CGLutil.SortString import SortString

# populate selectors...
try:
	# attempt to get ChemGroup selectors registered
	import ChemGroup
except ImportError:
	pass

try:
	# attempt to get ResProp selectors registered
	import ResProp
except ImportError:
	pass

try:
	# attempt to get idatm selectors registered
	from chimera import idatm
except ImportError:
	pass

try:
	# attempt to get element selectors registered
	import element
except ImportError:
	pass

try:
	# attempt to get secondary structure selectors registered
	import ss
except ImportError:
	pass

try:
	# attempt to get protein/nucleic selectors registered
	import proteinNuc
except ImportError:
	pass

#try:
#	# attempt to get atom/bond draw mode selectors registered
#	import drawmode
#except ImportError:
#	pass

try:
	# attempt to register chain ID selectors
	import chainID
except ImportError:
	pass

try:
	# attempt to register residue name selectors
	import residues
except ImportError:
	pass

try:
	# attempt to get main/side chain selectors registered
	import chain
except ImportError:
	pass

try:
	# attempt to get surface category selectors registered
	import Categorizer
except ImportError:
	pass

# restore saved selectors
saveLoc = chimera.pathFinder().firstExistingFile(
					"selectionGUI", "selectors", 0, 1)
if saveLoc:
	try:
		saveFile = open(saveLoc, 'r')
	except:
		replyobj.error("Cannot read existing selector save file '%s'\n"
								% (saveLoc))
		saveFile = None
	if saveFile:
		selMgr.integrateSelDict(eval(saveFile.read()))
	del saveFile
del saveLoc

