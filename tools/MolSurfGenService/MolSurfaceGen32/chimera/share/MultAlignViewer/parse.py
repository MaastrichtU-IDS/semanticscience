# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: parse.py 29789 2010-01-14 22:27:12Z pett $

import os
import parsers
from chimera import replyobj, UserError

class WrongFileTypeError(Exception):
	pass

class FormatSyntaxError(Exception):
	def __init__(self, msg):
		self.msg = msg
	
	def __str__(self):
		return self.msg

def makeReadable(seqName):
	"""make sequence name more human-readable"""

	return seqName.strip()

# "generic" file attributes are:
#	accession (for the whole alignment)
#	author
#	comments
#	   [keep in mind that this and other attributes can be multi-line]
#	date
#	description

# "generic" per-sequence attributes are:
#	accession
#	description
#	weight

parseFunc = {}
exts = {}
prefs = {}
for parserFile in os.listdir(parsers.__file__[:-12]):
	if parserFile[:4] != "read" \
	or parserFile[-3:] != ".py":
		continue
	parserType = parserFile[4:-3]
	try:
		exec \
		"from parsers.%s import extensions, prefixes, parse, fileType" \
						% parserFile[:-3]
	except ImportError:
		replyobj.error("Parser for %s multi-sequence file "
			"does not contain file-name extension list, "
			"command-line prefix list, "
			"file type description, and/or parse() "
			"function\n" % parserType)
		continue
	except:
		replyobj.reportException("Error in %s parser"
							% parserType)
		continue
	parseFunc[fileType] = parse
	exts[fileType] = extensions
	prefs[fileType] = prefixes
extensions = exts
prefixes = prefs

if not parseFunc:
	raise ImportError, "No working multi-sequence file parsers found."

def parseFile(filename, fileType, minSeqs=2):
	seqs = None
	if isinstance(filename, basestring) \
	and not filename.startswith("http:") \
	and not os.path.exists(filename):
		raise UserError("No such file: %s" % filename)
	for parserType, parse in parseFunc.items():
		if fileType and parserType != fileType:
			continue
		replyobj.status("Trying %s parser\n" % parserType)
		try:
			seqs, fileAttrs, fileMarkups = parse(filename)
		except WrongFileTypeError:
			if fileType:
				raise UserError("'%s' is not a %s file" % (
							filename, parserType))
			continue
		except FormatSyntaxError, val:
			raise IOError, "Syntax error in %s file '%s': %s" % (
						parserType, filename, val)
		except:
			replyobj.reportException("Error in %s parse() function"
								% parserType)
			continue
		if seqs and len(seqs) < minSeqs:
			raise UserError("Only one sequence found in %s file"
				" '%s'.\nCheck your alignment file for errors."
				"\nIf the file seems correct, use Help->"
				"Report a Bug menu item to report the problem."
				% (parserType, filename))
		replyobj.status("%s parser succeeded for %s\n" % (parserType,
								filename))
		break
	if seqs is None:
		replyobj.error("File '%s' not recognized by any"
					" multi-sequence parsers\n" % filename)
		return None, None, None
	
	for s in seqs:
		if len(s) != len(seqs[0]):
			raise UserError("Sequence '%s' differs in length from"
				" preceding sequences.\nCheck your alignment"
				" file for errors.\nIf the file seems correct,"
				" use 'Help->Report a Bug' menu item to report"
				" the problem." % s.name)
		if s.name.endswith(" x 2") or '/' in s.name \
		and s.name[:s.name.rindex('/')].endswith(" x 2"):
			# set up circular attribute
			nogaps = s.ungapped()
			if nogaps[:len(nogaps)/2] == nogaps[len(nogaps)/2:]:
				s.circular = True
	return seqs, fileAttrs, fileMarkups
