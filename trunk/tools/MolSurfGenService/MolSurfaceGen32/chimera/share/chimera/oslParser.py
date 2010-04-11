#!/usr/local/bin/python
# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: oslParser.py 26655 2009-01-07 22:02:30Z gregc $

import types
import re
import string
import StringIO
import operator
from oslLexer import *

class OSLSyntaxError(SyntaxError):
	pass

# replace expand() with:
#
#	from chimera import selection
#	sel = selection.OSLSelection(str)
#
# and to use it to get atoms (vertices):
#
#	sel.itemize(vertex=1) => { chimera.SelVertex: [...] }
# 	sel.apply(vFunc=func) => None (just explicit atoms in selection)
#	sel.expandApply(chimera.SelVertex, vFunc) => None (all implied atoms)

# Obsolete:
#def expand(s, graphs):
#	"""
#	Expand an object specification string and a graph list into an
#	object selection.  See "applyFunctions" for acceptable graph list
#	constructs
#	"""
#
#	import oslSelection
#	oslSel = oslSelection.oslSelection()
#	applyFunctions(s, graphs, oslSel.addGraph,
#			oslSel.addSubgraph, oslSel.addVertex)
#	return oslSel

def applyFunctions(s, graphs, gFunc, sFunc, vFunc):
	"""
	Base on an object specification string, apply functions to selected
	graphs, subgraphs and vertices in the given graph list.  The graph
	list can either be a simple list, or a dictionary whose values are
	lists of graphs.  Any of the supplied functions may be None.
	"""

	if gFunc:
		gs = 'gFunc'
	else:
		gs = None
	if sFunc:
		ss = 'sFunc'
	else:
		ss = None
	if vFunc:
		vs = 'vFunc'
	else:
		vs = None
	p = Parser(s, gs, ss, vs)
	if not graphs or (not gFunc and not sFunc and not vFunc):
		return	# no graphs to examine
	if isinstance(graphs, dict):
		oslGraphList = reduce(operator.add, graphs.values(), [])
	else:
		oslGraphList = graphs
	matchIndex = 0
	try:
		exec p.code in globals(), locals()
	except:
		from replyobj import message
		message("Generated OSL code string was:\n%s\n" % p.code)
		import sys
		raise OSLSyntaxError("Error in '%s': %s" %
						(s, sys.exc_info()[1]))
KeyEnd = 'end'

# Parser class variables:
#    level	the relationships among graphs, subgraphs and vertices
#		objects with smaller numbers contain objects with bigger
#	 	these are constants, since relationships are fixed
#    symbol	symbol of the iterator for each type of object

# Parser instance variables:
#    input	string to parse
#    error	error encountered parsing input
#    code	code generated from parsing input
#    __indent	the indentation level for each object type
#    __end	index of end of input
#    __start	where to start looking for the next token
#    __f	temporary output stream for generated loop code
#    __p	temporary output stream for generated setup code
#    __cond	temporary output stream for generated conditions
#    __token	current token
#    __key	current key level (graph, subgraph, etc.)

class Parser:
	level = { None:-1, KeyGraph:0, KeySubgraph:1, KeyVertex:2, KeyEnd:3 }
	symbol = { None:'?', KeyGraph:'g', KeySubgraph:'s', KeyVertex:'v' }

	#
	# __init__
	#	initialize a Parser instance by parsing the given
	#	string and generating Python code corresponding to
	#	the object selection language specification
	#	
	def __init__(self, s, gFunc, sFunc, vFunc):
		self.input = s
		self.code = None
		self.error = None
		self.gFunc = gFunc
		self.sFunc = sFunc
		self.vFunc = vFunc
		self.__indent = { None:-1, KeyGraph:0, KeySubgraph:1,
					KeyVertex:2, KeyEnd:3 }
		self.__start = 0
		self.__end = len(self.input)
		self.__p = StringIO.StringIO()
		self.__f = StringIO.StringIO()
		self.__p.write('import chimera\n')
		self.__p.write('from chimera.oslParser import oslTestAttr\n')
		self.__key = None
		self.__nextToken(ModeAbbr)
		self.__specIndex = 0
		self.__abbrIndex = 0
		while self.__token['type'] is TypeKey:
			self.__parseKey()
		if self.__token['type'] is not TypeEnd:
			raise SyntaxError, \
				('extraneous token', ('', 1,
				self.__token['start'], self.input))
		self.__newKey(None)
		self.code = self.__p.getvalue() + self.__f.getvalue()
		del self.__p
		del self.__f

	#
	# __nextToken
	#	Get the next token from input string
	#
	def __nextToken(self, mode):
		self.__token, self.__start = nextToken(self.input, self.__start,
							self.__end, mode)

	#
	# __beginCond
	#	Prepare to create the conditional part of a selection test
	#	We create a StringIO object to store any generated code
	#
	def __beginCond(self):
		self.__cond = StringIO.StringIO()

	#
	# __addCond
	#	Add code for condition of current test
	#
	def __addCond(self, s):
		self.__cond.write(s)

	#
	# __checkPresence
	#	Add code to test for the truth value of an attribute
	#
	def __checkPresence(self, key, attr, present=1):
		if not present:
			self.__cond.write('not ')
		self.__cond.write('(hasattr(%s, %s) and %s.%s)' % 
					(Parser.symbol[key], repr(attr),
					Parser.symbol[key], str(attr)))

	#
	# __checkDefined
	#	Add code to test if an attribute is defined
	#
	def __checkDefined(self, key, attr, present=1):
		if not present:
			self.__cond.write('not ')
		self.__cond.write('(hasattr(%s, %s) and %s.%s is not None)' % 
					(Parser.symbol[key], repr(attr),
					Parser.symbol[key], str(attr)))

	# __checkValue
	#	Add code to test an attribute against a constant
	#
	def __checkValue(self, key, attr, op, s):
		self.__cond.write('oslTestAttr(%s, %s, %s, %s)' % 
					(Parser.symbol[key], repr(attr),
					repr(op), repr(s)))

	#
	# __endCond
	#	If If code was generated for a condition, we insert a test
	#	into the output code
	#
	def __endCond(self):
		cond = self.__cond.getvalue()
		if cond != '':
			self.__insertTest(cond)
		del self.__cond

	#
	# __insertTest
	#	Insert a test into the output code
	#	Since we are inserting an if statement, we adjust the
	#	indentation level of all objects that we contain to match
	#	the indentation level of this test
	#
	def __insertTest(self, cond, commaInfo=None):
		indent = self.__indent[self.__key] + 1
		self.__f.write('%sif %s:\n' % ('\t' * indent, cond))
		cIndent = '\t' * (indent+1)
		if commaInfo:
			pkey, commaAbbr = commaInfo
			self.__f.write('%sfor %scommaIndex, abbrTest in '
				'enumerate(%s):\n' % (cIndent, pkey, commaAbbr))
			self.__f.write('%s\tif %s.oslTestAbbr(abbrTest):\n' %
				(cIndent, pkey))
			self.__f.write('%s\t\tbreak\n' % cIndent)
		if self.__key is KeyGraph:
			self.__indent[KeyGraph] = indent
			self.__indent[KeySubgraph] = indent + 1
			self.__indent[KeyVertex] = indent + 2
			self.__indent[KeyEnd] = indent + 3
		elif self.__key is KeySubgraph:
			self.__indent[KeySubgraph] = indent
			self.__indent[KeyVertex] = indent + 1
			self.__indent[KeyEnd] = indent + 2
		elif self.__key is KeyVertex:
			self.__indent[KeyVertex] = indent
			self.__indent[KeyEnd] = indent + 1

	#
	# __insertAbbrev
	#	Insert a test for an abbreviation into the output code
	#	Note that we call __insertTest to do all the hard work
	#
	def __insertAbbrev(self, key, depth, abbr):
		n = self.__abbrIndex
		self.__p.write('abbr%d = chimera.OSLAbbreviation(%d, %s)\n' %
					(n, depth, repr(abbr)))
		kw = {}
		if ',' in abbr:
			self.__p.write('commaAbbr%d = [' % n)
			for commaAbbr in abbr.split(","):
				self.__p.write('chimera.OSLAbbreviation(%d,'
					' %s), ' % (depth, repr(commaAbbr)))
			self.__p.write(']\n')
			kw['commaInfo'] = (Parser.symbol[key], 'commaAbbr%d'%n)

		self.__insertTest('%s.oslTestAbbr(abbr%d)' %
						(Parser.symbol[key], n), **kw)
		self.__abbrIndex = n + 1

	#
	# __tab
	#	Indent to the proper level
	#
	def __tab(self, key):
		self.__f.write('\t' * self.__indent[self.__key])

	#
	# __newKey
	#	Switch to a new object type (key)
	#	This is the function that inserts all the code between tests
	#	The algorithm is divided into two phases:
	#	     1. If the new key level is higher (more specific) than
	#		the current key level, we descend to that level
	#	     2. If the new key level is equal or lower (same
	#		or less specific) than the current key level, we
	#		invoke the callback and pop up to the new level
	#	     3. Readjust the indentation levels to the new object type
	#	Phase 1 allows us to insert the start of the loop constructs
	#	Phase 2 allows us to terminate the loop and select objects
	#		if appropriate
	#	Phase 3 allows us to move on to the next test in a consistent
	#	state
	#
	def __newKey(self, key):
		if self.level[key] > self.level[self.__key]:
		    while self.__key is not key:
			if self.__key is None:
				self.__key = KeyGraph
				self.__f.write('for %s in oslGraphList:\n'
						% Parser.symbol[KeyGraph])
				self.__f.write('\t%scommaIndex = 0\n'
						% Parser.symbol[KeyGraph])
			elif self.__key is KeyGraph:
				self.__key = KeySubgraph
				self.__tab(self.__key)
				self.__f.write('for %s in '
						'%s.oslChildren():\n'
						% (Parser.symbol[KeySubgraph],
						Parser.symbol[KeyGraph]))
				self.__tab(self.__key)
				self.__f.write('\t%scommaIndex = 0\n'
						% Parser.symbol[KeySubgraph])
				if not self.sFunc and not self.vFunc:
					# ugly, but it works
					self.__tab(self.__key)
					self.__f.write('\tbreak'
					' # no subgraph or vertex functions\n')
			elif self.__key is KeySubgraph:
				self.__key = KeyVertex
				self.__tab(self.__key)
				self.__f.write('for %s in '
						'%s.oslChildren():\n'
						% (Parser.symbol[KeyVertex],
						Parser.symbol[KeySubgraph]))
				self.__tab(self.__key)
				self.__f.write('\t%scommaIndex = 0\n'
						% Parser.symbol[KeyVertex])
		else:
			if self.__key is KeyGraph:
				if self.gFunc:
					self.__tab(self.__key)
					self.__f.write('\t# Use graph\n')
					self.__tab(self.__key)
					self.__f.write('\t%s(%s, %d, '
						'gcommaIndex, matchIndex)\n' %
						(self.gFunc,
						Parser.symbol[KeyGraph],
						self.__specIndex))
					self.__tab(self.__key)
					self.__f.write('\tmatchIndex = '
							'matchIndex + 1\n')
				if self.sFunc or self.vFunc:
					self.__key = KeySubgraph
					self.__setIndent()
					self.__tab(self.__key)
					self.__f.write('for %s in '
							'%s.oslChildren():\n'
							% (Parser.symbol[KeySubgraph],
							Parser.symbol[KeyGraph]))
					self.__tab(self.__key)
					self.__f.write('\t%scommaIndex = 0\n'
							% Parser.symbol[KeySubgraph])
			if self.__key is KeySubgraph:
				if self.sFunc:
					self.__tab(self.__key)
					self.__f.write('\t# Use subgraph\n')
					self.__tab(self.__key)
					self.__f.write('\t%s(%s, %d, '
						'(gcommaIndex, scommaIndex),'
						' matchIndex)\n' % (self.sFunc,
						Parser.symbol[KeySubgraph],
						self.__specIndex))
					self.__tab(self.__key)
					self.__f.write('\tmatchIndex = '
							'matchIndex + 1\n')
				else:
					self.__tab(self.__key)
					self.__f.write('\tpass\n')

				if self.vFunc:
					self.__key = KeyVertex
					self.__setIndent()
					self.__tab(self.__key)
					self.__f.write('for %s in '
							'%s.oslChildren():\n'
							% (Parser.symbol[KeyVertex],
							Parser.symbol[KeySubgraph]))
					self.__tab(self.__key)
					self.__f.write('\t%scommaIndex = 0\n'
							% Parser.symbol[KeyVertex])
			if self.__key is KeyVertex:
				if self.vFunc:
					self.__tab(self.__key)
					self.__f.write('\t# Use vertex\n')
					self.__tab(self.__key)
					self.__f.write('\t%s(%s, %d, '
						'(gcommaIndex, scommaIndex, '
						'vcommaIndex), matchIndex)\n' %
						(self.vFunc,
						Parser.symbol[KeyVertex],
						self.__specIndex))
					self.__tab(self.__key)
					self.__f.write('\tmatchIndex = '
							'matchIndex + 1\n')
				else:
					self.__tab(self.__key)
					self.__f.write('\tpass\n')
			self.__key = key
		self.__setIndent()
		self.__specIndex = self.__specIndex + 1

	#
	# __setIndent
	#	Set the indentation levels according to the key
	#
	def __setIndent(self):
		if self.__key is KeyGraph:
			indent = self.__indent[None]
			self.__indent[KeyGraph] = indent + 1
			self.__indent[KeySubgraph] = indent + 2
			self.__indent[KeyVertex] = indent + 3
			self.__indent[KeyEnd] = indent + 4
		elif self.__key is KeySubgraph:
			indent = self.__indent[KeyGraph]
			self.__indent[KeySubgraph] = indent + 1
			self.__indent[KeyVertex] = indent + 2
			self.__indent[KeyEnd] = indent + 3
		elif self.__key is KeyVertex:
			indent = self.__indent[KeySubgraph]
			self.__indent[KeyVertex] = indent + 1
			self.__indent[KeyEnd] = indent + 2
		elif self.__key is None:
			self.__indent[KeyGraph] = 0
			self.__indent[KeySubgraph] = 1
			self.__indent[KeyVertex] = 2
			self.__indent[KeyEnd] = 3

	#
	# __parseKey
	#	Input consists of a set of selectors that consist of
	#	a predefined key (# for graphs, : for subgraphs and
	#	@ for vertices), an optional abbreviation string and
	#	a qualifier (which starts with a /)
	#	We parse this input use a recursive descent parser that
	#	starts with the first key
	#
	def __parseKey(self):
		key = self.__token['key']
		if key is not KeyGraph \
		and key is not KeySubgraph \
		and key is not KeyVertex:
			raise ValueError, ('unknown key type', self.__token)
		self.__newKey(key)
		level = -1
		while self.__token['type'] is TypeKey \
		and self.__token['key'] is key:
			level = level + 1
			self.__nextToken(ModeAbbr)
		if self.__token['type'] is TypeAbbr:
			self.__insertAbbrev(self.__key, level,
						self.__token['string'])
			self.__nextToken(ModeQual)
		if self.__token['type'] is TypeQual:
			self.__beginCond()
			self.__parseQualifier()
			self.__endCond()

	#
	# __parseQualifier
	#	Parse the qualifier expression
	#
	def __parseQualifier(self):
		if self.__token['type'] is not TypeQual:
			raise RuntimeError, ('unexpected token', self.__token)
		self.__nextToken(ModeQual)
		self.__parseOrList()

	#
	# __parseOrList
	#	The qualifier expression can have "or" and "and" conjunctions
	#	We define "and" as having higher precedence than "or", so
	#	we parse the "or" list higher
	#
	def __parseOrList(self):
		self.__parseAndList()
		while self.__token['type'] is TypeOp \
		and self.__token['operator'] is OpOr:
			self.__addCond(' or ')
			self.__nextToken(ModeQual)
			self.__parseAndList()

	#
	# __parseAndList
	#	Parse the "and" list of qualifier expressions
	#
	def __parseAndList(self):
		self.__parseTest()
		while self.__token['type'] is TypeOp \
		and self.__token['operator'] is OpAnd:
			self.__addCond(' and ')
			self.__nextToken(ModeQual)
			self.__parseTest()

	#
	# __parseTest
	#	Each "and" list consists of a series of actual conditions
	#	A condition may be simply the name of an attribute, which
	#	tests for the presence of the attribute (a preceding
	#	! negates the test)
	#	It may also be a name and a constant, separated by an
	#	operator, which tests the attribute against a fixed value
	#	Finally, a test may be a parenthesized expression as well
	#
	def __parseTest(self):
		if self.__token['type'] is TypeIdent:
			left = self.__token
			self.__nextToken(ModeQual)
			if self.__token['type'] is not TypeOp:
				# Create node
				self.__checkPresence(self.__key, left['string'])
			else:
				op = self.__token['operator']
				if op is OpMatch \
				or op is OpNotMatch \
				or op is OpEQ1 \
				or op is OpEQ2 \
				or op is OpNE \
				or op is OpLT \
				or op is OpLE \
				or op is OpGT \
				or op is OpGE:
					self.__nextToken(ModeValue)
					if self.__token['type'] is not TypeIdent:
						raise SyntaxError, \
							('expected identifier',
							('', 1,
							self.__token['start'],
							self.input))
					# Create node
					self.__checkValue(self.__key,
							left['string'], op,
							self.__token['string'])
					self.__nextToken(ModeQual)
				else:
					# Create node
					self.__checkPresence(self.__key,
							left['string'])
		elif self.__token['type'] is TypeOp:
			if self.__token['operator'] is OpNot:
				self.__nextToken(ModeQual)
				if self.__token['type'] is not TypeIdent:
					raise SyntaxError, \
						('expected identifier',
						('', 1, self.__token['start'],
						self.input))
				# Create node
				self.__checkPresence(self.__key,
						self.__token['string'], 0)
				self.__nextToken(ModeQual)
			elif self.__token['operator'] is OpUndef:
				self.__nextToken(ModeQual)
				if self.__token['type'] is not TypeIdent:
					raise SyntaxError, \
						('expected identifier',
						('', 1, self.__token['start'],
						self.input))
				# Create node
				self.__checkDefined(self.__key,
						self.__token['string'], 0)
				self.__nextToken(ModeQual)
			elif self.__token['operator'] is OpLP:
				self.__addCond('(')
				self.__nextToken(ModeQual)
				self.__parseOrList()
				if self.__token['type'] is not TypeOp \
				or self.__token['operator'] is not OpRP:
					raise SyntaxError, \
						('expected close parenthesis',
						('', 1, self.__token['start'],
						self.input))
				self.__addCond(')')
				self.__nextToken(ModeQual)
			else:
				raise SyntaxError, ('unexpected operator',
						('', 1, self.__token['start'],
						self.input))
		else:
			raise SyntaxError, ('unexpected token',
						('', 1, self.__token['start'],
						self.input))

#
# _typeTestDict is the dictionary holding attribute test functions for
#	a particular type of object (e.g., Integer, Instance, etc.)
# _classTestDict is the dictionary holding attribute test functions
#	for an instance of a particular Python class (note that
#	extension classes have distinct types from a Python class
#	instance and therefore must be registered in _typeTestDict
#
_typeTestDict = {}
_classTestDict = {}
_classAttrTestDict = {}

def registerTest(subject, testFunc):
	if isinstance(subject, type):
		_typeTestDict[subject] = testFunc
	elif isinstance(subject, types.ClassType):
		_classTestDict[subject] = testFunc
	elif isinstance(subject, (tuple, list)):
		# for class attributes that are types (rather than instances)
		# mostly used for enums that have symbolic names
		klass, attrName = subject
		try:
			catDict = _classAttrTestDict[klass]
		except KeyError:
			catDict = {}
			_classAttrTestDict[klass] = catDict
		catDict[attrName] = testFunc
	else:
		raise TypeError, \
			"Cannot register test for non-attr non-class non-type"

#
# oslTestAttr
#	Compares an attribute of this instance with the given value
#	'attrName' is the name of the attribute
#	'op' is the string representation of the comparison operator
#	'value' is the constant (string) value to compare with
#
def oslTestAttr(obj, attrName, op, value):
	try:
		attr = getattr(obj, attrName)
	except:
		return op in (OpNE, OpNotMatch) and 1 or 0
	if callable(attr):
		attr = apply(attr, ())
	try:
		return _typeTestDict[type(attr)](attr, op, value)
	except ValueError:
		# perhaps an enum with a symbolic name...
		try:
			testFunc = _classAttrTestDict[obj.__class__][attrName]
		except KeyError:
			return op in (OpNE, OpNotMatch) and 1 and 0
		return testFunc(obj, op, value)
	except KeyError:
		return op in (OpNE, OpNotMatch) and 1 or 0

#
# Here are the test functions for standard types: string, number and instance
#
def _stringTest(attr, op, value):
	if op in (OpMatch, OpNotMatch):
		m = re.match(value, attr, re.I)
		matched = m is not None and m.end() == len(attr)
		if op == OpNotMatch:
			return not matched
		return matched
	if op in (OpEQ1, OpNE):
		if attr.lower() == value.lower():
			return op == OpEQ1 and 1 or 0
		return op == OpNE and 1 or 0
	d = cmp(attr, value)
	if d < 0:
		if op in (OpNE, OpLE, OpLT):
			return 1
	elif d == 0:
		if op in (OpEQ2, OpGE, OpLE):
			return 1
	else:
		if op in (OpNE, OpGE, OpGT):
			return 1
	return 0
for st in types.StringTypes:
	registerTest(st, _stringTest)

def _numberTest(attr, op, value):
	if op in (OpMatch, OpNotMatch):
		return 0
	value = string.atof(value)
	d = cmp(attr, value)
	if d < 0:
		if op in (OpNE, OpLE, OpLT):
			return 1
	elif d == 0:
		if op in (OpEQ1, OpEQ2, OpGE, OpLE):
			return 1
	else:
		if op in (OpNE, OpGE, OpGT):
			return 1
	return 0
registerTest(int, _numberTest)
registerTest(long, _numberTest)
registerTest(float, _numberTest)
import numpy
for bits in ["16", "32", "64", "128"]:
	for base in ["int", "uint", "float"]:
		try:
			registerTest(getattr(numpy, base + bits), _numberTest)
		except AttributeError:
			pass

def _instanceTest(inst, op, value):
	try:
		return _classTestDict[inst.__class__](inst, op, value)
	except KeyError:
		inst = str(inst)
		d = cmp(inst, value)
		if d < 0:
			if op in (OpNE, OpLE, OpLT):
				return 1
		elif d == 0:
			if op in (OpEQ1, OpEQ2, OpGE, OpLE):
				return 1
		else:
			if op in (OpNE, OpGE, OpGT):
				return 1
		return 0
registerTest(types.InstanceType, _instanceTest)

#
# Test code
#
if __name__ == '__main__':
	def testString(s):
		print 'parsing', repr(s)
		try:
			p = Parser(s, 'graphFunc', 'subgraphFunc', 'vertexFunc')
			print 'Parse code:'
			print
			print p.code
			print compile(p.code, '<OSL Code>', 'exec')
		except SyntaxError, v:
			print 'Parse error:', v
	if 1:
		testString('#0:90.A@CA:91.A@CA:92.A@CA:93.A@CA')
		testString('#1:90.A@CA:91.A@CA:92.A@CA:93.A')
	else:
		testString('#0:12:14')
		testString(':12@ca@cb')
		testString('#/number=0@/name=ca')
		testString('#0:12@ca #1@cb')
	if 0:
		import sys
		while 1:
			print '> ',
			s = sys.stdin.readline()
			if not s:
				break
			testString(s)
