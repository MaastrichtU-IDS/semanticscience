# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""The 'session' package defines class 'Session'.  A 'Session' object
may be used to save the state of an object and its sub-objects (e.g.,
object attributes, sequence elements, dictionary items) to a file
object in XML format.  A 'Session' object may also be used to
reconstruct a previously saved object from a file object.  (Note that
the XML specification requires that there be only one root element
per document, so saving multiple objects to the same file object
may not work properly.)

'Session' does not save a representation of Python objects; it saves
the Python object *types and states*, which may be used to reconstruct
the objects.  Python objects are divided into four groups:

- primitive data type (string, int, float)

	Object type is 'type(obj).__name__'.
	Object state is its value.

- standard container (list, tuple, dictionary)

	Object type is 'type(obj).__name__'.
	Object state is the combined states of its contents.

- class instances

	Object type is '(obj.__class__.__module__, obj.__class__.__name__)'.
	Object state is obtained in the same way as 'pickle'.
	Object reconstruction follows the same procedure as 'pickle'.
	(Details and exceptions described below.)

- type instances

	Object type is 'obj.__getfactory__()'.
	Object state is 'obj.__getstate__()'.
	During object reconstruction, the object type is used to
	locate a callable object which is invoked with the
	object state and is expected to return the reconstructed
	object.
	(Details and exceptions described below.)

The save procedure is divided into the following phases:

	- identify all referenced objects
	- remove referenced objects that cannot be saved
	- construct map of objects to unique identifiers
	- write object types and states into XML to output

The reconstruction procedure is divided into the following phases:

	- read in XML tree
	- convert nodes into objects
	- construct map of unique identifiers to objects
	- convert unique identifiers in objects into references
	- return root object

*Unique Identifiers*

The unique identifiers are to handle object references.  For example,
if an attribute A of object X is object Y, then there are two options:

	- attribute A can be saved as the type and state of object Y, or
	- object Y can be saved separately, tagged with a unique
	identifier, and attribute A is saved as the unique identifier.

The former approach has an important drawback: it cannot handle objects
that are referenced by more than one object.  'Session' uses the latter
approach.  Generating unique identifiers is non-trivial because some
objects may be saved implicitly (e.g., atoms in may be saved as part of
a molecule).  For all saved objects, the unique identifier may
simply be the string 'id(obj)'.  Implicitly saved objects
must also supply their own factory method (function used to create
the objects) and initialization arguments information (see below).

*Class and Type Instances*

While primitive data types and standard containers can be handled
by 'Session' with no help from the objects themselves, class and
type instances are more complex.  Class instances contain enough
information so that 'Session' can save those which do not require
special processing; however, some class instances may need to do
more things when they are restored (e.g., rebuild a graphical user
interface).  'Session' provides several mechanisms to provide
sufficient control to reconstructed instances:

	- Normally, an instance is recreated without calling its
	'__init__' method (by creating an instance of a dummy class
	and then setting its '__class__' attribute to the real
	class).  If an instance has an '__getinitargs__' method,
	then the return value from the method (which must be a tuple)
	is saved as part of the object state and the reconstructed
	instance is created by 'apply'ing the class factory method
	to the '__getinitargs__' tuple.
	- Normally, an the '__dict__' attribute of an instance is
	saved as its state, and the contents of the dictionary is
	used to set attributes of the reconstructed object.  If an
	instance has a '__getstate__' method, then the return value
	from the method is saved as the state instead.  If the
	class has a '__setstate__' method, then it is invoked with
	the saved state to restore the object state.

Type instances contain much less information (accessible via
Python introspection) than class instances:

	- They do not contain information about its factory method
	(the function used to create the instance).
	- They do not necessarily have an '__dict__' attribute, so
	it is difficult to identify which objects they reference
	and to construct object state automatically.
	- They cannot be created without using a factory method.

These differences require that type instances provide additional
methods to supply the necessary information.  In keeping with
the class instance interface style, 'Session' uses '__getstate__',
'__setstate__', and '__getinitargs__' methods for type instances.
In addition, 'Session' uses the '__getfactory__' method to obtain the
factory information and saves it along with the object state.
For completeness, 'Session' checks for the '__getfactory__' method
for class instances as well as type instances.

If an instance does not provide special methods ('__getfactory__',
'__getstate__', '__getinitargs__', '__setstate__'), 'Session' checks
for registered class/type handlers.  These handlers may be registered
using the 'register' method in 'Session' with the appropriate
keyword arguments.

* Identify Objects to Save *

Once the object state has been obtained, either via '__dict__' or
'__getstate__()', it is used to find other referenced objects.
Objects that do not contain sufficient information."""

import exceptions
import types
import xml
from xml.sax import saxexts
from xml.dom.sax_builder import SaxBuilder
from xml.dom.core import createDocument
from xml.dom.writer import XmlWriter

PrimitiveType = [ int, float, long, str ]

class SaveData:
	"SaveData keeps track of data to send to XML output for an object."

	def __init__(self, obj):
		self.children = []
		self.object = obj
		self.initargs = None
		self.state = None
		self.factory = None
		self.refCnt = 1
		self.written = 0

	def addChild(self, child):
		self.children.append(child)

	def incRef(self):
		self.refCnt = self.refCnt + 1

class Reference:
	"Reference instances are placeholders to be fixed later."

	def __init__(self, uniqId):
		self.uniqId = uniqId

class Delay(exceptions.Exception):
	pass
class ReferenceError(exceptions.Exception):
	pass
class ReconstructError(exceptions.Exception):
	pass

class Dummy:
	pass

def importModule(name):
	"""Import module by name and return leaf module.

	Code taken from Python documentation."""

	mod = __import__(name)
	components = name.split('.')
	for comp in components[1:]:
		mod = getattr(mod, comp)
	return mod

class PySession:
	"PySession is used to save and restore session data in XML."

	def __init__(self, appName):
		self._appName = appName
		self._refDict = {
			None.__class__:		self._refPrimitive,
			str:			self._refPrimitive,
			int:			self._refPrimitive,
			long:			self._refPrimitive,
			float:			self._refPrimitive,
			list:			self._refList,
			tuple:			self._refTuple,
			dict:			self._refMap
		}
		self._classDict = {}
		self._typeDict = {}
		self._writeDict = {
			None.__class__:		self._xmlOutNone,
			str:			self._xmlOutString,
			int:			self._xmlOutInt,
			long:			self._xmlOutLong,
			float:			self._xmlOutFloat,
			list:			self._xmlOutList,
			tuple:			self._xmlOutTuple,
			dict:			self._xmlOutDictionary
		}
		self._readDict = {
			'none':		self._xmlInNone,
			'string':	self._xmlInString,
			'int':		self._xmlInInt,
			'long':		self._xmlInLong,
			'float':	self._xmlInFloat,
			'list':		self._xmlInList,
			'tuple':	self._xmlInTuple,
			'dict':		self._xmlInDictionary,
			'reference':	self._xmlInReference,
			'instance':	self._xmlInInstance,
			'typeinst':	self._xmlInTypeinst
		}

	#
	# Only four routines are publicly available:
	#	save, restore, register and deregister
	#

	def save(self, obj, outFile):
		"Save an object, 'obj', to file object 'outFile'."

		# Set up temporaries
		self._setupSave(obj)

		# identify all referenced objects
		self._getReferenced(obj, None)

		# write object types and states into XML to output
		self._writeXML(outFile, obj)

		# Clean up
		badObjects = self._badObjects
		self._cleanupSave()
		return badObjects

	def restore(self, inFile):
		"Restore an object from file object 'inFile'."

		# Set up temporaries
		self._setupRestore()

		# read in XML tree
		xmlDoc = self._readXML(inFile)

		# convert nodes into objects and construct map
		# of unique identifiers to objects
		root = self._reconstruct(xmlDoc)

		# Clean up
		self._cleanupRestore()

		# return root object
		return root

	def register(self, typeClass, **kw):
		"Register functions for object type 'objType'."

		dict = self._getDict(typeClass)
		try:
			tcDict = dict[typeClass.__name__]
		except KeyError:
			tcDict = {}
			dict[typeClass.__name__] = tcDict
		tcDict.update(kw)

	def deregister(self, typeClass):
		"Deregister functions for object type 'objType'."

		dict = self._getDict(typeClass)
		del dict[typeClass.__name__]

	#
	# Methods used in saving session
	#

	def _setupSave(self, obj):
		"Set up temp variables."

		# _saveDict is a dictionary from uniq id to SaveData instances
		self._saveDict = {}
		# _badObjects is a dictionary from id to unsavable object
		self._badObjects = []

	def _cleanupSave(self):
		"Clean up temp variables to eliminate unnecessary references."

		del self._saveDict
		del self._badObjects

	def _getDict(self, typeClass):
		"Get the registered function dictionary for a type or class."

		if isinstance(typeClass, type):
			return self._typeDict
		elif isinstance(typeClass, types.ClassType):
			return self._classDict
		raise TypeError, 'expected type or class type'

	def _getReferenced(self, obj, owner):
		"Save all referenced objects on save list."

		try:
			so =  self._saveDict[id(obj)]
			so.incRef()
			if owner:
				owner.addChild(obj)
			return
		except KeyError:
			pass
		so = SaveData(obj)
		self._saveDict[id(obj)] = so
		ref = self._refDict.get(type(obj), self._refDefault)
		try:
			ref(so, obj, owner)
		except ReferenceError, o:
			raise
		else:
			if owner:
				owner.addChild(obj)

	def _refPrimitive(self, so, obj, owner):
		"Save primitive object."

		so.state = obj

	def _refTuple(self, so, obj, owner):
		"Save tuple."

		#
		# If a sub-object fails to be referenced properly,
		# we just let the exception through since the tuple
		# cannot be saved properly either.
		#
		so.state = obj
		for o in obj:
			self._getReferenced(o, so)

	def _refList(self, so, obj, owner):
		"Save list."

		#
		# If a sub-object fails to be referenced properly,
		# we just ignore that one and save a shorter list.
		#
		so.state = obj
		for o in obj:
			try:
				self._getReferenced(o, so)
			except ReferenceError:
				pass
				
	def _refMap(self, so, obj, owner):
		"Save mapping object."

		#
		# If an item-object fails to be referenced properly,
		# we just ignore that one and save a shorter map.
		#
		so.state = obj.items()
		for t in so.state:
			self._getReferenced(t, so)

	def _refDefault(self, so, obj, owner):
		"Save a type or class instance."

		#
		# Object is more complex.  Try to locate registered
		# function dictionary (in case we need it later).
		#
		tcDict = {}
		if isinstance(obj, types.InstanceType):
			try:
				dict = self._getDict(obj.__class__)
				tcDict = dict[obj.__class__.__name__]
			except KeyError:
				pass
		elif isinstance(type(obj), type):
			try:
				dict = self._getDict(type(obj))
				tcDict = dict[type(obj).__name__]
			except KeyError:
				pass

		#
		# Grab the state of the object
		#
		state = None
		if hasattr(obj, '__getstate__'):
			state = obj.__getstate__()
		else:
			try:
				state = tcDict['__getstate__'](obj)
			except KeyError:
				if hasattr(obj, '__dict__'):
					state = obj.__dict__
		so.state = state

		#
		# Grab the factory method information
		#
		factory = None
		if hasattr(obj, '__getfactory__'):
			factory = obj.__getfactory__()
		else:
			try:
				factory = tcDict['__getfactory__'](obj)
			except KeyError:
				pass
		so.factory = factory

		#
		# Grab the initargs method
		#
		initargs = None
		if hasattr(obj, '__getinitargs__'):
			initargs = obj.__getinitargs__()
		else:
			try:
				initargs = tcDict['__getinitargs__'](obj)
			except KeyError:
				pass
		so.initargs = initargs

		# Check whether object is savable.  If not, put it
		# in the badObjects dictionary; otherwise, make the
		# state another object we need to save.
		if not isinstance(obj, types.InstanceType) \
		and so.factory is None:
			self._badObjects.append(obj)
			raise ReferenceError, obj
		else:
			try:
				if so.factory:
					self._getReferenced(so.factory, so)
				if so.initargs:
					self._getReferenced(so.initargs, so)
				if so.state:
					self._getReferenced(so.state, so)
			except ReferenceError, o:
				if not hasattr(obj, '__tolerateBadObject__') \
				or not obj.__tolerateBadObject__(o):
					raise ReferenceError, obj

	def _writeXML(self, outFile, obj):
		"Write object types and states into XML to output."

		doc = createDocument()
		root = doc.createElement('pysession', app=self._appName,
						root=str(id(obj)))
		doc.insertBefore(root, None)
		so = self._saveDict[id(obj)]
		so.incRef()
		self._writeSaveData(so, doc, root)
		outFile.write('<?xml version="1.0"?>\n')
		outFile.write('<!DOCTYPE pysession SYSTEM "pysession.dtd">\n\n')
		writer = XmlSessionWriter(outFile)
		writer.write(doc)

	def _writeSaveData(self, so, doc, root):
		"Recursively write saved data object and its children."

		if so.written:
			child = doc.createElement('reference',
							ref=str(id(so.object)))
			root.insertBefore(child, None)
			return
		so.written = 1
		saver = self._writeDict.get(type(so.object),
						self._xmlOutDefault)
		child = saver(doc, so)
		if child:
			if so.refCnt > 1:
				child.setAttribute('id', str(id(so.object)))
			root.insertBefore(child, None)
		#for c in so.children:
		#	self._writeSaveData(self._saveDict[id(c)], doc, root)

	#
	# XML Output Routines
	#
	def _xmlOutNone(self, doc, so):
		return doc.createElement('none')
	def _xmlOutString(self, doc, so):
		node = doc.createElement('string')
		text = doc.createTextNode(so.state)
		node.insertBefore(text, None)
		return node
	def _xmlOutInt(self, doc, so):
		return doc.createElement('int', value=str(so.object))
	def _xmlOutLong(self, doc, so):
		return doc.createElement('long', value='%d' % so.object)
	def _xmlOutFloat(self, doc, so):
		return doc.createElement('float', value=str(so.object))
	def _xmlOutList(self, doc, so):
		node = doc.createElement('list')
		for o in so.object:
			self._writeSaveData(self._saveDict[id(o)], doc, node)
		return node
	def _xmlOutTuple(self, doc, so):
		node = doc.createElement('tuple')
		for o in so.object:
			self._writeSaveData(self._saveDict[id(o)], doc, node)
		return node
	def _xmlOutDictionary(self, doc, so):
		node = doc.createElement('dict')
		for o in so.state:
			self._writeSaveData(self._saveDict[id(o)], doc, node)
		return node
	def _xmlOutDefault(self, doc, so):
		t = type(so.object)
		if t is types.InstanceType:
			c = so.object.__class__
			node = doc.createElement('instance', name=c.__name__,
							module=c.__module__)
		else:
			node = doc.createElement('typeinst', name=t.__name__)
		if so.factory:
			subnode = doc.createElement('instdata', name='factory')
			node.insertBefore(subnode, None)
			self._writeSaveData(self._saveDict[id(so.factory)],
						doc, subnode)
		if so.initargs:
			subnode = doc.createElement('instdata', name='initargs')
			node.insertBefore(subnode, None)
			self._writeSaveData(self._saveDict[id(so.initargs)],
						doc, subnode)
		if so.state:
			subnode = doc.createElement('instdata', name='state')
			node.insertBefore(subnode, None)
			self._writeSaveData(self._saveDict[id(so.state)],
						doc, subnode)
		return node


	#
	# Methods used in restoring session
	#

	def _setupRestore(self):
		"Initialize temporaries used in session restoration."

		self._objDict = {}
		self._nodeList = []

	def _cleanupRestore(self):
		"Remove temporaries used in session restoration."

		del self._objDict
		del self._nodeList

	def _readXML(self, inFile):
		"Read in XML tree from file object."

		p = saxexts.make_parser()
                dh = SaxBuilder()
                p.setDocumentHandler(dh)
                p.parseFile(inFile)
                p.close()
                return dh.document

	def _reconstruct(self, xmlDoc):
		"Convert XML tree nodes into objects and build id map."

		session = xmlDoc.get_documentElement()
		if session.getAttribute('app') != self._appName:
			raise ValueError, \
				'file is not %s session' % self._appName
		for node in session.get_childNodes():
			if node.__class__ is not xml.dom.core.Text:
				self._nodeList.append(node)
		while self._nodeList:
			nList = self._nodeList
			size = len(nList)
			self._nodeList = []
			for node in nList:
				try:
					self._reconstructNode(node)
				except Delay:
					self._nodeList.append(node)
			if len(self._nodeList) == size:
				raise ReconstructError, 'cyclic references'
		return self._objDict[session.getAttribute('root')]

	def _reconstructNode(self, node):
		uniqId = node.getAttribute('id')
		try:
			obj = self._objDict[uniqId]
		except KeyError:
			restorer = self._readDict.get(node.get_name(),
							self._xmlInDefault)
			obj = restorer(node)
			if uniqId:
				self._objDict[uniqId] = obj
		return obj

	#
	# XML Parsing Routines
	#
	def _xmlInNone(self, node):
		return None
	def _xmlInString(self, node):
		nList = node.get_childNodes()
		if len(nList) == 0:
			return ''
		if len(nList) > 1:
			raise SyntaxError, 'string node with too many children'
		text = nList[0]
		if text.__class__ != xml.dom.core.Text:
			raise SyntaxError, 'string node with non-text'
		return text.get_value()
	def _xmlInInt(self, node):
		return int(node.getAttribute('value'))
	def _xmlInLong(self, node):
		return long(node.getAttribute('value'))
	def _xmlInFloat(self, node):
		return float(node.getAttribute('value'))
	def _xmlInList(self, node):
		result = []
		for n in node.get_childNodes():
			if n.__class__ == xml.dom.core.Text:
				continue
			obj = self._reconstructNode(n)
			result.append(obj)
		return result
	def _xmlInTuple(self, node):
		return tuple(self._xmlInList(node))
	def _xmlInDictionary(self, node):
		result = {}
		for n in node.get_childNodes():
			if n.__class__ == xml.dom.core.Text:
				continue
			t = self._reconstructNode(n)
			if not isinstance(t, tuple) or len(t) != 2:
				raise SyntaxError, 'item is not 2-tuple'
			result[t[0]] = t[1]
		return result
	def _xmlInReference(self, node):
		ref = node.getAttribute('ref')
		try:
			return self._objDict[ref]
		except KeyError:
			raise Delay, ref
	def _xmlInInstance(self, node):
		d = self._xmlInInstData(node)
		className = node.getAttribute('name')
		try:
			f = d['factory']
			module = importModule(f[0])
			factory = getattr(module, f[1])
		except KeyError:
			modName = node.getAttribute('module')
			module = importModule(modName)
			klass = getattr(module, className)
			factory = None
		try:
			args = d['initargs']
		except KeyError:
			# No arguments, either call factory method
			# or build a dummy instance and convert into
			# proper class (latter is necessary because
			# class constructor may require arguments)
			if factory is not None:
				obj = apply(factory, ())
			else:
				obj = Dummy()
				obj.__class__ = klass
		else:
			# Got arguments.  Either call factory method
			# or class constructor with arguments
			if factory:
				obj = apply(factory, args)
			else:
				obj = apply(klass, args)
		if d.has_key('state'):
			if hasattr(obj, '__setstate__'):
				obj.__setstate__(d['state'])
			elif self._classDict.has_key(className):
				tcDict = self._classDict[className]
				f = tcDict.get('__setstate__',
						self._setAttributes)
				f(obj, d['state'])
			else:
				self._setAttributes(obj, d['state'])
		if hasattr(obj, '__reconstructed__'):
			obj.__reconstructed__()
		return obj
	def _xmlInTypeinst(self, node):
		d = self._xmlInInstData(node)
		typeName = node.getAttribute('name')
		try:
			f = d['factory']
			module = importModule(f[0])
			factory = getattr(module, f[1])
		except KeyError:
			raise ReconstructError, (node, d)
		try:
			args = d['initargs']
		except KeyError:
			args = ()
		obj = apply(factory, args)
		if d.has_key('state'):
			if hasattr(obj, '__setstate__'):
				obj.__setstate__(d['state'])
			elif self._typeDict.has_key(typeName):
				tcDict = self._typeDict[typeName]
				f = tcDict.get('__setstate__',
						self._setAttributes)
				f(obj, d['state'])
			else:
				self._setAttributes(obj, d['state'])
		if hasattr(obj, '__reconstructed__'):
			obj.__reconstructed__()
		return obj
	def _xmlInInstData(self, node):
		data = node.getElementsByTagName('instdata')
		d = {}
		for f in node.get_childNodes():
			if f.get_name() != 'instdata':
				continue
			n = None
			for t in f.get_childNodes():
				if t.get_name() == 'tuple':
					n = t
					break
			if not n:
				continue
			obj = self._reconstructNode(n)
			d[f.getAttribute('name')] = obj
		return d
	def _xmlInDefault(self, node):
		raise ReconstructError, node.get_name()

	def _setAttributes(self, obj, dict):
		for k, v in dict.items():
			setattr(obj, k, v)


class XmlSessionWriter(XmlWriter):

	TagNewlines = {
		'pysession':	(1, 1, 1, 1),
		'instdata':	(1, 0, 0, 1),
		'reference':	(1, 0, 0, 1),
		'typeinst':	(1, 1, 1, 1),
		'instance':	(1, 1, 1, 1),
		'list':		(1, 1, 1, 1),
		'tuple':	(1, 1, 1, 1),
		'dictionary':	(1, 1, 1, 1),
		'string':	(1, 0, 0, 1),
		'int':		(1, 0, 0, 1),
		'float':	(1, 0, 0, 1)
	}

	def __init__(self, *args, **kw):
		apply(XmlWriter.__init__, (self,) + args, kw)
		self._setNewLines(self.TagNewlines)
