# This module invokes the server at
#	http://molbio.info.nih.gov/structbio/basic.html
# to compute some atomic quantities.

import chimera
import re

def msms(target, opts, propName, rba):
	aList = _target2atoms(target)
	lines, idMap = _atoms2PDB(aList)
	output = _invoke("msms", opts, lines)
	if chimera.debug:
		print output
	m = re.match(".*MSMS terminated normally.*sas_0\\s*\\n(.*)<P><hr>",
			output, re.M | re.S | re.I)
	if not m:
		raise chimera.NotABug(
			"unexpected output from StrucTools server")
	lines = m.group(1).rstrip().split('\n')
	if len(lines) > len(aList):
		raise chimera.NotABug(
			"expected %d lines from StrucTools server and got %d"
			% (len(aList), len(lines)))
	eProp = propName + "_MS"
	aProp = propName + "_SAS"
	totalExposed = 0.0
	totalAccessible = 0.0
	assigned = set([])
	unused = 0
	for line in lines:
		values = _msmsValues(line)
		try:
			a = _msmsAtom(idMap, values)
		except KeyError:
			if chimera.debug:
				print "unused", values
			unused += 1
		else:
			if a not in assigned:
				setattr(a, eProp, values[-2])
				totalExposed += values[-2]
				setattr(a, aProp, values[-1])
				totalAccessible += values[-1]
				assigned.add(a)
	unmatched = len(aList) - len(assigned)
	_printMismatch(aList, assigned)
	_reportWarning(unmatched, unused)
	msg = "Total area assigned: MS=%.2f SAS=%.2f.  " % (totalExposed,
							totalAccessible)
	_reportStatus(msg, assigned, [aProp, eProp], _modelList(aList), rba)
	return output

def _msmsValues(line):
	aNum, exposed, accessible, aSpec = line.split()
	aNum = int(aNum)
	exposed = float(exposed)
	accessible = float(accessible)
	aName, rType, chainId, rSeq = aSpec.split('_')
	if rSeq[-1].isdigit():
		insertCode = ' '
		rSeq = int(rSeq)
	else:
		insertCode = rSeq[-1]
		rSeq = int(rSeq[:-1])
	return aName, rType, chainId, rSeq, insertCode, exposed, accessible

def _msmsAtom(idMap, values):
	aName, rType, chainId, rSeq, insertCode, exposed, accessible = values
	return idMap[(aName, rType, chainId, rSeq, insertCode)]

def surface(target, opts, propName, rba):
	return gerstein(target, propName, rba, "surf_Gerstein", opts,
			_gersteinSurface)

def volume(target, opts, propName, rba):
	return gerstein(target, propName, rba, "vol_Gerstein", opts,
			_gersteinVolume)

def gerstein(target, propName, rba, service, opts, parser):
	aList = _target2atoms(target)
	lines, idMap = _atoms2PDB(aList)
	output = _invoke(service, opts, lines)
	if chimera.debug:
		print output
	m = re.match(""".*<pre>\n[^\n]*\n(.*)\n<P><hr>""", output, re.M | re.S)
	if not m:
		raise chimera.NotABug(
				"unexpected output from StrucTools server")
	lines = m.group(1).rstrip().split('\n')
	if len(lines) > len(aList):
		raise chimera.NotABug(
			"expected %d lines from StrucTools server and got %d"
			% (len(aList), len(lines)))
	total = 0.0
	assigned = set([])
	unused = 0
	for line in lines:
		values = parser(line)
		try:
			a = _gersteinAtom(idMap, values)
		except KeyError:
			if chimera.debug:
				print "unused", values
			unused += 1
		else:
			if a not in assigned:
				v = values[-1]
				setattr(a, propName, v)
				if v is not None:
					total += v
				assigned.add(a)
	unmatched = len(aList) - len(assigned)
	_printMismatch(aList, assigned)
	_reportWarning(unmatched, unused)
	if service.startswith("surf"):
		msg = "Total area assigned: %.2f.  " % total
	else:
		msg = "Total volume assigned: %.2f.  " % total
	_reportStatus(msg, assigned, [propName], _modelList(aList), rba)
	return output

def _gersteinVolume(line):
	aName = line[12:16].strip()
	rType = line[17:20].strip()
	chainId = line[21]
	rSeq = int(line[22:26])
	insertCode = line[26]
	value = float(line[73:79])
	if value < 0:
		value = None
	return aName, rType, chainId, rSeq, insertCode, value

def _gersteinSurface(line):
	aName = line[12:16].strip()
	rType = line[17:20].strip()
	chainId = line[21]
	rSeq = int(line[22:26])
	insertCode = line[26]
	value = float(line[67:73])
	return aName, rType, chainId, rSeq, insertCode, value

def _gersteinAtom(idMap, values):
	aName, rType, chainId, rSeq, insertCode, value = values
	try:
		return idMap[(aName, rType, chainId, rSeq, insertCode)]
	except KeyError:
		return idMap[(aName, rType, chainId.upper(), rSeq, insertCode)]

def _target2atoms(target):
	rList = []
	for t in target:
		# Target can be either a molecule or a chain.
		r = t.residues
		if callable(r):
			r = r()
		rList += r
	aList = []
	for r in rList:
		aList.extend(r.atoms)
	return aList

def _atoms2PDB(aList):
	idMap = {}
	pList = []
	for n, a in enumerate(aList):
		r = a.residue
		if r.isHet:
			recType = "HETATM"
		else:
			recType = "ATOM  "
		rid = r.id
		c = a.xformCoord()
		try:
			occupancy = a.occupancy
		except AttributeError:
			occupancy = 1.0
		try:
			bfactor = a.bfactor
		except AttributeError:
			bfactor = 0.0
		aName = _pdbAtomName(a)
		idMap[(aName.strip(), r.type.strip(), rid.chainId[0],
				rid.position, rid.insertionCode[0])] = a
		pdb = ("%6s%5d %4s%1s%3s %1.1s%4d%1s   "
			"%8.3f%8.3f%8.3f%6.2f%6.2f\n"
			% (recType, n + 1, aName, a.altLoc, r.type,
				rid.chainId, rid.position, rid.insertionCode,
				c.x, c.y, c.z, occupancy, bfactor))
		pList.append(pdb)
	lines = ''.join(pList)
	if chimera.debug:
		import pprint
		print lines
		pprint.pprint(idMap)
	return lines, idMap

def _pdbAtomName(a):
	# this routine is a straight translation from PDBio component
	aname = a.name.replace("'", "*")
	if len(a.element.name) > 1:
		return "%-4s" % aname
	else:
		if a.element.name[0] == aname[0]:
			# nothing funny in front
			if len(aname) == 4:
				# need to swap last character into front
				return aname[3:4] + aname[0:3]
			else:
				return " %-3s" % aname
		else:
			return "%-4s" % aname

def _invoke(service, opts, pdb):
	import multipart
	try:
		return multipart.post_multipart(
				"helixweb.nih.gov",
				"/cgi-bin/structbio/basic",
				opts + [
				  ( "pdb_file", "chimera", pdb ),
				  ( "what", None, service ),
				  ( "outputtype", None, "Raw" ),
				]
				)
	except:
		raise chimera.NonChimeraError("Error contacting "
				"StrucTools web server")

def _modelList(aList):
	mDict = {}
	for a in aList:
		mDict[a.molecule] = True
	return mDict.keys()

def _printMismatch(aList, assigned):
	print "Unmatched atoms"
	for a in aList:
		if a in assigned:
			continue
		print " ", a.oslIdent()

def _reportWarning(unmatched, unused):
	if unmatched > 0 or unused > 0:
		if unmatched > 0:
			if unmatched == 1:
				phrase = "One atom was"
				verb = "does"
			else:
				phrase = "%d atoms were" % unmatched
				verb = "do"
			msg1 = ("%s missing from output and %s not "
				"have new attributes.\n" % (phrase, verb))
		else:
			msg1 = ""
		if unused > 0:
			if unused == 1:
				phrase = "One line"
				verb = "was"
			else:
				phrase = "%d lines" % unused
				verb = "were"
			msg2 = "%s of output %s unused.\n" % (phrase, verb)
		else:
			msg2 = ""
		if msg1 and msg2:
			warning = msg1 + msg2
		elif msg1:
			warning = msg1
		else:
			warning = msg2
		chimera.replyobj.warning(warning)

def _reportStatus(msg, assigned, propList, modelList, rba):
	if len(assigned) == 1:
		phrase = "one atom"
	else:
		phrase = "%d atoms" % len(assigned)
	pList = [ repr(p) for p in propList ]
	if len(pList) == 1:
		s = pList[0]
		plural = ""
		verb = "was"
	else:
		s = ", ".join(pList[:-1]) + " and " + pList[-1]
		plural = "s"
		verb = "were"
	msg += ("Attribute%s %s %s created for %s.\n"
		% (plural, s, verb, phrase))
	chimera.replyobj.status(msg)
	chimera.replyobj.message(msg)
	if rba and assigned:
		try:
			from ShowAttr import ShowAttrDialog
		except ImportError:
			# No "render by attribute", just ignore
			pass
		else:
			from chimera import dialogs
			d = dialogs.display(ShowAttrDialog.name)
			d.configure(models=modelList, attrsOf="atoms",
					attrName=None)
			d.refreshAttrs()
			d.configure(models=modelList, attrsOf="atoms",
					attrName=propList[0])
