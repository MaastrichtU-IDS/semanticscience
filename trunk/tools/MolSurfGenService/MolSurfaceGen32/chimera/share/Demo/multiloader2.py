#
# Copyright (c) 2004 The Regents of the University of California.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions, and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions, and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#   3. Redistributions must acknowledge that this software was
#      originally developed by the UCSF Computer Graphics Laboratory
#      under support by the NIH National Center for Research Resources,
#      grant P41-RR01081.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""
A general-purpose converter between XML objects and Python objects.
"""
from string import *
import xml.parsers.expat
from xml.sax.saxutils import escape
from types import ListType

def _ensureList(x):
	"Ensure that objects are loaded into lists."
	if not x:
		return []
	if type(x) != ListType:
		return [x]
	return x

def _indent(level):
	"Returns the indentation for a given depth level."
	return "  " * level

class _TypeInfo:
	"A handy class to store callback information about class types."
	def __init__(self, constructor, super=None):
		if super:
			try:
				sample = constructor(super)
			except:
				sample = constructor()
		else:
			sample = constructor()
		self.name = sample.XMLName()
		self.fieldDict = sample.XMLFields()
		self.attrDict = sample.XMLAttributes()
		self.embedDict = sample.XMLEmbedding()
		self.constructor = constructor
		self.free_float = not self.fieldDict

class Multiloader:
	"""
	Multiloader: The General XML Object Loader & Saver

	  Multiloader provides the code required to load objects from XML
	  data files, and write them back into the data files after you're
	  done processing them. These objects need to have certain callbacks,
	  which multiloader uses to identify them and how they are to be
	  structured inside the XML file.

	Object Format

	  All objects that are read in or out using the Multiloader *must*
	  have the following callback functions present:

	  - 'XMLName()' --
	  Returns the XML name of the object.

	  - 'XMLFields()' --
	  Returns a dictionary mapping data members of the object into
	  their associated XML element names.

	  - 'XMLAttributes()' --
	  Returns a dictionary mapping XML element names into
	  lists of tuples. Each tuple represents an attribute that the
	  related element can be given. Each tuple has as its first
	  element the XML name of the attribute, and as its second
	  element the name of the data member of the object where it
	  can store and look up the attribute data.

	  - 'XMLEmbedding()' --
	  Returns a dictionary mapping XML object names to constructors,
	  for objects that can be embedded within the object.

	  Each class used by Multiloader, including classes embedded
	  inside other classes through 'XMLEmbedding()', must have all four
	  of these callback functions defined. Embedded objects will be
	  passed a reference to their superobject as the 'super' parameter
	  of their constructors; if this fails, they will be constructed
	  using the default constructors. Furthermore, *all objects used
	  by Multiloader must have empty (or keyword only) constructors*.

	Loading

	  Once you have created a Multiloader instance, you must load
	  in the data, using the 'load()' function. Once this has been done,
	  you can retrieve the data either by using 'getObjects()', by using
	  'getLookupTable()', or by doing a search with 'lookup()'.

	  After each object is loaded in, its 'finish()' method will be
	  called, if available. This method should do any type conversions
	  or special gimmicks that need to be done once an object is loaded.
	  For example, numeric data members will probably be loaded in as
	  strings, so this function should convert them back to numbers.

	Saving

	  In addition to reading data in using a Multiloader, you can also
	  write data out. There are two functions that do this: 'save()' and
	  'saveList()'. One takes a structured dictionary as a parameter
	  (just like the one returned by 'getObjects()') and the other takes
	  a list of objects.

	  Remember that all of the objects to be written out must have the
	  four callbacks mentioned above defined. If they don't, Multiloader
	  will have no idea how to convert them to XML.

	Known Issues

	  1 When determining the information about class types using '_TypeInfo',
	  a sample instance of each class is created, which may be undesirable,
	  particularly if the constructor for the class does anything important,
	  or if something is keeping track of all the instances of the class that
	  are constructed.

	  2 Won't write out '<element />' or '<element attr=123 />' for blank
	  elements; instead, does '<element></element>' and '<element attr=123></element>',
	  which is valid XML but doesn't look as cool.
	"""

	#
	# The next three functions implement the callbacks necessary for the
	# XML parser.  "startElement" is called whenever the parser sees the
	# beginning of an element (e.g. <start>),  endElement is called whenever
	# the parser sees the end element (e.g. </start>), and charData is called
	# when the parser sees character data.
	#

	def _startElement(self, name, attrs):
		self._curChar = ""

		# Are we the document element?
		if not self._docElement:
			self._docElement = name
			return

		# Are we at the start of a top object (not a subobject)?
		if name in self._objTypes and not self._curObject:
			# Yes. Construct the object.
			self._curObject = self._objTypes[name].constructor()
			self._objInfo = self._objTypes[name]
		elif self._curObject and name in self._objInfo.embedDict:
			# No. Instead, we are at the start of a subobject.
			# Stack the object and construct the subobject, passing it a reference to super.
			try:
				newObject = self._objInfo.embedDict[name](super=self._curObject)
			except:
				# Whoops! Looks like they don't want a reference to the superobject.
				newObject = self._objInfo.embedDict[name]()
			self._stack.append( (self._curObject, self._objInfo) )
			self._objInfo = _TypeInfo(self._objInfo.embedDict[name], self._curObject)
			self._curObject = newObject

		# Properly store the attributes
		if self._objInfo and name in self._objInfo.attrDict:
			for pair in self._objInfo.attrDict[name]:
				if pair[0] in attrs:
					setattr(self._curObject, pair[1], attrs[pair[0]])

	def _endElement(self, name):
		# Did we just finish reading the document?
		if name == self._docElement:
			# Woohoo! Nothing more to do here.
			return

		# Did we just finish reading an object?
		if name in self._objTypes:
			# Yes, a top level object.
			# Fix up the elements (in terms of being lists or not)
			for key in self._objInfo.fieldDict.keys():
				elem = None
				if hasattr(self._curObject, self._objInfo.fieldDict[key]):
					elem = getattr(self._curObject, self._objInfo.fieldDict[key])
					if not elem:
						elem = ""
					elif type(elem) == ListType and len(elem) == 1:
						elem = elem[0]

				setattr(self._curObject, self._objInfo.fieldDict[key], elem)

			# Finish the top level object, and await another.
			self._objects[name].append(self._curObject)
			if hasattr(self._curObject, "finish"):
				self._curObject.finish()
			if self._lookupField and hasattr(self._curObject, self._lookupField):
				if getattr(self._curObject, self._lookupField) in self._lookup[name]:
					self._lookup[name][getattr(self._curObject, self._lookupField)].append(self._curObject)
				else:
					self._lookup[name][getattr(self._curObject, self._lookupField)] = [self._curObject]
			self._curObject = None
			self._objInfo = None
		elif self._stack and name in self._stack[-1][1].embedDict:
			if self._objInfo.free_float:
				setattr(self._curObject, "_cdata", self._curChar)

			# Yes, a subobject.
			# Fix up the elements (in terms of being lists or not)
			for key in self._objInfo.fieldDict.keys():
				elem = None
				if hasattr(self._curObject, self._objInfo.fieldDict[key]):
					elem = getattr(self._curObject, self._objInfo.fieldDict[key])
					if not elem:
						elem = ""
					elif type(elem) == ListType and len(elem) == 1:
						elem = elem[0]

				setattr(self._curObject, self._objInfo.fieldDict[key], elem)
	
			# Attach this object to its superobject, and return to the superobject.
			object, self._objInfo = self._stack.pop()

			if name not in self._objInfo.fieldDict:
				raise Exception("You forgot to give me an XMLField to store the embedded object in!")

			elem = []
			if not hasattr(object, self._objInfo.fieldDict[name]):
				elem.append(self._curObject)
			elif len(getattr(object, self._objInfo.fieldDict[name])) == 0:
				elem.append(self._curObject)
			else:
				elem = _ensureList(getattr(object, self._objInfo.fieldDict[name]))
				elem.append(self._curObject)
			if hasattr(self._curObject, "finish"):
				self._curObject.finish()

			setattr(object, self._objInfo.fieldDict[name], elem)
			self._curObject = object
		elif not self._curObject:
			# A top level object/element that we don't recognize? Gadzooks!
			# Well, since this isn't a verifying parser, just ignore it.
			pass
		elif not name in self._objInfo.fieldDict:
			# An object with an element that we were never told about? Gadzooks!
			# Well, since this isn't a verifying parser, just ignore it.
			pass
		else:
			# No, just an element.
			elem = []
			if not hasattr(self._curObject, self._objInfo.fieldDict[name]):
				elem.append(self._curChar)
			elif not getattr(self._curObject, self._objInfo.fieldDict[name]):
				elem.append(self._curChar)
			else:
				elem = _ensureList(getattr(self._curObject, self._objInfo.fieldDict[name]))
				elem.append(self._curChar)

			setattr(self._curObject, self._objInfo.fieldDict[name], elem)

	def _charData(self, data):
		self._curChar += data

	def load(self, file, objectConstructors, lookupField=None):
		"""Load the objects from a file.

		This function instructs the Multiloader to load in the objects
		from the specified XML file. This function must be passed the
		filename of the XML data file and a list of constructors for the
		Python objects. It can also be passed a particular field to build
		a search dictionary against. This 'lookupField' should be the name
		of the Python data member, not the XML element name."""
		self._lookupField = lookupField
		self._docElement = ''

		self._objects = {}
		self._lookup = {}
		self._objTypes = {}

		# For each constructor, discover the information
		# about that type of object. (XML structure, etc)
		for constructor in objectConstructors:
			sample = constructor()
			objName = sample.XMLName()

			self._objTypes[objName] = _TypeInfo(constructor)
			self._lookup[objName] = {}
			self._objects[objName] = []

		# Set the current object to be empty
		self._curObject = None
		self._objInfo = None

		# The object stack, for recursion into embedded objects
		self._stack = []

		# Create parser
		self.parser = xml.parsers.expat.ParserCreate()
		# Register callbacks
		self.parser.StartElementHandler = self._startElement
		self.parser.EndElementHandler = self._endElement
		self.parser.CharacterDataHandler = self._charData

		# Parse
		self.parser.ParseFile(open(file))

	def loadString(self, data, objectConstructors, lookupField=None):
		"""Load the objects from an XML data string.

		This function instructs the Multiloader to load in the objects
		from a string storing XML data. Aside from the filename being
		replaced with the data string, the parameters for this function
		are the same as those for the regular 'load()' function."""
		self._lookupField = lookupField
		self._docElement = ''

		self._objects = {}
		self._lookup = {}
		self._objTypes = {}

		# For each constructor, discover the information
		# about that type of object. (XML structure, etc)
		for constructor in objectConstructors:
			sample = constructor()
			objName = sample.XMLName()

			self._objTypes[objName] = _TypeInfo(constructor)
			self._lookup[objName] = {}
			self._objects[objName] = []

		# Set the current object to be empty
		self._curObject = None
		self._objInfo = None

		# The object stack, for recursion into embedded objects
		self._stack = []

		# Create parser
		self.parser = xml.parsers.expat.ParserCreate()
		# Register callbacks
		self.parser.StartElementHandler = self._startElement
		self.parser.EndElementHandler = self._endElement
		self.parser.CharacterDataHandler = self._charData

		# Parse
		self.parser.Parse(data, 1)

	def getLookupTable(self):
		"""Get the table used for searches.

		This function returns the table created for lookups. This table
		is represented as a dictionary indexed by XML object name; each
		XML object name is mapped to another dictionary, which maps the
		element data stored in the object data member 'lookupField' (passed
		to the Multiloader upon loading) to the objects that contains
		that exact element data."""
		return self._lookup

	def lookup(self, fieldEntry, inClass=None):
		"""Search through the loaded Python objects.
		
		This function searches through the loaded objects for entries that
		have a particular entry (fieldEntry) in a particular Python data
		member (the member specified as lookupField to the load function).
		It returns a dictionary indexed by XML object names, each mapping
		to a list of objects which have the data 'fieldEntry' in their
		data member 'lookupField'.

		When specifying 'inClass' to be the name of a particular class, the
		function will merely return a list of objects that have the matching
		entry."""
		try:
			if inClass:
				return self._lookup[inClass][fieldEntry]
			else:
				results = {}
				for inClass in self._lookup:
					if fieldEntry in self._lookup[inClass]:
						results.update({inClass:self._lookup[inClass][fieldEntry]})
				return results
		except:
			return None

	def getObjects(self):
		"""Get the loaded Python objects.

		This function returns a dictionary of lists, indexed by the XML
		name of the objects inside them. Each list contains all of the
		objects of that type that were read in by the Multiloader on the
		top level. Embedded objects are stored properly inside these top
		level objects."""
		return self._objects

	def save(self, filename, dict):
		"""Save a structured dictionary of Python objects into an XML file.

		This function converts a structured dictionary of objects into XML,
		and writes them out to the specified file. The dictionary must be in
		the same format as the one returned by the getObjects() function.
		The objects must have the proper callbacks.

		*Note: This function essentially turns the dictionary into a list and
		calls saveList(), so if you've got a list you should use saveList()
		rather than doing any work to structure it.*
		"""
		objects = []
		for name in dict:
			objects += dict[name]
		self.saveList(filename, objects)

	def saveList(self, filename, objects):
		"""Save a list of Python objects into an XML file.

		This function converts an arbitrary list of objects into XML,
		and writes them out to the specified filename. These objects
		must have the proper callbacks."""
		# Open the file
		outFile = open(filename, "w")

		# Write out the starting tags
		outFile.write('<?xml version="1.0" encoding="utf-8"?>\n')
		outFile.write('<Multiloader>\n')

		# Iterate over the list of objects, recursively outputing each object
		for obj in objects: 
			self._saveObj(outFile, obj, 1)

		# Write out the closing tab
		outFile.write('</Multiloader>\n')

		# Close the file
		outFile.close

	def _saveObj(self, outFile, obj, level):
		# Get all of the lookup fields directly from the object rather
		# than our stored values.  This will be helpful when we recurse to
		# get encapsulated objects.

		# Get the top-level object name
		XMLName = obj.XMLName()

		# Get the XML Structures
		fieldDict = obj.XMLFields()
		attrDict = obj.XMLAttributes()

		# Get any embedded structures
		embedList = obj.XMLEmbedding()

		# Prepare the list of attributes
		attrs = ''
		if XMLName in attrDict:
			for pair in attrDict[XMLName]:
				if hasattr(obj, pair[1]):
					attrs += ' ' + pair[0] + '="' + escape(str(getattr(obj, pair[1]))) + '"'

		# Output the top level tag
		outFile.write (_indent(level)+'<'+XMLName+attrs+'>')

		if not fieldDict and hasattr(obj, "_cdata"):
			line = strip(escape(str(getattr(obj, "_cdata"))))
			line.encode('utf-8', 'replace')
			outFile.write(line)
			outFile.write ('</'+XMLName+'>\n')
			return

		outFile.write('\n')

		# Output all of the fields (recursing when necessary)
		for key in fieldDict.keys():
			if hasattr(obj, fieldDict[key]):
				field = getattr(obj, fieldDict[key])
				if type(field) is type([]):
					for f in field:
						self._saveElem(outFile, level, key, f, embedList, obj, attrDict)
				else:
					self._saveElem(outFile, level, key, field, embedList, obj, attrDict)

		# Close the top level
		outFile.write (_indent(level)+'</'+XMLName+'>\n')

	def _saveElem(self, outFile, level, key, field, embedList, obj, attrDict):
		# is it really an embedded object that needs to be written out in its entirety?
		if key in embedList:
			if field:
				self._saveObj(outFile, field, level+1)
		else:
			attrs = ''
			if key in attrDict:
				for pair in attrDict[key]:
					if hasattr(obj, pair[1]):
						attrs += ' ' + pair[0] + '="' + escape(getattr(obj, pair[1])) + '"'

			if not field:
				field = ''
			field = escape(str(field))

			line = '%s<%s%s>%s</%s>\n' % (_indent(level+1), key, attrs, field, key)
			line.encode('utf-8', 'replace')
			outFile.write (line)
