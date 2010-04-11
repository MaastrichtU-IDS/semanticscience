# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera
from chimera import replyobj
from chimera import elements
from chimera.baseDialog import ModalDialog
import os
import Tix, Tkinter, Pmw

FORMAT_MOL2 = '.mol2'
FORMAT_PDB = '.pdb'

def _value(s):
	try:
		return int(s)
	except ValueError:
		try:
			return float(s)
		except ValueError:
			return s

class Atom:
	"""Class for holding information about a single atom"""

	def __init__(self, aname, rtype, rseq, x, y, z):
		self.aname = aname.strip()
		if (len(self.aname) == 4 and aname[0] == 'H') \
		or aname[0] in "0123456789":
			self.atype = 'H'
		else:
			atype = aname[:2].strip()
			self.atype = atype[0].upper() + atype[1:].lower()
		if self.atype[-1] in "0123456789":
			self.atype = self.atype[:-1]
		self.rtype = rtype
		self.rseq = rseq
		self.x = x
		self.y = y
		self.z = z

	def makeChimera(self, mol):
		for name in [ self.atype, 'LP' ]:	# default to lone pair
			try:
				num = elements.name.index(name)
				break
			except ValueError:
				pass
		e = chimera.Element(num)
		self.chimeraAtom = mol.newAtom(self.aname, e)
		coord = chimera.Coord()
		coord.x = self.x
		coord.y = self.y
		coord.z = self.z
		self.chimeraAtom.setCoord(coord)

class Compound:
	"""Class for holding information about a single compound"""

	Undefined = 'U'
	Viable = 'V'
	Deleted = 'D'
	Purged = 'P'
	VMap = {		# map from old viewdock values to new ones
		-1:	Undefined,
		0:	Viable,
		1:	Deleted,
		2:	Purged
	}

	def __init__(self, chimeraMol=None, filetype=None, number=0):
		self.label = 'Unlabeled'
		self.atoms = {}
		self.atomList = []
		self.conect = []
		self.header = ''
		self.compnd = ''
		self.author = ''
		self.rawText = []
		self.fields = {}
		self.state = Compound.Viable
		self.listed = False
		self.data = []
		self.prevData = []
		self.textArray = []
		self.connected = 0
		if filetype == "Dock 4, 5 or 6":
			self._parseDock = self._parseDock4
		elif filetype == "Dock 3.5.x search":
			import re
			self._parseDock = self._parseDock35xSearch
			self._dockLine = 0
			self._dockRE = re.compile("""\s*([^=]+)\s*=\s*(\S+)""")
		elif filetype == "Dock 3.5.x single":
			self._parseDock = self._parseDock35xSingle
			self.number = number
		elif filetype == "Dock 3 or 3.5":
			import re
			self._parseDock = self._parseDock3
			self._dockLine = 0
			self._dockRE = re.compile("""\s*([^=]+)\s*=\s*(\S+)""")
		else:
			self._parseDock = self._parseDock4

		if chimeraMol and chimeraMol.pdbHeaders:
			self.chimeraModel = chimeraMol
			if chimeraMol.pdbHeaders.has_key('REMARK'):
				for line in chimeraMol.pdbHeaders['REMARK']:
					if self._pdbParseRemark(line):
						self.rawText.append(line)
			if chimeraMol.pdbHeaders.has_key('HEADER'):
				for line in chimeraMol.pdbHeaders['HEADER']:
					self._pdbParseHeader(line)
					self.rawText.append(line)
			if chimeraMol.pdbHeaders.has_key('COMPND'):
				for line in chimeraMol.pdbHeaders['COMPND']:
					self._pdbParseCompnd(line)
					self.rawText.append(line)
			if chimeraMol.pdbHeaders.has_key('AUTHOR'):
				for line in chimeraMol.pdbHeaders['AUTHOR']:
					self._pdbParseAuthor(line)
					self.rawText.append(line)
			self.text = '\n'.join(self.rawText)
		elif chimeraMol:
			self.chimeraModel = chimeraMol
			try:
				keys = chimeraMol.dockKeys.split('\001')
				values = chimeraMol.dockValues.split('\001')
			except AttributeError:
				keys = [ "Number" ]
				values = [ number ]
			if len(keys) != len(values):
				raise AssertionError, \
				  "Bad DOCK comments in file (keys != values)"
			for i in range(len(keys)):
				key = keys[i]
				value = values[i]
				if key == "Name":
					chimeraMol.name = value
				value = _value(value)
				if key == "viewdock state":
					self.state = self.VMap.get(value, value)
				self.fields[key] = value
			self.text = ''
			for comment in chimeraMol.mol2comments:
				if comment.find("viewdock state:") == -1:
					self.rawText.append(comment)

			self.text = '\n'.join(self.rawText)
			self.data = chimeraMol.mol2data

	def readPDB(self, f, defaultRseq):
		self._rseq = defaultRseq
		while 1:
			line = f.readline()
			if not line:
				break
			if line[:3] == 'TER':
				self.data.append(line)
				break
			elif line[:6] == 'ATOM  ':
				self._pdbParseAtom(line)
				self.data.append(line)
			elif line[:6] == 'CONECT':
				self._pdbParseConect(line)
				self.data.append(line)
			elif line[:6] == 'REMARK':
				if self._pdbParseRemark(line):
					self.rawText.append(line)
			elif line[:6] == 'HEADER':
				self._pdbParseHeader(line)
				self.rawText.append(line)
			elif line[:6] == 'COMPND':
				self._pdbParseCompnd(line)
				self.rawText.append(line)
			elif line[:6] == 'AUTHOR':
				self._pdbParseAuthor(line)
				self.rawText.append(line)
		seq = self._rseq
		del self._rseq
		return seq

	def _pdbParseAtom(self, line):
		serial = int(line[6:11])
		aname = line[12:16]
		rtype = line[17:20]
		try:
			rseq = int(line[22:26])
		except ValueError:
			rseq = self._rseq
		else:
			if rseq > self._rseq:
				self._rseq = rseq
		x = float(line[30:38])
		y = float(line[38:46])
		z = float(line[46:54])
		a = Atom(aname, rtype, rseq, x, y, z)
		self.atoms[serial] = a
		self.atomList.append(a)

	def _pdbParseConect(self, line):
		line = line[:31]  # ignore hydrogen bonds and salt bridges
		field = []
		start = 6
		while start < len(line):
			item = line[start:start+5].strip()
			if item:
				field.append(item)
			start += 5
		if len(field) < 2:
			#print 'CONECT record with %d fields!' % len(field)
			#print line
			return
		n = int(field[0])
		for d in field[1:]:
			m = int(d)
			if m > n:
				self.conect.append((n, m))
		self.connected = 1

	def _pdbParseRemark(self, line):
		try:
			int(line[7:10])
		except ValueError:
			return self._parseDock(line, len('REMARK'))
		return self._parseDock(line, 10)

	def _pdbParseHeader(self, line):
		self.header = line[6:].strip()
		self.textArray.append(line)

	def _pdbParseCompnd(self, line):
		self.compnd = line[6:].strip()
		self.textArray.append(line)

	def _pdbParseAuthor(self, line):
		self.author = line[6:].strip()
		self.textArray.append(line)

	def _parseDock4(self, line, prefixLen):
		keepRemark = 1
		field = line[prefixLen:].split(':')
		if len(field) == 2:
			key = field[0].strip()
			value = _value(field[1].strip())
			if key == 'viewdock state':
				self.state = self.VMap.get(value, value)
				keepRemark = 0
			else:
				self.fields[key] = value
		else:
			field = line[prefixLen:].rsplit(None, 1)
			if len(field) > 1:
				value = _value(field[1])
				if not isinstance(value, basestring):
					key = field[0].strip()
					self.fields[key] = value
		if keepRemark:
			self.textArray.append(line)
		return keepRemark

	def _parseDock3(self, line, prefixLen):
		field = line[prefixLen:].split(':')
		if len(field) == 2 and field[0].strip() == "viewdock state":
			value = _value(field[1].strip())
			self.state = self.VMap.get(value, value)
			return 0
		if self._dockLine == 0:
			self.fields["Description"] = line[prefixLen:].strip()
		elif self._dockLine == 1:
			self.fields["Name"] = line[prefixLen:32].strip()
			for k, v in self._dockRE.findall(line[32:]):
				self.fields[k] = _value(v)
		elif self._dockLine == 2:
			for k, v in self._dockRE.findall(line[prefixLen:]):
				self.fields[k] = _value(v)
		self._dockLine += 1
		if self._dockLine > 2:
			self._dockLine = 0
		return 1

	def _parseDock35xSearch(self, line, prefixLen):
		field = line[prefixLen:].split(':')
		if len(field) == 2 and field[0].strip() == "viewdock state":
			value = _value(field[1].strip())
			self.state = self.VMap.get(value, value)
			return 0
		line = line[prefixLen:].strip()
		if self._dockLine == 0:
			self.fields["Description"] = line
		elif self._dockLine == 1:
			field = line.split(None, 1)
			self.fields["Name"] = field[0]
			for k, v in self._dockRE.findall(field[1]):
				self.fields[k] = _value(v)
		self._dockLine += 1
		if self._dockLine > 1:
			self._dockLine = 0
		return 1

	def _parseDock35xSingle(self, line, prefixLen):
		field = line[prefixLen:].split(':')
		if len(field) == 2 and field[0].strip() == "viewdock state":
			value = _value(field[1].strip())
			self.state = self.VMap.get(value, value)
			return 0
		field = line[prefixLen:].split()
		if len(field) == 8:
			# field[0] is a cutesy "s" (to make REMARK plural)
			self.fields["Conformation"] = _value(field[1])
			self.fields["Contacts"] = _value(field[2])
			self.fields["Electrostatics"] = _value(field[3])
			self.fields["VDW"] = _value(field[4])
			self.fields["Total"] = _value(field[5])
			self.fields["RMSD"] = _value(field[6])
			self.fields["Identifier"] = _value(field[7])
			self.fields["Number"] = self.number
		return 1

	def readMol2(self, f):
		if self._mol2ReadDockComments(f) < 0:
			return
		if self._mol2ReadMoleculeSection(f) < 0:
			return
		if self._mol2ReadAtomSection(f) < 0:
			return
		if self._mol2ReadBondSection(f) < 0:
			return

	def _mol2ReadDockComments(self, f):
		state = 0
		while 1:
			line = f.readline()
			if not line:
				return -1
			if line[0] == '#':
				state = 1
				if self._parseDock(line, len('##########')):
					self.rawText.append(line)
			elif state == 1:
				self.data.append(line)
				line = line.strip().lower()
				if line == '@<tripos>molecule':
					break
			else:
				self.prevData.append(line)
		return 0

	def _mol2ReadMoleculeSection(self, f):
		state = 1
		while 1:
			line = f.readline()
			if not line:
				return -1
			# Note that state 0 of checking for the
			# correct head is done in _mol2ReadDockComments
			self.data.append(line)
			if state == 1:
				# mol_name
				self.name = line
				state = 2
			elif state == 2:
				# atoms bonds subst feat sets
				data = line.split()
				if len(data) >= 3:
					self.numAtoms = int(data[0])
					self.numBonds = int(data[1])
					self.numSubst = int(data[2])
				state = 3
			elif state == 3:
				# mol_type (e.g., SMALL)
				state = 4
			elif state == 4:
				# charge_type (e.g., NO_CHARGES)
				# some DOCK files are missing the
				# status_bits and mol_comment lines, 
				# so break here
				break
		return 0

	def _mol2ReadAtomSection(self, f):
		while 1:
			line = f.readline()
			if not line:
				return -1
			self.data.append(line)
			line = line.strip().lower()
			if line == '@<tripos>atom':
				break
		for i in range(self.numAtoms):
			line = f.readline()
			if not line:
				self.atoms = {}
				self.atomList = []
				return -1
			data = line.split()
			if len(data) < 6:
				self.atoms = {}
				self.atomList = []
				return -1
			self.data.append(line)
			serial = int(data[0])
			aname = data[1]
			x = float(data[2])
			y = float(data[3])
			z = float(data[4])
			try:
				rseq = int(data[6])
				rtype = data[7]
			except (ValueError, IndexError):
				rseq = 0
				rtype = 'UNK'
			a = Atom(aname, rtype, rseq, x, y, z)
			self.atoms[serial] = a
			self.atomList.append(a)
		return 0

	def _mol2ReadBondSection(self, f):
		while 1:
			line = f.readline()
			if not line:
				return -1
			self.data.append(line)
			line = line.strip().lower()
			if line == '@<tripos>bond':
				break
		for i in range(self.numBonds):
			line = f.readline()
			if not line:
				self.atoms = {}
				self.atomList = []
				return -1
			data = line.split()
			if len(data) < 4:
				self.atoms = {}
				self.atomList = []
				return -1
			self.data.append(line)
			n = int(data[1])
			m = int(data[2])
			self.conect.append((n, m))
		return 0

	def buildChimera(self):
		self.text = ''.join(self.textArray)
		del self.textArray
		mol = chimera.Molecule()
		mol.name = self.compnd
		rMap = {}
		for a in self.atomList:
			a.makeChimera(mol)
			key = (a.rtype, a.rseq)
			try:
				res = rMap[key]
			except KeyError:
				res = mol.newResidue(a.rtype, ' ', a.rseq, ' ')
				rMap[key] = res
			res.addAtom(a.chimeraAtom)
		for f, t in self.conect:
			try:
				a1 = self.atoms[f]
				a2 = self.atoms[t]
				mol.newBond(a1.chimeraAtom, a2.chimeraAtom)
			except KeyError:
				pass
		if not self.connected:
			chimera.connectMolecule(mol)
		self.chimeraModel = mol

	def buildLabel(self):
		if not self.chimeraModel:
			return
		self.label = ('Chimera Model %s' % self.chimeraModel.oslIdent())

	def addAttributes(self, attrMap):
		if not self.chimeraModel:
			return
		for f, v in self.fields.iteritems():
			setattr(self.chimeraModel, attrMap[f], v)

	def hide(self):
		if not self.chimeraModel:
			return
		mList = chimera.openModels.list(id=self.chimeraModel.id,
						subid=self.chimeraModel.subid)
		for m in mList:
			m.display = 0

	def show(self):
		if not self.chimeraModel:
			return
		mList = chimera.openModels.list(id=self.chimeraModel.id,
						subid=self.chimeraModel.subid)
		for m in mList:
			m.display = 1

	def displayed(self):
		if not self.chimeraModel:
			return False
		return self.chimeraModel.display

	def closeChimeraModel(self):
		mList = [ self.chimeraModel ]
		self.chimeraModel = None
		chimera.openModels.close(mList)

	def save(self, format, f):
		if format is FORMAT_MOL2:
			joiner = '\n'
		else:
			joiner = ''
		f.write(joiner.join(self.rawText))
		if format is FORMAT_MOL2:
			f.write('\n########## viewdock state: %s\n'
								% self.state)
		else:
			f.write('REMARK viewdock state: %s\n' % self.state)
		f.write(joiner.join(self.data))
		f.write(joiner)

	def saveSession(self):
		if self.chimeraModel:
			import SimpleSession
			model = SimpleSession.sessionID(self.chimeraModel)
		else:
			model = None
		return (self.fields, self.state, self.rawText, self.data,
				self.label, self.listed, self.text, model)

	def restoreSession(self, data):
		(self.fields, self.state, self.rawText, self.data,
			self.label, self.listed, self.text, model) = data
		if model:
			import SimpleSession
			self.chimeraModel = SimpleSession.idLookup(model)
		else:
			self.chimeraModel = None

class MordorCompound(Compound):

	def __init__(self, path, results, number=0):
		Compound.__init__(self, filetype='Mordor', number=number)
		self.number = number
		self.results = results
		self.text = ''
		self.mordorPath = path
		self.mordorLigand = None
		self.prevId = None

	def show(self):
		if not self.chimeraModel:
			self.loadMordor()
		Compound.show(self)
		self.results.mordorShown(self)

	def hide(self):
		Compound.hide(self)
		self.results.mordorHidden(self)

	def closeChimeraModel(self):
		mList = [ self.chimeraModel, self.mordorLigand ]
		self.chimeraModel = None
		self.mordorLigand = None
		chimera.openModels.close(mList)
		self.results.mordorCloseCB(self)

	def loadMordor(self):
		if self.prevId:
			id, subid = self.prevId
		else:
			id, subid = self.results.mordorIds
		try:
			receptorFile = os.path.join(self.mordorPath,
							self.fields['recefile'])
			receptorBegin = self.fields['recebeg']
			receptorEnd = self.fields['receend']
		except KeyError, key:
			replyobj.error("Cannot load compound %d "
						"because field \"%s\" is "
						"missing" % (self.number, key))
			return
		receptorName = "Receptor %d" % self.number
		self.chimeraModel = self.loadMordorModel(receptorFile,
						receptorBegin,
						receptorEnd,
						receptorName,
						id, subid, None)
		id = self.chimeraModel.id
		subid = self.chimeraModel.subid
		ligandFile = os.path.join(self.mordorPath,
						self.fields['ligafile'])
		ligandBegin = self.fields['ligabeg']
		ligandEnd = self.fields['ligaend']
		ligandName = "Ligand %d" % self.number
		self.mordorLigand = self.loadMordorModel(ligandFile,
							ligandBegin,
							ligandEnd,
							ligandName,
							id, subid,
							self.chimeraModel)
		self.applyTemplates()
		if not self.prevId:
			self.prevId = ( id, subid )
			self.results.mordorIds = ( id, subid + 1 )
		self.label = ('Chimera Model %s' % self.chimeraModel.oslIdent())

	def loadMordorModel(self, filename, start, end, name, id, subid, ref):
		import tempfile
		fd, tmpfile = tempfile.mkstemp('.pdb', 'mordor')
		try:
			f = open(filename, "rb")
			f.seek(start)
			data = f.read(end - start)
			os.write(fd, data)
			f.close()
			os.close(fd)
			mList = chimera.openModels.open(tmpfile,
							identifyAs=name,
							baseId=id,
							subid=subid,
							sameAs=ref)
			return mList[0]
		finally:
			os.remove(tmpfile)

	def receptorTemplate(self):
		return ReceptorTemplate(self.chimeraModel)

	def ligandTemplate(self):
		return LigandTemplate(self.mordorLigand)

	def applyTemplates(self, templates=None):
		for a in self.mordorLigand.atoms:
			a.surfaceCategory = "ligand"
		if templates is None:
			templates = self.results.mordorActiveTemplates
		if templates is None:
			return
		rTemplate, lTemplate, showHb = templates
		if rTemplate is not None:
			rTemplate.apply(self.chimeraModel)
		if lTemplate is not None:
			lTemplate.apply(self.mordorLigand)
		if showHb == "ligand-receptor":
			spec = "%s%s" % (self.mordorLigand.oslIdent(),
					self.chimeraModel.oslIdent())
			chimera.runCommand("findhbond intramodel false spec %s"
					% spec)
		elif showHb == "all":
			spec = "%s%s" % (self.mordorLigand.oslIdent(),
					self.chimeraModel.oslIdent())
			chimera.runCommand("findhbond spec %s" % spec)

class Results:
	"""Class for holding information about a set of DOCK results"""

	def __init__(self, filename, filetype, notifySelectionChange,
			notifyCompoundChange, sessionData):
		self.notifySelectionChange = notifySelectionChange
		self.notifyCompoundChange = notifyCompoundChange
		self.filename = filename
		self.uiFrame = None
		self.uiScrolledList = None
		self.uiList = None
		self.header = []
		self.sortColumn = None
		self.sortDir = {}
		self.displayedCompounds = []
		self.diagramDisplay = False
		self.diagramWidth = 64
		self.diagramHeight = 64
		self.diagramBlank = None
		self.diagramCache = {}
		self.diagramPending = set([])
		format = FORMAT_PDB
		from OpenSave import osOpen, compressSuffixes
		if filename.endswith(FORMAT_MOL2):
			format = FORMAT_MOL2
		else:
			for cs in compressSuffixes:
				if filename.endswith(FORMAT_MOL2 + cs):
					format = FORMAT_MOL2
					break
		self.compoundList = []
		self.format = format
		if sessionData is not None:
			replyobj.status("opening %s..." % filename)
			self.restoreSession(sessionData)
		elif filetype == "Mordor":
			self.mordorLRU = LRU(10)
			self.mordorIds = [ chimera.openModels.Default, 1 ]
			self.mordorTemplates = {}
			self.mordorActiveTemplates = None
			d = os.path.dirname(filename)
			f = osOpen(filename)
			keys = f.readline().split()
			index = 1
			for line in f:
				values = line.split()
				if len(values) != len(keys):
					replyobj.warning("bad Mordor line")
					continue
				c = MordorCompound(d, self, number=index)
				for i in range(len(keys)):
					c.fields[keys[i]] = _value(values[i])
				c.chimeraModel = None
				self.compoundList.append(c)
				index += 1
		elif format == FORMAT_MOL2 or filetype.startswith('Modeller'):
			replyobj.status("opening %s..." % filename)
			mList = chimera.openModels.open(filename)
			if len(mList) == 0:
				raise chimera.UserError(
						"no models found in file %s!"
						% filename)
			else:
				i = 1
				for mol in mList:
					self.compoundList.append(
							Compound(mol, number=i))
					i += 1
		else:
			nextrseq = 0
			f = osOpen(filename)
			index = 1
			while 1:
				c = Compound(filetype=filetype, number=index)
				try:
					rseq = c.readPDB(f, nextrseq)
				except ValueError, e:
					raise chimera.UserError(
						"error in PDB input: %s"
						% str(e))
				nextrseq = max(nextrseq, rseq) + 1
				if len(c.atoms) == 0:
					break
				self.compoundList.append(c)
				replyobj.status("%d molecules read" % index)
				index += 1
			f.close()
			if len(self.compoundList) == 0:
				raise chimera.UserError(
						"no models found in file %s!"
						% filename)
			else:
				replyobj.status("building Chimera models...")
				for cmpd in self.compoundList:
					cmpd.buildChimera()
				chimera.openModels.add([ c.chimeraModel
						for c in self.compoundList ])

		keys = {}
		for c in self.compoundList:
			for k in c.fields.keys():
				keys[k] = 1
			c.buildLabel()
		if len(keys) == 0:
			raise chimera.UserError("file %s does not appear to be"
						" DOCK output" % filename)
		self.fields = keys.keys()
		self.fields.sort()

		from chimera.misc import stringToAttr
		attrMap = {}
		attrUsed = {}
		for f in self.fields:
			a = stringToAttr(f, prefix="dock", style="caps")
			try:
				count = attrUsed[a]
			except KeyError:
				attrUsed[a] = 2
			else:
				attrUsed[a] = count + 1
				a = a + str(count)
			attrMap[f] = a
		for c in self.compoundList:
			c.addAttributes(attrMap)

		self.style = {'S': 'string'}
		for k in self.fields:
			self.style[k] = 'number'
		for c in self.compoundList:
			for k, v in c.fields.items():
				if isinstance(v, basestring):
					self.style[k] = 'string'
		self.displayStyle = {}

		if sessionData is not None:
			columnKeys = self.columnKeys
			try:
				columnKeys.remove('S')
			except ValueError:
				pass
			self.columnKeys = []
			self.setCompoundsKeys(columnKeys)
		elif filetype == "Mordor":
			self.selected = []
			self.columnKeys = []
			columnKeys = []
			initKeys = [
				"Ref",
				"rmsR",
				"nR",
				"nL",
				"nRIL",
				"vRIL",
				"eRIL",
				"sRIL",
				"vR",
				"eR",
				"sR",
				"dR",
				"iR",
			]
			for key in initKeys:
				if keys.has_key(key):
					columnKeys.append(key)
			if len(columnKeys) == 0:
				columnKeys.append(self.fields[0])
			self.setCompoundsKeys(columnKeys)
			self.sortedCompoundList = self.compoundList[:]
		else:
			self.selected = [ self.compoundList[0] ]
			for c in self.compoundList[1:]:
				c.hide()
			self.columnKeys = []
			columnKeys = []
			if keys.has_key('Number'):
				columnKeys.append('Number')
			if keys.has_key('Name'):
				columnKeys.append('Name')
			if filetype.startswith('Modeller') \
			and keys.has_key('MODELLER OBJECTIVE FUNCTION'):
				columnKeys.append('MODELLER OBJECTIVE FUNCTION')
			if len(columnKeys) == 0:
				columnKeys.append(self.fields[0])
			self.setCompoundsKeys(columnKeys)
			self.sortedCompoundList = self.compoundList[:]
		replyobj.status('building display lists...', blankAfter=1)

	def setCompoundsFrame(self, frame):
		from chimera import chimage
		self.uiFrame = frame
		self.upArrow = chimage.get("uparrow.png", frame)
		self.downArrow = chimage.get("downarrow.png", frame)

	def setCompoundsKeys(self, keys):
		if len(keys) + 1 != len(self.columnKeys) \
		and self.uiScrolledList is not None:
			# Tix HList does cannot change number of
			# columns dynamically, so we need to destroy
			# the existing one if it does not have the
			# right number of columns
			self._destroyScrolledList()
		self.columnKeys = ['S'] + keys

	def _destroyScrolledList(self):
		for ds in self.displayStyle.values():
			ds.delete()
		self.displayStyle = {}
		for h in self.header:
			h.destroy()
		self.header = []
		self.uiScrolledList.destroy()
		self.uiScrolledList = None
		self.uiList = None

	def _makeFormats(self, tw, dw, a):
		if tw > dw:
			tpad = 0
			twidth = tw
			dpad = (tw - dw) / 2
			dwidth = twidth - dpad
		else:
			dpad = 0
			dwidth = dw
			tpad = (dw - tw) / 2
			twidth = dwidth - tpad
		return '%%%ds%s' % (twidth, tpad * ' '), \
			'%%%s%ds%s' % (a, dwidth, dpad * ' ')

	def createColumn(self, col, style, replacing=None):
		if replacing in self.fields and replacing != col:
			self.fields.remove(replacing)
			self.fields.append(col)
			self.fields.sort()
			del self.style[replacing]
			self.style[col] = style
			try:
				n = self.columnKeys.index(replacing)
			except ValueError:
				pass
			else:
				self.columnKeys[n] = col
			return "renamed"
		elif col not in self.fields:
			self.fields.append(col)
			self.fields.sort()
			self.style[col] = style
			return "created"
		return "exists"

	def addColumn(self, col):
		if col not in self.fields or col in self.columnKeys:
			return 0
		self.setCompoundsKeys(list(self.columnKeys)[1:] + [col])
		return 1

	def deleteColumn(self, col):
		if col not in self.fields or col not in self.columnKeys:
			return 0
		l = self.columnKeys[1:]
		l.remove(col)
		self.setCompoundsKeys(l)
		return 1

	def getColumns(self):
		return self.columnKeys[1:]

	def _getField(self, c, k):
		if k == 'S':
			return c.state
		else:
			return c.fields.get(k, None)

	def setSortKey(self, k, dir=None):
		if self.sortColumn:
			try:
				n = self.columnKeys.index(self.sortColumn)
			except ValueError:
				# column not displayed
				pass
			else:
				self.header[n].setImage(None)
		all = [ (self._getField(c, k), c)
			for c in self.compoundList ]
		all.sort()
		disp = [ (self._getField(c, k), c)
			for c in self.displayedCompounds ]
		disp.sort()
		# dir is the new sort direction.
		# so we will store in "sortDir" the sort
		# direction we will use _next_ time.
		try:
			if dir is None:
				dir = self.sortDir[k]
		except KeyError:
			self.sortDir[k] = "down"	# next time
			image = self.upArrow
		else:
			if dir == "up":
				# lists are already low to high
				self.sortDir[k] = "down"	# next time
				image = self.upArrow
			else:
				all.reverse()	# go from high to low
				disp.reverse()
				self.sortDir[k] = "up"	# next time
				image = self.downArrow
		self.sortedCompoundList = [ t[1] for t in all ]
		self.displayedCompounds = [ t[1] for t in disp ]
		self.sortColumn = k
		try:
			n = self.columnKeys.index(self.sortColumn)
		except ValueError:
			# column not displayed
			pass
		else:
			self.header[n].setImage(image)

	def updateCompounds(self, show, filterSet):
		compounds = []
		for c in self.sortedCompoundList:
			if not show[c.state]:
				c.listed = False
				continue
			if filterSet is not None and c not in filterSet:
				c.listed = False
				continue
			c.listed = True
			compounds.append(c)
		self.displayedCompounds = compounds
		self.updateDisplayedCompounds()

	def updateDisplayedCompounds(self):
		numColumns = len(self.columnKeys)
		numCompounds = len(self.displayedCompounds)
		values = []
		for c in self.displayedCompounds:
			v = [ c.state ]
			for k in self.columnKeys[1:]:
				try:
					v.append(str(c.fields[k]))
				except KeyError:
					v.append('')
			values.append(v)
		if self.diagramDisplay:
			nc = numColumns + 1
			self._diagramMakeBlank()
		else:
			nc = numColumns
		if self.uiScrolledList is None:
			self.uiScrolledList = Tix.ScrolledHList(self.uiFrame,
				options = """hlist.columns %d
				hlist.header 1
				hlist.selectMode extended
				hlist.indicator 1""" % nc)
			self.uiScrolledList.pack(expand=1, fill=Tkinter.BOTH)
			self.uiList = self.uiScrolledList.hlist
			self.uiList.config(
				browsecmd=self.updateSelectedCompounds)
			self.displayStyle['string'] = Tix.DisplayStyle('text',
				refwindow=self.uiScrolledList, anchor='w')
			self.displayStyle['number'] = Tix.DisplayStyle('text',
				refwindow=self.uiScrolledList, anchor='e')
			newList = 1
		else:
			self.uiList.delete_all()
			newList = 0
		bg = self.uiList["bg"]
		if self.diagramDisplay:
			self.uiList.header_create(0 , itemtype="text",
							text="Diagram")
		for i in range(numColumns):
			k = self.columnKeys[i]
			if self.diagramDisplay:
				col = i + 1
			else:
				col = i
			if newList:
				def f(event, key=k):
					self.setSortKey(key)
					self.updateDisplayedCompounds()
				c = ColumnHeader(self.uiList, k, command=f)
				self.header.append(c)
				self.uiList.header_create(col, itemtype='window',
								window=c)
			else:
				self.header[i].setTitle(k)
		if self.sortColumn:
			try:
				n = self.columnKeys.index(self.sortColumn)
			except ValueError:
				# column not displayed
				pass
			else:
				if self.sortDir[self.sortColumn] == "up":
					image = self.downArrow
				else:
					image = self.upArrow
				self.header[n].setImage(image)
		for row in range(numCompounds):
			self.uiList.add(row)
			value = values[row]
			if self.diagramDisplay:
				self.uiList.item_create(row, 0,
							itemtype='imagetext',
							image=self.diagramBlank,
							showtext=False)
			for i in range(numColumns):
				if self.diagramDisplay:
					col = i + 1
				else:
					col = i
				name = self.columnKeys[i]
				style = self.style[name]
				ds = self.displayStyle[style]
				self.uiList.item_create(row, col,
							text=value[i],
							style=ds)
		if self.diagramDisplay:
			self.diagramUpdate()
		if self.selected == self.displayedCompounds:
			self.uiList.selection_set(0, numCompounds - 1)
			self.uiList.see(0)
		else:
			selected = []
			n = -1
			for c in self.selected:
				try:
					# Select previously displayed item
					n = self.displayedCompounds.index(c)
					selected.append(c)
					self.uiList.selection_set(n)
				except ValueError:
					# Hide no longer displayed compound
					c.hide()
			if self.selected and n < 0:
				# show next one instead
				n = -1
				for c in self.sortedCompoundList[
						self.sortedCompoundList.index(
						self.selected[0])+1:]:
					try:
						n = self.displayedCompounds.index(c)
					except ValueError:
						continue
					selected.append(c)
					c.show()
					self.uiList.selection_set(n)
					break
			if selected and n >= 0:
				self.uiList.see(n)
			self.selected = selected
		self.notifySelectionChange(self.selected)

	def pruneModels(self, molList):
		compounds = self._getCompounds(molList)
		changed = []
		for c in compounds:
			if c.state == Compound.Viable:
				c.state = Compound.Deleted
				changed.append(c)
			c.hide()
		if changed:
			self.notifyCompoundChange(changed)

	def selectModels(self, molList, update=True):
		selected = self._getCompounds(molList)
		if update:
			self.setSelected(selected)
		else:
			self.selected = selected
			self.notifySelectionChange(self.selected)

	def _getCompounds(self, molList):
		compounds = []
		for c in self.compoundList:
			if c.chimeraModel in molList:
				compounds.append(c)
		return compounds

	def setSelected(self, selected):
		for c in self.selected:
			c.hide()
		for c in selected:
			c.show()
		self.selected = selected
		self.updateDisplayedCompounds()

	def invertSelected(self):
		for c in self.selected:
			c.hide()
		selected = [ c for c in self.displayedCompounds
				if c not in self.selected ]
		for c in selected:
			c.show()
		self.selected = selected
		self.updateDisplayedCompounds()

	def updateSelectedCompounds(self, event=None):
		compounds = []
		for s in self.uiList.info_selection():
			compounds.append(self.displayedCompounds[int(s)])
		if compounds == self.selected:
			return
		for c in self.selected:
			if c not in compounds:
				c.hide()
		for c in compounds:
			if c not in self.selected:
				c.show()
		self.selected = compounds
		self.notifySelectionChange(self.selected)

	def setSelectedState(self, state):
		changed = []
		for c in self.selected:
			if c.state != state:
				c.state = state
				changed.append(c)
		if changed:
			self.notifyCompoundChange(changed)

	def showDiagram(self, display, width, height):
		if self.diagramWidth != width or self.diagramHeight != height:
			self.diagramWidth = width
			self.diagramHeight = height
			self.diagramCache = {}
			self.diagramPending = set([])
		if not display and not self.diagramDisplay:
			# Image size changed but since they weren't displayed,
			# it doesn't matter
			return
		if display and self.diagramDisplay:
			# Update images.  This will retry any images
			# that did not make previously.
			self.diagramUpdate()
		else:
			# Display state changed.  Just update the entire table.
			self.diagramDisplay = display
			self._destroyScrolledList()
			self.updateDisplayedCompounds()

	def diagramUpdate(self):
		needDiagramsFor = []
		for row, c in enumerate(self.displayedCompounds):
			try:
				image = self.diagramCache[c]
				self.uiList.item_configure(row, 0, image=image)
			except KeyError:
				needDiagramsFor.append(c)
		if needDiagramsFor:
			wanted = []
			for c in needDiagramsFor:
				if c in self.diagramPending:
					# Already working on it
					continue
				self.diagramPending.add(c)
				wanted.append(c)
			if wanted:
				from chimera.tkgui import runThread
				runThread(self._diagramMake, wanted)

	def _diagramMake(self, q, compounds):
		from StructureDiagram.base import molecule2image
		import traceback
		def status(msg):
			from chimera.replyobj import status
			status("%s\n" % msg)
		def log(msg):
			from chimera.replyobj import message
			message("%s\n" % msg)
		made = 0
		for c in compounds:
			mol = c.chimeraModel
			if not mol:
				continue
			try:
				image = molecule2image(mol, self.diagramWidth,
							self.diagramHeight)
			except:
				msg = ("ViewDock: cannot make diagram for %s."
					"  See Reply Log for details." %
					mol.oslIdent())
				q.put(lambda f=status, msg=msg: status(msg))
				msg = traceback.format_exc()
				q.put(lambda f=log, msg=msg: log(msg))
				q.put(lambda f=self._diagramFailed, c=c: f(c))
			else:
				q.put(lambda f=self._diagramComplete,
						c=c, i=image: f(c, i))
				made += 1
		msg = "ViewDock: made %d of %d diagrams" % (made, len(compounds))
		q.put(lambda s=status, m=msg: s(m))
		q.put(q)

	def _diagramMakeBlank(self):
		from chimera.extension import TextIcon
		if self.diagramBlank:
			if (self.diagramWidth == self.diagramBlank.width
			and self.diagramHeight == self.diagramBlank.height):
				return
		self.diagramBlank = TextIcon(self.uiFrame, "Blank",
					(self.diagramWidth, self.diagramHeight))

	def _diagramFailed(self, c):
		self.diagramPending.remove(c)

	def _diagramComplete(self, c, image):
		from ImageTk import PhotoImage
		w, h = image.size
		if w != self.diagramWidth or h != self.diagramHeight:
			# Must be from an old thread with a different
			# image size.  Just discard the results.
			return
		tkimg = PhotoImage(image)
		self.diagramPending.remove(c)
		self.diagramCache[c] = tkimg
		if not self.diagramDisplay:
			# User can turn off diagram column as we're generating
			# the images.  We'll just save the image in the cache
			# for later use.
			return
		try:
			row = self.displayedCompounds.index(c)
			self.uiList.item_configure(row, 0, image=tkimg)
		except (ValueError, Tkinter.TclError):
			pass

	def hideAll(self):
		for c in self.compoundList:
			c.hide()

	def hideViable(self):
		for c in self.compoundList:
			if c.state == Compound.Viable:
				c.hide()

	def hideDeleted(self):
		for c in self.compoundList:
			if c.state == Compound.Deleted:
				c.hide()

	def hidePurged(self):
		for c in self.compoundList:
			if c.state == Compound.Purged:
				c.hide()

	def displayAll(self):
		for c in self.compoundList:
			c.show()

	def displayViable(self):
		for c in self.compoundList:
			if c.state == Compound.Viable:
				c.show()

	def displayDeleted(self):
		for c in self.compoundList:
			if c.state == Compound.Deleted:
				c.show()

	def displayPurged(self):
		for c in self.compoundList:
			if c.state == Compound.Purged:
				c.show()

	def save(self, filename=None, skipPurged=0):
		if filename == None:
			filename = self.filename
		try:
			os.rename(filename, filename + '.save')
		except os.error:
			pass
		from OpenSave import osOpen
		f = osOpen(filename, 'w')
		for c in self.compoundList:
			if not skipPurged or c.state != Compound.Purged:
				c.save(self.format, f)
		f.close()

	def movieSetup(self):
		self.movieList = []
		first = None
		for c in self.sortedCompoundList:
			if not c.listed:
				continue
			self.movieList.append(c)
			if c.displayed():
				if first:
					c.hide()
				else:
					first = c
		if first is None:
			first = self.movieList[0]
			first.show()
		if len(self.movieList) < 2:
			print 'Not enough compounds displayed in list'
			return 0
		self.uiList.selection_clear()
		self.movieIndex = self.movieList.index(first)
		self.uiList.selection_set(self.movieIndex)
		self.uiList.see(self.movieIndex)
		self.selected = [first]
		self.notifySelectionChange(self.selected)
		return 1

	def movieStep(self):
		prev = self.movieList[self.movieIndex]
		self.uiList.selection_clear()
		self.movieIndex = self.movieIndex + 1
		if self.movieIndex >= len(self.movieList):
			self.movieIndex = 0
		self.uiList.selection_set(self.movieIndex)
		self.uiList.see(self.movieIndex)
		next = self.movieList[self.movieIndex]
		prev.hide()
		next.show()
		self.selected = [next]
		self.notifySelectionChange(self.selected)
		return 1

	def movieStop(self):
		return

	#
	# Mordor format menu callbacks
	#
	def mordorSetMenubar(self, menubar):
		self.mordorMenubar = menubar

	def mordorDefTemplate(self):
		if len(self.selected) != 1:
			replyobj.warning("Please select exactly one compound "
						"as template")
			return
		c = self.selected[0]
		app = self.mordorMenubar.winfo_toplevel().master
		names = self.mordorTemplates.keys()
		v = MordorDefDialog(names).run(app)
		if not v:
			return
		name, forReceptor, forLigand, showHb = v
		c = self.selected[0]
		if forReceptor:
			rTemplate = c.receptorTemplate()
		else:
			rTemplate = None
		if forReceptor:
			lTemplate = c.ligandTemplate()
		else:
			lTemplate = None
		templates = (rTemplate, lTemplate, showHb)
		self.mordorTemplates[name] = templates
		self.mordorActiveTemplates = templates
		self.mordorRemakeMenu()

	def mordorDelTemplate(self):
		app = self.mordorMenubar.winfo_toplevel().master
		names = self.mordorTemplates.keys()
		if not names:
			replyobj.error("No templates have been defined.")
			return
		v = MordorDelDialog(names).run(app)
		if not v:
			return
		for name in v:
			if self.mordorTemplates[name] is self.mordorActiveTemplates:
				self.mordorActiveTemplates = None
			del self.mordorTemplates[name]
		if (self.mordorActiveTemplates is None
		and len(self.mordorTemplates) == 1):
			self.mordorActiveTemplates = self.mordorTemplates.values()[0]
		self.mordorRemakeMenu()

	def mordorRemakeMenu(self):
		mb = self.mordorMenubar
		mb.deletemenu("Mordor")
		mb.addmenu('Mordor', 'Mordor commands')
		mb.addmenuitem('Mordor', 'command',
				label='Define Template',
				command=self.mordorDefTemplate)
		mb.addmenuitem('Mordor', 'command',
				label='Remove Template',
				command=self.mordorDelTemplate)
		names = self.mordorTemplates.keys()
		if not names:
			return
		names.sort()
		mb.addmenuitem("Mordor", "separator")
		for name in names:
			def cb(self=self, name=name):
				self.mordorApplyTemplates(name)
			mb.addmenuitem("Mordor", "command",
					label=name,
					command=cb)

	def mordorApplyTemplates(self, name):
		templates = self.mordorTemplates[name]
		for c in self.selected:
			c.applyTemplates(templates)
		self.mordorActiveTemplates = templates

	def mordorShown(self, compound):
		self.mordorLRU.remove(compound)

	def mordorHidden(self, compound):
		self.mordorLRU.add(compound, self.mordorClose)

	def mordorClose(self, compound):
		compound.closeChimeraModel()

	def mordorCloseCB(self, compound):
		self.mordorLRU.remove(compound)

	#
	# Session methods
	#
	def saveSession(self):
		"Return printable representation of data"
		cList = [ c.saveSession() for c in self.compoundList ]
		return (cList, self._sesIndex(self.displayedCompounds),
				self._sesIndex(self.sortedCompoundList),
				self._sesIndex(self.selected),
				self.columnKeys,
				self.sortColumn,
				self.sortDir)

	def restoreSession(self, data):
		"Convert session string back into data"
		(cList, dcList, scList, sList,
			self.columnKeys, self.sortColumn, self.sortDir) = data
		for cData in cList:
			c = Compound()
			c.restoreSession(cData)
			self.compoundList.append(c)
		self.displayedCompounds = self._sesCompound(dcList)
		self.sortedCompoundList = self._sesCompound(scList)
		self.selected = self._sesCompound(sList)

	def _sesIndex(self, l):
		return [ self.compoundList.index(c) for c in l ]

	def _sesCompound(self, l):
		return [ self.compoundList[i] for i in l ]

class ColumnHeader(Tkinter.Frame):

	def __init__(self, master, title, **kw):
		try:
			self.colCmd = kw["command"]
		except KeyError:
			self.colCmd = None
		else:
			del kw["command"]
		kw["takefocus"] = 1
		Tkinter.Frame.__init__(self, master)
		self.colTitle = Tkinter.Label(self, text=title, **kw)
		self.colTitle.pack(side=Tkinter.LEFT)
		self.colImage = None
		if self.colCmd:
			self.colTitle.bind("<ButtonRelease>", self.colCmd)

	def setTitle(self, title):
		self.colTitle.config(text=title)

	def setImage(self, img):
		if img is None:
			if self.colImage:
				self.colImage.destroy()
				self.colImage = None
		else:
			if self.colImage:
				self.colImage.config(image=img)
			else:
				self.colImage = Tkinter.Label(self, image=img)
				self.colImage.pack(side=Tkinter.RIGHT)
				if self.colCmd:
					self.colImage.bind("<ButtonRelease>",
								self.colCmd)


class ReceptorTemplate:

	def __init__(self, m):
		self.modelAttr = {
			"ballScale": m.ballScale,
			"stickScale": m.stickScale,
			"lineWidth": m.lineWidth,
			"color": m.color,
			"surfaceColor": m.surfaceColor,
		}
		self.residueTemplates = {}
		interBondSet = set([])
		for r in m.residues:
			k, v = self.initResidueTemplate(r, interBondSet)
			self.residueTemplates[k] = v
		self.interBondTemplates = {}
		for b in interBondSet:
			k, v = self.initBondTemplate(b)
			self.interBondTemplates[k] = v

	def initResidueTemplate(self, r, interBondSet):
		import copy
		key = copy.copy(r.id)
		attr = {
			"label": r.label,
			"ribbonDisplay": r.ribbonDisplay,
			"ribbonColor": r.ribbonColor,
			"ribbonDrawMode": r.ribbonDrawMode,
			"ribbonXSection": r.ribbonXSection,
			"ribbonStyle": r.ribbonStyle,
		}
		atoms = {}
		bondSet = set([])
		for a in r.atoms:
			k, v = self.initAtomTemplate(a)
			atoms[k] = v
			for b in a.bonds:
				if b.otherAtom(a).residue is r:
					bondSet.add(b)
				else:
					interBondSet.add(b)
		bonds = {}
		for b in bondSet:
			k, v = self.initBondTemplate(b)
			bonds[k] = v
		return (key, (attr, atoms, bonds))

	def initAtomTemplate(self, a):
		key = (a.name, a.altLoc)
		attr = {
			"color": a.color,
			"drawMode": a.drawMode,
			"display": a.display,
			"radius": a.radius,
			"label": a.label,
			"labelColor": a.labelColor,
			"labelOffset": a.labelOffset,
			"surfaceColor": a.surfaceColor,
			"surfaceDisplay": a.surfaceDisplay,
			"surfaceOpacity": a.surfaceOpacity,
			"vdw": a.vdw,
		}
		return (key, attr)

	def initBondTemplate(self, b):
		a0, a1 = b.atoms
		if a0.residue is a1.residue:
			key = ((a0.name, a0.altLoc), (a1.name, a1.altLoc))
		else:
			import copy
			key = (copy.copy(a0.residue.id), (a0.name, a0.altLoc),
				copy.copy(a1.residue.id), (a1.name, a1.altLoc))
		attr = {
			"color": b.color,
			"drawMode": b.drawMode,
			"display": b.display,
			"radius": b.radius,
			"halfbond": b.halfbond,
			"label": b.label,
			"labelColor": b.labelColor,
			"labelOffset": b.labelOffset,
		}
		return (key, attr)

	def apply(self, m):
		self.displayedSurfaceCategories = set([])
		for a, v in self.modelAttr.iteritems():
			setattr(m, a, v)
		for k, v in self.residueTemplates.iteritems():
			r = m.findResidue(k)
			if r:
				self.applyResidueTemplate(r, v)
		for k, v in self.interBondTemplates.iteritems():
			b = self.findInterBond(m, k)
			if b:
				self.applyBondTemplate(b, v)
		if self.displayedSurfaceCategories:
			import Midas
			models = [ m ]
			for cat in self.displayedSurfaceCategories:
				Midas.surfaceNew(cat, models=models)
		self.displayedSurfaceCategories = None

	def applyResidueTemplate(self, r, v):
		attr, atoms, bonds = v
		for k, v in attr.iteritems():
			setattr(r, k, v)
		for k, v in atoms.iteritems():
			a = r.findAtom(*k)
			if a:
				self.applyAtomTemplate(a, v)
		for k, v in bonds.iteritems():
			k0, k1 = k
			a0 = r.findAtom(*k0)
			if a0 is None:
				continue
			a1 = r.findAtom(*k1)
			if a1 is None:
				continue
			b = a0.findBond(a1)
			if b:
				self.applyBondTemplate(b, v)

	def applyAtomTemplate(self, a, v):
		for k, v in v.iteritems():
			setattr(a, k, v)
		if a.surfaceDisplay:
			self.displayedSurfaceCategories.add(a.surfaceCategory)

	def applyBondTemplate(self, b, v):
		for k, v in v.iteritems():
			setattr(b, k, v)

	def findInterBond(self, m, k):
		r0id, a0id, r1id, a1id = k
		r0 = m.findResidue(r0id)
		if r0 is None:
			return None
		r1 = m.findResidue(r1id)
		if r1 is None:
			return None
		a0 = r0.findAtom(*a0id)
		if a0 is None:
			return None
		a1 = r1.findAtom(*a1id)
		if a1 is None:
			return None
		return a0.findBond(a1)

class LigandTemplate:

	def __init__(self, m):
		self.modelAttr = {
			"ballScale": m.ballScale,
			"stickScale": m.stickScale,
			"lineWidth": m.lineWidth,
			"color": m.color,
			"surfaceColor": m.surfaceColor,
		}

		# Recognize either (1) atoms are all one color
		# or (2) colored by element
		tryColorMap = True
		colorMap = {}
		for a in m.atoms:
			try:
				c = colorMap[a.element]
			except KeyError:
				colorMap[a.element] = a.color
			else:
				if c != a.color:
					tryColorMap = False
					break
		self.atomColor = None
		if tryColorMap:
			import Midas
			colorByElement = True
			for e, c in colorMap.iteritems():
				mc = Midas.elementColor(e)
				if c != mc:
					colorByElement = False
					break
			if colorByElement:
				self.atomColor = "byelement"
			else:
				colors = colorMap.values()
				if len(set(colors)) == 1:
					self.atomColor = colors[0]

		firstAtom = m.atoms[0]
		self.atomDrawMode = firstAtom.drawMode
		self.surfaceColor = firstAtom.surfaceColor
		self.surfaceDisplay = firstAtom.surfaceDisplay
		self.surfaceOpacity = firstAtom.surfaceOpacity
		for a in m.atoms:
			if self.atomDrawMode != a.drawMode:
				self.atomDrawMode = None
			if self.surfaceColor != a.surfaceColor:
				self.surfaceColor = None
			if self.surfaceDisplay != a.surfaceDisplay:
				self.surfaceDisplay = None
			if self.surfaceOpacity != a.surfaceOpacity:
				self.surfaceOpacity = None

		self.bondDrawMode = m.bonds[0].drawMode
		for b in m.bonds:
			if self.bondDrawMode != b.drawMode:
				self.bondDrawMode = None
				break

		self.halfbond = m.bonds[0].halfbond
		for b in m.bonds:
			if self.halfbond != b.halfbond:
				self.halfbond = None
				break

	def apply(self, m):
		for a, v in self.modelAttr.iteritems():
			setattr(m, a, v)
		if self.atomColor == "byelement":
			import Midas
			sel = chimera.selection.ItemizedSelection()
			sel.add(m.atoms)
			Midas.color(self.atomColor, sel)
		elif self.atomColor is not None:
			for a in m.atoms:
				a.color = self.atomColor
		if self.atomDrawMode is not None:
			for a in m.atoms:
				a.drawMode = self.atomDrawMode
		if self.surfaceColor is not None:
			for a in m.atoms:
				a.surfaceColor = self.surfaceColor
		if self.surfaceDisplay is not None:
			for a in m.atoms:
				a.surfaceDisplay = self.surfaceDisplay
		if self.surfaceOpacity is not None:
			for a in m.atoms:
				a.surfaceOpacity = self.surfaceOpacity
		if self.bondDrawMode is not None:
			for b in m.bonds:
				b.drawMode = self.bondDrawMode
		if self.halfbond is not None:
			for b in m.bonds:
				a.halfbond = self.halfbond
		if self.surfaceDisplay:
			import Midas
			Midas.surfaceNew("ligand", models=[ m ])

class LRU:
	"Least Recently Used cache."
	def __init__(self, threshold):
		self.items = {}
		self.threshold = threshold
		self.nextId = 1

	def add(self, item, dispose):
		self.items[item] = self.nextId
		self.nextId += 1
		if len(self.items) <= self.threshold:
			return
		itemList = [ (t, v) for v, t in self.items.iteritems() ]
		itemList.sort()
		nDiscard = len(itemList) - self.threshold
		for t, v in itemList[:nDiscard]:
			del self.items[v]
			dispose(v)
		nextId = 1
		for t, v in itemList[nDiscard:]:
			self.items[v] = nextId
			nextId += 1
		self.nextId = nextId

	def remove(self, item):
		try:
			del self.items[item]
		except KeyError:
			pass

class MordorDefDialog(ModalDialog):
	"""Dialog for getting new Mordor template name"""

	title = "Define Mordor Template"
	buttons = ("OK", "Cancel")

	def __init__(self, names, *args, **kw):
		self.names = names
		ModalDialog.__init__(self, *args, **kw)

	def fillInUI(self, master):
		f = Tkinter.Frame(master)
		f.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
		self.nameWidget = Pmw.EntryField(f, labelpos="w",
						label_text="Name:",
						command=self.OK)
		self.nameWidget.pack(fill=Tkinter.X, expand=Tkinter.TRUE)
		self.targetWidget = Pmw.RadioSelect(f, buttontype="checkbutton")
		self.targetWidget.pack(fill=Tkinter.X, expand=Tkinter.TRUE)
		self.targetWidget.add("Receptor")
		self.targetWidget.add("Ligand")
		self.targetWidget.invoke("Receptor")
		self.targetWidget.invoke("Ligand")
		self.hbWidget = Pmw.OptionMenu(f, labelpos="w",
					label_text="Show hydrogen bonds:",
					items = ("none", "all",
						"ligand-receptor"),
					menubutton_width=15)
		self.hbWidget.pack(fill=Tkinter.X, expand=Tkinter.TRUE)

	def OK(self):
		targetValue = self.targetWidget.getvalue()
		if not targetValue:
			self.Cancel(value=None)
			replyobj.error("You must select either Ligand, "
					"Receptor, or both")
			return
		name = self.nameWidget.getvalue().strip()
		if not name:
			self.Cancel(value=None)
			replyobj.error("You must provide a template name")
			return
		if name in self.names:
			self.Cancel(value=None)
			replyobj.error("Template %s is already defined" % name)
			return
		showHb = self.hbWidget.getvalue()
		self.Cancel(value=(name, "Receptor" in targetValue,
					"Ligand" in targetValue,
					showHb))

class MordorDelDialog(ModalDialog):
	"""Dialog for getting Mordor template names to remove"""

	title = "Remove Mordor Template"
	buttons = ("OK", "Cancel")

	def __init__(self, names, *args, **kw):
		self.names = names
		self.names.sort()
		ModalDialog.__init__(self, *args, **kw)

	def fillInUI(self, master):
		self.listWidget = Pmw.ScrolledListBox(master,
					items=self.names,
					labelpos="nw",
					label_text="Remove templates",
					listbox_height=5)
		self.listWidget.pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)

	def OK(self):
		selected = self.listWidget.getvalue()
		if not selected:
			self.Cancel(value=None)
			replyobj.error("No template selected for removal")
			return
		self.Cancel(value=selected)
