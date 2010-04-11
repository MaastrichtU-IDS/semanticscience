from chimera import replyobj

ValidSolventShapes = ("cap", "box", "oct", "shell" )

ValidSolventModels = ("CHCL3BOX", "MEOHBOX", "NMABOX", "POL3BOX",
	"QSPCFWBOX", "SPCBOX", "SPCFWBOX",  "TIP3PBOX",
	"TIP3PFBOX", "TIP4PBOX", "TIP4PEWBOX")

def writeLeaprc(tempDir, method, solvent, extent, center, leaprc) :
	import os
	f = open( leaprc, 'w' )

	f.write( "source leaprc.ff03\n" )
	f.write( "tmp = loadmol2 " + os.path.join(tempDir, "sleap.in.mol2\n") )

	if method=="cap" or method=="Cap":
		f.write( "solvatecap tmp " + solvent + " tmp." + center + " "  + extent + "\n" )
	else:
		f.write( "solvate" + method + " tmp " + solvent + " " + extent + "\n" )

	f.write( "savemol2 tmp " + os.path.join(tempDir, "sleap.out.mol2\n") )
	f.write( "quit\n" )




def initiateSolvate(models, method, solvent, extent, center, status):
    import os
    import chimera
    from chimera import replyobj
    from chimera.molEdit import addAtom
    from WriteMol2 import writeMol2
    from tempfile import mkdtemp

    for m in models:
	tempDir = mkdtemp()
	print 'tempDir: ', tempDir

	def _clean():
		for fn in os.listdir(tempDir):
			os.unlink(os.path.join(tempDir, fn))
		os.rmdir(tempDir)

	sleapIn = os.path.join(tempDir, "sleap.in.mol2")
	sleapOut= os.path.join(tempDir, "sleap.out.mol2")
	writeMol2([m], sleapIn, status=status)

	leaprc = os.path.join(tempDir, "solvate.cmd")
	writeLeaprc(tempDir, method, solvent, extent, center, leaprc)

	chimeraRoot = os.environ["CHIMERA"]
        amberHome = os.path.join(chimeraRoot, "bin", "amber10")
	command = [os.path.join(amberHome, "exe", "sleap"), "-f", leaprc]

	print 'command: ', command
	if status:
		status("Running sleap" )
	from subprocess import Popen, STDOUT, PIPE
	# For some reason on Windows, if shell==False then antechamber
	# cannot run bondtype via system().
	import sys
	if sys.platform == "win32":
		shell = True
	else:
		shell = False
	replyobj.info("Running sleap command: %s\n" % " ".join(command))
	import os
	os.environ["AMBERHOME"]=amberHome
	sleapMessages = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
			cwd=tempDir, shell=shell, bufsize=1).stdout
	while True:
		line = sleapMessages.readline()
		if not line:
			break
		replyobj.status("(solvate) %s" % line, log=True)
	if not os.path.exists(sleapOut):
		_clean()
		from chimera import NonChimeraError
		raise NonChimeraError("Failure running sleap \n"
			"Check reply log for details\n")
	if status:
		status("Reading sleap output\n")
	from chimera import Mol2io, defaultMol2ioHelper
	mol2io = Mol2io(defaultMol2ioHelper)
	mols = mol2io.readMol2file(sleapOut)
	if not mol2io.ok():
		_clean()
		raise IOError(mol2io.error())
	if not mols:
		_clean()
		raise RuntimeError("No molecules in sleap output")

        assert len(mols)==1

	outm = mols[0]
	natom = len(m.atoms)
	nresd = len(m.residues)
	inAtoms = m.atoms
	outAtoms = outm.atoms
	# sort in coordIndex (i.e. input) order
	# (due to deletions, coordIndex values need _not_ be consecutive)
	serialSort = lambda a1, a2: cmp(a1.coordIndex, a2.coordIndex)
	inAtoms.sort(serialSort)
	outAtoms.sort(serialSort)

	if status:
		status("Translating %d atoms" % len(inAtoms))
	for inA, outA in zip(inAtoms, outAtoms[:len(inAtoms)]):
		inA.setCoord(outA.coord())
	
	# added solvent hydrogens may not have been categorized yet, so use
	# this less obvious way of gathering solvent atoms...
	existingSolvent = set()
	from chimera.elements import metals, alkaliMetals
	nonAlkaliMetals = metals - alkaliMetals
	for r in m.residues:
		if len(r.atoms) == 1 and r.atoms[0].element in nonAlkaliMetals:
			continue
		for a in r.atoms:
			if a.surfaceCategory in ["solvent", "ions"]:
				existingSolvent.update(r.atoms)
				break

	# copy mol2 comment which contain the info of the solvent: shape, size, etc
        if hasattr( outm, "mol2comments" ) and len(outm.mol2comments) > 0:
		m.solventInfo = outm.mol2comments[0]
		print "solvent info: ", m.solventInfo


	if existingSolvent:
		solventCharges = {}
	for r in outm.residues[nresd:]:
		solventNum = r.id.position - nresd
		if status:
			status("Creating solvent residue %d " % solventNum )

		atomMap = {}
		nr = m.newResidue(r.type, ' ', solventNum, ' ')
		# mark residue for exclusion by AddCharge...
		nr._solvateCharged = True
		for a in r.atoms:
			na = addAtom(a.name, a.element, nr, a.coord(),
						serialNumber=a.serialNumber)
			na.charge = a.charge
			na.gaffType = a.mol2type
			atomMap[a] = na
			if a.name[0]=="H": na.element = 1
			if a.name[0]=="C": na.element = 6
			if a.name[0]=="N": na.element = 7
			if a.name[0]=="O": na.element = 8
			if a.name[0]=="P": na.element = 15
			if a.name[0]=="S": na.element = 16
			if a.name[0:2]=="Cl": na.element = 17
			if existingSolvent:
				solventCharges[(r.type, a.name)] = a.charge
				if r.type == "WAT":
					solventCharges[
						("HOH", a.name)] = a.charge


		for a in r.atoms:
			na = atomMap[a]
			for n in a.neighbors:
				assert n.residue == r
				nn = atomMap[n]
				if nn in na.bondsMap:
					continue
				m.newBond(na, nn)
	
	if existingSolvent:
		unknowns = set()
		for sa in existingSolvent:
			key = (sa.residue.type, sa.name)
			try:
				sa.charge = solventCharges[key]
			except KeyError:
				unknowns.add(key)
			sa.residue._solvateCharged = True
		if unknowns:
			replyobj.warning("Could not determine charges for"
				" pre-existing solvent/ions from added solvent"
				"/ions for: " + ", ".join([" ".join(x)
				for x in unknowns]))
	_clean()
				
    from Midas import window
    window(models)

def test():
	import chimera
	models = chimera.openModels.list()
	method = "Box"
	solvent = "POL3BOX"
	extent = "4"
	center = ""
	status = chimera.replyobj.status
	initiateSolvate(models, method, solvent, extent, center, status)
