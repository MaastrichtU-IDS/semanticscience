#!/usr/local/bin/python
# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: oslLexer.py 26655 2009-01-07 22:02:30Z gregc $

import string
import re

#
# Lexical analyzer modes (determines whether some special characters are
# treated as qualifier elements or just normal characters)
#
ModeAbbr = 1
ModeQual = 2
ModeValue = 3

#
# Token type
#
TypeKey = 'key'
TypeAbbr = 'abbreviation'
TypeQual = 'qualifier'
TypeIdent = 'identifier'
TypeOp = 'operator'
TypeEnd = 'end of input'

#
# Operator type
#
OpLP = '('
OpRP = ')'
OpLB = '['
OpRB = ']'
OpMatch = '~'
OpNotMatch = '!~'
OpEQ1 = '='  # case independent
OpEQ2 = '==' # case dependent
OpNE = '!='
OpLT = '<'
OpLE = '<='
OpGT = '>'
OpGE = '>='
OpNot = '!'
OpUndef = '^'
OpAnd = 'and'
OpOr = 'or'

#
# Key type
#
KeyGraph = 'graph'
KeySubgraph = 'subgraph'
KeyVertex = 'vertex'
KeyEdge = 'edge'

#
# Various regular expressions for determining end of sequence of characters
#
white = re.compile('[' + string.whitespace + ']')
nonWhite = re.compile('[^' + string.whitespace + ']')
endAbbr = re.compile('[' + string.whitespace + '#:@/]')
endQual = re.compile('[^a-zA-Z0-9_]')
endValue = white

#
# nextToken
#	Skip over whitespace and return a token, which is a dictionary
#	with at least three attributes 'type', 'start' and 'end'.  'start'
#	and 'end' are the indices for the start and end of the token.
#	Depending on the value of 'type', there may be other attributes:
#	  'type' == 'key'
#		'key' is the type of key
#	  'type' == 'abbreviation'
#		'string' is the actual abbreviation string
#	  'type' == 'qualifier'
#		none
#	  'type' == 'identifier'
#		'string is the actual identifier string
#	  'type' == 'operator'
#		'operator' is the operator type
#	  'type' == 'end of input'
#		none
#
def nextToken(s, start, end, mode):
	#
	# Skip over leading whitespace and see if we reached end of input
	#
	m = nonWhite.search(s, start)
	n = m is None and -1 or m.start()
	if n < 0:
		return {'type':TypeEnd, 'start':n, 'end':n}, n

	#
	# Check for key or qualifier symbol
	#
	last = n
	token = {'start':n}
	if s[n] == '#':				# Check for graph key
		token['type'] = TypeKey
		token['key'] = KeyGraph
		last = n + 1
	elif s[n] == ':':			# Check for subgraph key
		token['type'] = TypeKey
		token['key'] = KeySubgraph
		last = n + 1
	elif s[n] == '@':			# Check for vertex key
		token['type'] = TypeKey
		token['key'] = KeyVertex
		last = n + 1
	elif s[n] == '/':			# Check for qualifier
		token['type'] = TypeQual
		last = n + 1
	if last > n:				# Check if any of above found
		token['end'] = last
		return token, last

	#
	# Check for abbreviation, identifier or operators
	#
	if mode == ModeAbbr:
		#
		# In abbreviation mode, we treat the subsequent characters
		# up to a whitespace or key/qualifier symbol as the
		# abbreviation string
		# Quoted strings are handled specially
		#
		if s[n] == '"':
			return lexString(s, n, end, TypeAbbr)
		m = endAbbr.search(s, n + 1)
		last = m is None and -1 or m.start()
		token['type'] = TypeAbbr
		if last < 0:
			token['string'] = s[n:]
		else:
			token['string'] = s[n:last]
	elif mode == ModeQual:			# Qualifer tests mode
		#
		# In qualifier mode, a quoted string is treated as an
		# identifier.  Otherwise, we look for operators first
		# and, if none is found, then assume we got an identifier
		#
		if s[n] == '"':
			return lexString(s, n, end, TypeIdent)
		elif s[n] == '(':
			token['type'] = TypeOp
			token['operator'] = OpLP
			last = n + 1
		elif s[n] == ')':
			token['type'] = TypeOp
			token['operator'] = OpRP
			last = n + 1
		elif s[n] == '[':
			token['type'] = TypeOp
			token['operator'] = OpLB
			last = n + 1
		elif s[n] == ']':
			token['type'] = TypeOp
			token['operator'] = OpRB
			last = n + 1
		elif s[n] == '~':
			token['type'] = TypeOp
			token['operator'] = OpMatch
			last = n + 1
		elif s[n] == '=':
			token['type'] = TypeOp
			if s[n + 1] == '=':
				token['operator'] = OpEQ2
				last = n + 2
			else:
				token['operator'] = OpEQ1
				last = n + 1
		elif s[n] == '!':
			token['type'] = TypeOp
			if s[n + 1] == '=':
				token['operator'] = OpNE
				last = n + 2
			elif s[n + 1] == '~':
				token['operator'] = OpNotMatch
				last = n + 2
			else:
				token['operator'] = OpNot
				last = n + 1
		elif s[n] == '<':
			token['type'] = TypeOp
			if s[n + 1] == '=':
				token['operator'] = OpLE
				last = n + 2
			else:
				token['operator'] = OpLT
				last = n + 1
		elif s[n] == '>':
			token['type'] = TypeOp
			if s[n + 1] == '=':
				token['operator'] = OpGE
				last = n + 2
			else:
				token['operator'] = OpGT
				last = n + 1
		elif s[n] == '^':
			token['type'] = TypeOp
			token['operator'] = OpUndef
			last = n + 1
		else:
			#
			# No operators found.  Must be either an identifier
			# or the conjunctions "and" or "or"
			#
			# _or_ a syntax error
			#
			m = endQual.search(s, n)
			if m and m.start() == n:
				raise SyntaxError, (
				'illegal symbol in identifier', ('', 1, n, s))
			last = m is None and -1 or m.start()
			if last == -1:
				str = s[n:]
			else:
				str = s[n:last]
			if str == 'and':
				token['type'] = TypeOp
				token['operator'] = OpAnd
			elif str == 'or':
				token['type'] = TypeOp
				token['operator'] = OpOr
			else:
				token['type'] = TypeIdent
				token['string'] = str
	elif mode == ModeValue:			# Qualifer value mode
		if s[n] == '"':
			return lexString(s, n, end, TypeIdent)
		m = endValue.search(s, n + 1)
		last = m is None and -1 or m.start()
		if last == -1:
			str = s[n:]
		else:
			str = s[n:last]
		token['type'] = TypeIdent
		token['string'] = str
	else:					# Unknown mode (how?)
		raise ValueError, ('unknown osl lexer mode ', mode)
	if last == -1:
		last = end
	token['end'] = last
	return token, last

#
# lexString
#	Grab a quoted string from the input
#
def lexString(s, start, end, type):
	token = {'type':type, 'start':start}
	last = start + 1
	escape = 0
	while last < end:
		if escape:
			escape = 0
		elif s[last] == '\\':
			escape = 1
		elif s[last] == '"':
			break
		last = last + 1
	if escape or last >= end:
		raise SyntaxError, ('unterminated string', ('', 1, start, s))
	last = last + 1
	str = s[start:last]
	token['string'] = eval(str)
	token['end'] = last
	return token, last

#
# Test code
#
if __name__ == '__main__':
	def testString(s, mode):
		print 'lexing', repr(s)
		start = 0
		end = len(s)
		while start != -1:
			token, start = nextToken(s, start, end, mode)
			print token
	testString('#0@ca #1@cb', ModeAbbr)
	testString('#0@"ca" #1@cb', ModeAbbr)
	testString('#0@"c\\"a" #1@cb', ModeAbbr)
	testString('#/number=0@/name=ca', ModeQual)
