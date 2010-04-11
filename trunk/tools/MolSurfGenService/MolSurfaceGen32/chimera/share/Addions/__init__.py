from chimera import replyobj

ValidIontypes = ("Cl-", "Cs+", "K+",  "Li+", "MG2", "Na+", "Rb+" )

def writeLeaprc(tempDir, iontype, numion, leaprc ) :
	import os
	f = open( leaprc, 'w' )

	f.write( "source leaprc.ff03\n" )
	f.write( "tmp = loadmol2 " + os.path.join(tempDir, "sleap.in.mol2\n") )
      
        if numion=="neutralize":
	    f.write( "addions tmp " + iontype + " 0\n" )
        else:
            f.write( "addions tmp " + iontype + " " + numion + "\n" )

	f.write( "savemol2 tmp " + os.path.join(tempDir, "sleap.out.mol2\n") )
	f.write( "quit\n" )

def is_solvent(r):
    for a in r.atoms:
        for n in a.neighbors:
            if n.residue !=r:
                return False

    return True

def get_solute_nresd(m):

    i=len(m.residues)-1

    while i>=0 and is_solvent(m.residues[i]):
        i -= 1

    return i+1
    


def initiateAddions(models, iontype, numion, status):
    import os
    import chimera
    from chimera import replyobj
    from chimera.molEdit import addAtom
    from WriteMol2 import writeMol2
    from tempfile import mkdtemp

    for m in models:
	tempDir = mkdtemp()

	def _clean():
		for fn in os.listdir(tempDir):
			os.unlink(os.path.join(tempDir, fn))
		os.rmdir(tempDir)

	sleapIn = os.path.join(tempDir, "sleap.in.mol2")
	sleapOut= os.path.join(tempDir, "sleap.out.mol2")
	writeMol2([m], sleapIn, status=status, gaffType=True)

	leaprc = os.path.join(tempDir, "solvate.cmd")
	writeLeaprc(tempDir, iontype, numion, leaprc)

	chimeraRoot = os.environ["CHIMERA"]
        amberHome = os.path.join(chimeraRoot, "bin", "amber10")
	command = [os.path.join(amberHome, "exe", "sleap"), "-f", leaprc]

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
		replyobj.status("(addions) %s" % line, log=True)
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
	solute_nresd = get_solute_nresd(m)
        print "total, solute, solvent: ", len(m.residues), solute_nresd, len(m.residues)-solute_nresd

        if status:
            status( "Deleting old solvents" )
        while len(m.residues) > solute_nresd:
            m.deleteResidue( m.residues[solute_nresd] )


	inAtoms = m.atoms
	outAtoms = outm.atoms
	# sort in coordIndex (i.e. input) order
	# (due to deletions, coordIndex values need _not_ be consecutive)
	serialSort = lambda a1, a2: cmp(a1.coordIndex, a2.coordIndex)
	inAtoms.sort(serialSort)
	outAtoms.sort(serialSort)

	# sleap repositions solute...
	if status:
		status("Translating %d atoms" % len(inAtoms))
	for inA, outA in zip(inAtoms, outAtoms[:len(inAtoms)]):
		inA.setCoord(outA.coord())

	for r in outm.residues[solute_nresd:]:
		if status:
			status("Creating ions/solvent residue %d " % (r.id.position-solute_nresd) )

		atomMap = {}
		nr = m.newResidue(r.type, ' ', 1, ' ')
		for a in r.atoms:
			na = addAtom(a.name, a.element, nr, a.coord(),
						serialNumber=a.serialNumber)
			na.charge = a.charge
			na.gaffType = a.mol2type

			if len(a.neighbors)==0:
				na.drawMode = chimera.Atom.Sphere

			atomMap[a] = na

			if a.name[0:2]=="Br": na.element = 35
			elif a.name[0:2]=="Cl": na.element = 17
			elif a.name[0:2]=="Cs": na.element = 47
			elif a.name[0:2]=="Mg": na.element = 12
			elif a.name[0:2]=="Na": na.element = 11
			elif a.name[0:2]=="Rb": na.element = 48
			elif a.name[0]=='F': na.element = 9
			elif a.name[0]=='I': na.element = 53
			elif a.name[0]=='K': na.element = 19
			elif a.name[0]=="H": na.element = 1
			elif a.name[0]=="C": na.element = 6
			elif a.name[0]=="N": na.element = 7
			elif a.name[0]=="O": na.element = 8
			elif a.name[0]=="P": na.element = 15
			elif a.name[0]=="S": na.element = 16

		for a in r.atoms:
			na = atomMap[a]
			for n in a.neighbors:
				assert n.residue == r
				nn = atomMap[n]
				if nn in na.bondsMap:
					continue
				m.newBond(na, nn)
	_clean()

def test():
	import chimera
	models = chimera.openModels.list()
	iontype = "Cl-"
	numion = "4"
	status = chimera.replyobj.status
	initiateAddions(models, method, solvent, extent, center, status)
