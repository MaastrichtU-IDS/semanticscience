"""Parser for BLAST output

This parser is designed for BLAST output with the following options:

	program: "blastp" (-p blastp)
	database: "pdb" (-d pdb)
	alignment view: "flat master-slave, no identities" (-m 6)
	GI included in deflines (-I)

The corresponding BLAST command line is something like:

	blastall -p blastp -d pdbaa -I -J -e 1e-5 -M BLOSUM62 \
					-m 6 -o blast.out -i fasta_input
"""

import re

REQueryLen = re.compile("\((?P<length>\d+) letters\)")
REDatabaseSize = re.compile("(?P<sequences>[\d,]+) sequences; "
				"(?P<letters>[\d,]+) total letters")
REMatch = re.compile("gi\|(?P<gi>\d+)\|pdb\|(?P<pdb>[^|]+)\|(?P<chain>.)"
			"(?P<desc>.*)\s+(?P<score>\d+)\s+(?P<evalue>[-e.\d]+)")
REMatch2 = re.compile("gi\|(?P<gi>\d+)\|(?P<db>[^|]+)\|(?P<dbid>[^|]*)\|"
			"(?P<desc>.*)\s+(?P<score>\d+)\s+(?P<evalue>[-e.\d]+)")
REAlign = re.compile("(?P<gi>\S+)\s+(?P<start>\d+)\s+(?P<seq>\S+)\s+"
			"(?P<end>\d+)")
RENoAlign = re.compile("(?P<gi>\S+)\s*\d*\s+(?P<seq>-+)\s*\d*\s*")
REMatrix = re.compile("Matrix: (?P<matrix>\S+)")
REGap = re.compile("Gap Penalties: Existence: (?P<existence>\d+), "
				"Extension: (?P<extension>\d+)")

class Parser:

	def __init__(self, trueName, results, fromPsiblast=False):
		self.trueName = trueName
		self.lines = map(str.strip, results.split('\n'))
		if fromPsiblast:
			self._psiblast2blast(self.lines)
		self.lineno = 0
		self.secondaryHits = {}
		self._getVersion()
		self._getReference()
		self._getQuery()
		self._getDatabase()
		self._getMatches()
		self._getAlignment()
		self._getInfo()

	def _psiblast2blast(self, lines):
		# Make psiblast output look like blast output by
		# keeping only alignment data from last round
		firstRound = lastRound = -1
		for i, line in enumerate(lines):
			if line.startswith("Results from round"):
				lastRound = i
				if firstRound < 0:
					firstRound = i
		if firstRound < 0:
			# No psiblast rounds, just leave output alone
			return
		oldSeq = -1
		newSeq = -1
		for i in range(lastRound, len(lines)):
			line = lines[i]
			if line.startswith("Sequences used in model and found"):
				oldSeq = i
			if line.startswith("Sequences not found previously"):
				newSeq = i
				break
		if newSeq > lastRound:
			del lines[newSeq - 1:newSeq + 2]
		if oldSeq > lastRound:
			del lines[oldSeq]
		del lines[firstRound:lastRound + 1]

	def _getLine(self):
		line = self.lines[self.lineno]
		self.lineno = self.lineno + 1
		return line

	def _ungetLine(self):
		self.lineno = self.lineno - 1

	def _getVersion(self):
		while self.lineno < len(self.lines):
			line = self._getLine()
			if line[:6] == "BLASTP":
				self.version = line.split()[1]
				break
		else:
			raise SyntaxError, "no BLAST version line found"

	def _getReference(self):
		state = 0	# 0 = have not seen reference yet
				# 1 = copying reference
		ref = []
		while self.lineno < len(self.lines):
			line = self._getLine()
			if state == 0:
				if line[:11] == "Reference: ":
					ref.append(line[11:])
					state = 1
			else:
				if not line:
					break
				ref.append(line)
		else:
			raise SyntaxError, "no BLAST reference found"
		self.reference = ref

	def _getQuery(self):
		while self.lineno < len(self.lines):
			line = self._getLine()
			if line[:6] != "Query=":
				continue
			self.query = line[6:].strip()
			line = self._getLine()
			m = REQueryLen.match(line)
			if not m:
				raise SyntaxError, "no BLAST query length found"
			self.queryLength = int(m.group("length"))
			break
		else:
			raise SyntaxError, "no BLAST query found"

	def _getDatabase(self):
		while self.lineno < len(self.lines):
			line = self._getLine()
			if line[:10] != "Database: ":
				continue
			self.database = line[10:]
			line = self._getLine()
			m = REDatabaseSize.match(line)
			if not m:
				raise SyntaxError, \
					"no BLAST database size found"
			self.dbSizeSequences = int(m.group("sequences").replace(",", ""))
			self.dbSizeLetters = int(m.group("letters").replace(",", ""))
			break
		else:
			raise SyntaxError, "no BLAST query found"

	def _getMatches(self):
		matches = []
		matches.append(Match(self.trueName, None, desc="user_input"))
		while self.lineno < len(self.lines):
			line = self._getLine()
			if not line.startswith(
			"Sequences producing significant alignments:"):
				continue
			self._getLine()		# skip blank line
			while self.lineno < len(self.lines):
				line = self._getLine()
				if not line:
					break
				m = REMatch.match(line)
				if m is not None:
					chain = m.group("chain")
					if chain == " ":
						pdb = m.group("pdb")
					else:
						pdb = "%s_%s" % (m.group(2),
									chain)
				else:
					m = REMatch2.match(line)
					if not m:
						raise IOError(
							"unparsable match:\n"
							+ line)
					pdb = None
				gi = m.group("gi")
				desc = m.group("desc").strip()
				score = int(m.group("score"))
				ev = m.group("evalue")
				if ev.startswith("e"):
					ev = "1" + ev
				evalue = float(ev)
				matches.append(Match(gi, pdb, desc,
							score, evalue))
			break
		else:
			raise SyntaxError, "no BLAST matches found"
		self.matches = matches
		self.matchDict = {}
		for m in matches:
			self.matchDict[m.gi] = m

	def _getAlignment(self):
		while 1:
			self._readBlock()
			# if line following block is blank,
			# then there is another block afterwards
			# otherwise, we reached the end
			line = self._getLine()
			if line:
				self._ungetLine()
				break

	def _readBlock(self):
		seen = {}
		while 1:
			try:
				line = self._getLine()
			except IndexError:
				raise IOError, "unexpected EOF in alignment"
			m = REAlign.match(line)
			if m:
				gi = m.group("gi")
				if gi == "QUERY" or gi[:6] == "tmpseq":
					gi = self.trueName
				match = self._findMatch(seen, gi)
				start = int(m.group("start"))
				seq = m.group("seq")
				end = int(m.group("end"))
				match.addSequence(start, end, seq)
				continue
			m = RENoAlign.match(line)
			if m:
				gi = m.group("gi")
				if gi == "QUERY" or gi[:6] == "tmpseq":
					gi = self.trueName
				match = self._findMatch(seen, gi)
				seq = m.group("seq")
				match.addSequence(-1, -1, seq)
				continue
			self._ungetLine()
			return

	def _findMatch(self, seen, gi):
		if seen.has_key(gi):
			# Seen before, key is gi+version
			version = seen[gi]
			key = (gi, version)
		else:
			# Not seen before, key for next match with
			# same gi is gi+version
			version = 0
			key = gi
		seen[gi] = version + 1
		try:
			# Found, return it.
			return self.matchDict[key]
		except KeyError:
			# Not found.  Copy original gi and return.
			m = self.matchDict[gi]
			newMatch = Match(m.gi, m.pdb, m.description,
						m.score, m.evalue)
			self.matches.append(newMatch)
			self.matchDict[key] = newMatch
			return newMatch

	def _getInfo(self):
		while self.lineno < len(self.lines):
			line = self._getLine()
			m = REMatrix.match(line)
			if m:
				self.matrix = m.group("matrix")
				continue
			m = REGap.match(line)
			if m:
				self.gapExistence = int(m.group("existence"))
				self.gapExtension = int(m.group("extension"))
				continue

	def writeMSF(self, f, perLine=60, block=10, matches=None):
		if matches is None:
			matches = self.matches
		if self.matches[0] not in matches:
			matches.insert(0, self.matches[0])
		length = len(matches[0].sequence)
		# Assumes that all sequence lengths are equal

		f.write("Query: %s\n" % self.query)
		f.write("BLAST Version: %s\n" % self.version)
		f.write("Reference: %s\n" % self.reference[0])
		for r in self.reference[1:]:
			f.write("\t%s\n" % r)
		f.write("Database: %s\n" % self.database)
		f.write("Database size: %d sequences, %d letters\n" %
			(self.dbSizeSequences, self.dbSizeLetters))
		f.write("Matrix: %s\n" % self.matrix)
		f.write("Gap penalties: existence: %d, extension: %d\n" %
			(self.gapExistence, self.gapExtension))
		f.write("\n")
		label = {}
		for m in matches:
			label[m] = m.pdb or m.gi
		width = max(map(lambda m: len(label[m]), matches[1:]))
		for m in matches[1:]:
			f.write("%*s %4d %g" %
				(width, label[m], m.score, m.evalue))
			if m.description:
				f.write(" %s\n" % m.description)
			else:
				f.write("\n")
		f.write("\n")

		import time
		now = time.strftime("%B %d, %Y %H:%M",
					time.localtime(time.time()))
		f.write(" %s  MSF: %d  Type: %s  %s  Check: %d ..\n\n"
				% ("BLAST", length, 'P', now , 0))

		nameWidth = max(map(lambda m: len(label[m]), matches))
		nameFmt = " Name: %-*s  Len: %5d  Check: %4d  Weight: %5.2f\n"
		for m in matches:
			f.write(nameFmt % (nameWidth, label[m], length, 0, 1.0))
		f.write("\n//\n\n")

		for i in range(0, length, perLine):
			start = i + 1
			end = start + perLine - 1
			if end > length:
				end = length
			seqLen = end - start + 1
			startLabel = str(start)
			endLabel = str(end)
			separators = (seqLen + block - 1) / block - 1
			blanks = (seqLen + separators
					- len(startLabel) - len(endLabel))
			if blanks < 0:
				f.write("%*s  %s\n" %
					(nameWidth, ' ', startLabel))
			else:
				f.write("%*s  %s%*s%s\n" %
					(nameWidth, ' ', startLabel,
					blanks, ' ', endLabel))
			for m in matches:
				f.write("%-*s " % (nameWidth, label[m]))
				for n in range(0, perLine, block):
					front = i + n
					back = front + block
					f.write(" %s" % m.sequence[front:back])
				f.write("\n")
			f.write("\n")

	def dump(self, f):
		f.write("Version: %s\n" % self.version)
		f.write("Reference: %s\n" % self.reference[0])
		for r in self.reference[1:]:
			f.write("\t%s\n" % r)
		f.write("Query: %s\n" % self.query)
		f.write("Query length: %d\n" % self.queryLength)
		f.write("Database: %s\n" % self.database)
		f.write("Database size: %d/%d\n" % (self.dbSizeSequences,
							self.dbSizeLetters))
		for m in self.matches:
			f.write("Match: %s\n" % repr(m))
			f.write("\tScore: bits: %d, e-value: %g\n" %
				(m.score, m.evalue))
			if m.description:
				f.write("\t%s\n" % m.description)
			m.printSequence(f, "\t")
		f.write("Matrix: %s\n" % self.matrix)
		f.write("Gap penalties: existence: %d, extension: %d\n" %
			(self.gapExistence, self.gapExtension))

	def sessionData(self):
		try:
			from cPickle import dumps
		except ImportError:
			from pickle import dumps
		return dumps(self)

def restoreParser(data):
	try:
		from cPickle import loads
	except ImportError:
		from pickle import loads
	return loads(data)

class Match:

	def __init__(self, gi, pdb, desc="", score=0, evalue=0):
		self.gi = gi
		self.pdb = pdb
		self.description = desc.strip()
		self.score = score
		self.evalue = evalue
		self.sequence = ""
		self.start = -1
		self.end = 0

	def __repr__(self):
		return "<Match %s (gi=%s) residues %d-%d>" % \
			(self.pdb, self.gi, self.start, self.end)

	def name(self):
		return self.pdb or self.gi

	def addSequence(self, start, end, s):
		if self.start < 0:
			self.start = start
		self.end = end
		self.sequence = self.sequence + s

	def printSequence(self, f, prefix, perLine=60):
		for i in range(0, len(self.sequence), perLine):
			f.write("%s%s\n" % (prefix, self.sequence[i:i+perLine]))


class BlastpdbService:

	outputFile = "blast.out"

	def __init__(self, queryName, querySeq, evalue, matrix, finishCB):
		from WebServices.AppService_types import ns0
		from WebServices.opal_client import OpalService
		self.queryName = queryName
		inputFile = ns0.InputFileType_Def("inputFile")
		inputFile._name = "query.fa"
		inputFile._contents = self.makeFasta(queryName, querySeq)
		service = "BlastpdbServicePort"
		argList = "-i %s -o %s -e %s -M %s" % (
				self.inputFile._name, self.outputFile,
				evalue, matrix)
		self.opal = OpalService(service)
		self.opal.launchJob(argList, _inputFile=[inputFile])
		self.finishCB = finishCB
		from chimera.tasks import Task
		self.task = Task("blastpdb %s" % queryName, self.cancelCB,
								self.statusCB)

	def cancelCB(self):
		self.task = None

	def statusCB(self):
		self.task.updateStatus(self.opal.currentStatus())
		if not self.opal.isFinished():
			self.opal.queryStatus()
			return
		self.task = None
		fileMap = self.opal.getOutputs()
		if self.opal.isFinished() > 0:
			# Successful completion
			self.finishCB(self.getURLContent(
						fileMap[self.outputFile]))
		else:
			# Failed
			from chimera import replyobj
			replyobj.error("blastpdb %s failed; "
					"see Reply Log for more information"
					% self.queryName)
			try:
				self.showURLContent("blastpdb stdout",
							fileMap["stdout"])
			except KeyError:
				pass
			try:
				self.showURLContent("blastpdb stderr",
							fileMap["stderr"])
			except KeyError:
				pass

	def makeFasta(self, name, seq):
		output = [ ">QUERY\n" ]
		maxLine = 60
		for i in range(0, len(seq), maxLine):
			end = min(i + maxLine, len(seq))
			output.append("%s\n" % seq[i:end])
		return ''.join(output)

	def getURLContent(self, url):
		import urllib2
		f = urllib2.urlopen(url)
		data = f.read()
		f.close()
		return data

	def showURLContent(self, title, url):
		from chimera import replyobj
		data = self.getURLContent(url)
		replyobj.message("%s\n-----\n%s-----\n" % (title, data))


class BlastproteinService:

	outputFile = "blast.out"

	def __init__(self, finishCB, params=None, sessionData=None):
		self.finishCB = finishCB
		if params is not None:
			self._initBlast(*params)
		else:
			self._initSession(*sessionData)

	def _initBlast(self, program, db, queryName, querySeq,
			evalue, matrix, passes):
		self.program = program
		self.db = db
		self.queryName = queryName
		self.params = (querySeq, evalue, matrix, passes)
		from WebServices.AppService_types import ns0
		from WebServices.opal_client import OpalService
		inputFile = ns0.InputFileType_Def("inputFile")
		inputFile._name = "query.fa"
		inputFile._contents = self.makeFasta(queryName, querySeq)
		service = "BlastproteinServicePort"
		argList = "-P %s -d %s -i %s -o %s -e %s -M %s -p %s" % (
				program, db, inputFile._name,
				self.outputFile, evalue, matrix, passes)
		try:
			self.opal = OpalService(service)
		except:
			import traceback, sys
			print "Traceback from Blast request:"
			traceback.print_exc(file=sys.stdout)
			print """
Typically, if you get a TypeError, it's a problem on the remote server
and it should be fixed shortly.  If you get a different error or
get TypeError consistently for more than a day, please report the
problem using the Report a Bug... entry in the Help menu.  Please
include the traceback printed above as part of the problem description."""
			from chimera import NonChimeraError
			raise NonChimeraError("Blast web service appears "
						"to be down.  See Reply Log "
						"for more details.")
		self.opal.launchJob(argList, _inputFile=[inputFile])
		from chimera.tasks import Task
		self.task = Task(self._title(), self.cancelCB,
								self.statusCB)

	def _initSession(self, program, db, queryName,
				params, running, opalData):
		self.program = program
		self.db = db
		self.queryName = queryName
		self.params = params
		from WebServices.opal_client import OpalService
		self.opal = OpalService(sessionData=opalData)
		if not running:
			self.task = None
		else:
			from chimera.tasks import Task
			self.task = Task(self._title(), self.cancelCB,
								self.statusCB)

	def _title(self):
		return "%s %s: %s" % (self.program, self.db, self.queryName)

	def sessionData(self):
		return (self.program, self.db, self.queryName, self.params,
				self.task is not None,
				self.opal.sessionData())

	def cancelCB(self):
		self.task = None

	def statusCB(self):
		self.task.updateStatus(self.opal.currentStatus())
		if not self.opal.isFinished():
			self.opal.queryStatus()
			return
		self.task = None
		fileMap = self.opal.getOutputs()
		if self.opal.isFinished() > 0:
			# Successful completion
			self.finishCB(self.getURLContent(
						fileMap[self.outputFile]))
		else:
			# Failed
			from chimera import replyobj
			replyobj.error("blast %s failed; "
					"see Reply Log for more information\n"
					% self.queryName)
			self.showURLContent("blast stderr", fileMap["stderr.txt"])
			self.showURLContent("blast stdout", fileMap["stdout.txt"])

	def makeFasta(self, name, seq):
		output = [ ">QUERY\n" ]
		maxLine = 60
		for i in range(0, len(seq), maxLine):
			end = min(i + maxLine, len(seq))
			output.append("%s\n" % seq[i:end])
		return ''.join(output)

	def getURLContent(self, url):
		import urllib2
		f = urllib2.urlopen(url)
		data = f.read()
		f.close()
		return data

	def showURLContent(self, title, url):
		from chimera import replyobj
		data = self.getURLContent(url)
		replyobj.message("%s\n-----\n%s-----\n" % (title, data))
